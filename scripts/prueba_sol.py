"""Primera prueba con el equipo: medir los patrones SOL y aplicar la corrección por software.

Uso:
    .venv/bin/python scripts/prueba_sol.py                  # con el NanoVNA conectado
    .venv/bin/python scripts/prueba_sol.py --simulado       # sin equipo, para probar el flujo

Mide cada patrón (abierto, corto, carga) varias veces en el plano donde irá la sonda, guarda
todos los barridos en data/raw/prueba_sol/ y calcula los términos de error con lcds.sol.

La comprobación es dejar una repetición fuera: los términos se calculan con las demás y se
aplican a la que no se usó. Tras corregir, cada patrón debe caer en su valor ideal; el residuo
que queda mide la repetibilidad de la conexión y del equipo, no la exactitud del kit.

Reparto: pynanovna habla con el equipo y lcds.sol hace el cálculo de la SOL (rfmeasurement no
trae calibración). rfmeasurement pone el resto: cada barrido en bruto y cada red corregida es un
Measurement con su contexto, pasa por su motor de validación y queda enlazado por registros de
trazabilidad desde el resultado hasta los .s1p de partida. Su motor de incertidumbre propaga la
repetibilidad de los tres patrones y de la medida hasta el Gamma corregido, de modo que el
residuo se compara con su incertidumbre: si la repetibilidad lo explica todo, cerca del 95 % de
los puntos debe quedar dentro de la incertidumbre expandida.
"""

import argparse
import tempfile
from dataclasses import replace
from datetime import datetime, timezone

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from scipy import stats

from rfmeasurement.provenance import ProvenanceGraph
from rfmeasurement.uncertainty import expand, propagate_linear
from rfmeasurement.validation import validate

from lcds.acquisition import F_STOP_HZ, REGLAS, SEGMENTOS, calibracion_firmware, conectar, desconectar, medir
from lcds.metadata import Medida
from lcds.paths import FIGURAS, PROCESSED, RAW
from lcds.provenance import guardar_registros, registrar
from lcds.sol import PATRONES_IDEALES, corregir, promediar, terminos_error
from lcds.uncertainty import evaluar, modelo_sol

PATRONES = ("abierto", "corto", "carga")
IDEAL = dict(zip(PATRONES, PATRONES_IDEALES))
COLOR = {"abierto": "#2a78d6", "corto": "#eb6834", "carga": "#1baf7a"}
COBERTURA = 0.95
TINTA, TINTA_2, REJILLA, FONDO = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


class VNASimulado:
    """Equipo ficticio con una red de error fija y ruido, para ensayar el flujo sin hardware."""

    def __init__(self):
        self.rng = np.random.default_rng(1)
        self.gamma = 1 + 0j

    def set_sweep(self, inicio, fin, puntos):
        self.f = np.linspace(inicio, fin, puntos)

    def sweep(self):
        ed, es = 0.05 - 0.02j, 0.1 + 0.07j
        er = 0.8 * np.exp(-2j * np.pi * self.f * 0.4e-9)
        ruido = self.rng.normal(0, 2e-4, self.f.size) + 1j * self.rng.normal(0, 2e-4, self.f.size)
        return list((ed + er * self.gamma) / (1 - es * self.gamma) + ruido), [0j] * self.f.size, list(self.f)

    def info(self):
        return {"Serial Number": "simulado", "Version": "simulado"}


def db(x):
    return 20 * np.log10(np.maximum(np.abs(x), 1e-7))


def segmentos_hasta(f_max):
    return tuple((a, min(b, f_max)) for a, b in SEGMENTOS if a < f_max)


def figura(f, residuo, u, ruta, titulo):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": REJILLA, "text.color": TINTA,
                         "axes.labelcolor": TINTA_2, "xtick.color": TINTA_2, "ytick.color": TINTA_2})
    fig, ejes = plt.subplots(2, 1, figsize=(8, 6.4), sharex=True, sharey=True, facecolor=FONDO)
    paneles = (
        (residuo, "Residuo tras corregir la repetición no usada, |Γ − Γ ideal| (dB)"),
        (u, "Incertidumbre expandida (95 %) del Γ corregido, propagada con rfmeasurement (dB)"),
    )
    for eje, (datos, rotulo) in zip(ejes, paneles):
        eje.set_facecolor(FONDO)
        for patron in PATRONES:
            eje.semilogx(f, db(datos[patron]), color=COLOR[patron], lw=1.1, label=patron)
        eje.set_title(rotulo, loc="left", fontsize=9, color=TINTA)
        eje.grid(True, which="major", color=REJILLA, lw=0.6)
        eje.spines[["top", "right"]].set_visible(False)
        eje.margins(x=0.02)
        eje.legend(frameon=False, ncols=3, loc="lower left", fontsize=8)
    ejes[1].set_xlabel("Frecuencia (Hz)")
    fig.suptitle(titulo, x=0.02, ha="left", fontsize=10, color=TINTA)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(ruta, dpi=150, facecolor=FONDO)
    plt.close(fig)


def incertidumbre_corregida(patrones, u_patrones, medida, u_medida):
    """Incertidumbre expandida de Re e Im del Gamma corregido a cada frecuencia (propagación lineal)."""
    expandida = np.empty(medida.size, dtype=complex)
    for i in range(medida.size):
        gammas = {p: patrones[p][i] for p in PATRONES} | {"medida": medida[i]}
        u = {p: u_patrones[p][i] for p in PATRONES} | {"medida": u_medida[i]}
        partes = []
        for parte in ("re", "im"):
            lineal = propagate_linear(modelo_sol(gammas, u, parte=parte))
            partes.append(expand(lineal.value, lineal.standard_uncertainty, COBERTURA)[0])
        expandida[i] = complex(*partes)
    return expandida


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repeticiones", type=int, default=5)
    ap.add_argument("--fmax", type=float, default=F_STOP_HZ, help="frecuencia máxima en Hz")
    ap.add_argument("--puerto", default=None)
    ap.add_argument("--simulado", action="store_true")
    args = ap.parse_args()
    if args.repeticiones < 3:
        ap.error("hacen falta al menos 3 repeticiones para dejar una fuera")

    cal_id = "sol_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    campana = "prueba_sol"
    # En simulado nada se escribe en el repositorio: data/raw es solo para medidas reales
    temporal = Path(tempfile.mkdtemp(prefix="prueba_sol_")) if args.simulado else None
    raw, processed, figuras = (temporal / "raw", temporal / "processed", temporal) if temporal else (RAW, PROCESSED, FIGURAS)
    segmentos = segmentos_hasta(args.fmax)
    vna = VNASimulado() if args.simulado else conectar(args.puerto)
    trazas, registros, ultima = {}, [], {}
    try:
        if not args.simulado:
            info = vna.info()
            print(f"Equipo: {info['Comment']}, firmware {info['Version']}")
            print(f"Calibración del firmware: {calibracion_firmware(vna)}")
        print(f"Tramos: {len(segmentos)} hasta {args.fmax / 1e6:g} MHz; {args.repeticiones} repeticiones por patrón\n")

        for patron in PATRONES:
            if args.simulado:
                vna.gamma = IDEAL[patron]
            else:
                input(f"Conecta el patrón «{patron}» y pulsa Intro… ")
            trazas[patron] = []
            for i in range(1, args.repeticiones + 1):
                medida = Medida(campana=campana, muestra=f"sol_{patron}", repeticion=i, cal_sol_id=cal_id)
                ruta, medicion = medir(vna, medida, segmentos=segmentos, raiz=raw)
                trazas[patron].append(medicion.data.s[:, 0, 0])
                registros.append(medicion.provenance[0])
                pasiva = {r.rule_id: r.status.value for r in medicion.validation.results}["physics.passivity"]
                print(f"  {patron} r{i:02d}: {ruta.name}  (pasividad: {pasiva})")
            ultima[patron] = medicion  # la repetición que se deja fuera en la comprobación
            dispersion = np.median(np.abs(np.array(trazas[patron]) - np.mean(trazas[patron], axis=0)), axis=1).max()
            if dispersion > 0.05:
                print(f"  AVISO: las repeticiones de «{patron}» no coinciden entre sí (desviación de {dispersion:.2f}).\n"
                      "  ¿Se conectó o se movió el patrón durante la medida? Conviene repetir la tanda.")
            f = medicion.data.f
    finally:
        if not args.simulado:
            desconectar(vna)

    # Términos de error con todas las repeticiones, para usarlos después
    medias = {p: promediar(trazas[p]) for p in PATRONES}
    ed, er, es = terminos_error(*(medias[p][0] for p in PATRONES))
    carpeta = processed / campana
    carpeta.mkdir(parents=True, exist_ok=True)
    np.savez(carpeta / f"{cal_id}_terminos.npz", f_hz=f, ed=ed, er=er, es=es,
             **{f"u_{p}": medias[p][1] for p in PATRONES})
    calculo = registrar("calcular_terminos_sol", entradas=[r.record_id for r in registros],
                        parametros={"cal_sol_id": cal_id, "patrones": "ideales", "repeticiones": args.repeticiones})
    guardar_registros([calculo], carpeta / f"{cal_id}_terminos.procedencia.json")

    # Comprobación dejando fuera la última repetición de cada patrón
    parciales = terminos_error(*(promediar(trazas[p][:-1])[0] for p in PATRONES))
    usados = [r.record_id for r in registros if r not in [m.provenance[0] for m in ultima.values()]]
    calculo_parcial = registrar("calcular_terminos_sol", entradas=usados,
                                parametros={"cal_sol_id": cal_id, "patrones": "ideales", "uso": "comprobación"})
    residuo, cadena = {}, [calculo_parcial]
    print("\nValidación de las redes corregidas (rfmeasurement):")
    for p in PATRONES:
        bruta = ultima[p]
        red = bruta.data.copy()
        red.s[:, 0, 0] = corregir(trazas[p][-1], *parciales)
        correccion = registrar("corregir_sol", entradas=(bruta.provenance[0].record_id, calculo_parcial.record_id),
                               parametros={"cal_sol_id": cal_id})
        corregida = replace(
            bruta, data=red,
            context=replace(bruta.context, calibration=f"SOL por software ({cal_id}) sobre la del firmware"),
            provenance=[bruta.provenance[0], calculo_parcial, correccion],
        )
        corregida.validation = validate(corregida, rules=REGLAS)
        estados = ", ".join(f"{r.rule_id.split('.')[1]}={r.status.value}" for r in corregida.validation.results
                            if r.status.value not in ("pass", "not_applicable")) or "todas las reglas pasan"
        grafo = ProvenanceGraph.from_measurement(corregida)
        print(f"  {p:8s} {estados}  ·  procede de {len(grafo.external_sources) + len(grafo.ancestors(correccion.record_id))} registros")
        residuo[p] = red.s[:, 0, 0] - IDEAL[p]
        cadena.append(correccion)
    guardar_registros(cadena, carpeta / f"{cal_id}_comprobacion.procedencia.json")

    # Incertidumbre del Gamma corregido con el motor de rfmeasurement. Fuentes: la media de cada
    # patrón (desviación típica de la media) y la medida suelta (desviación típica de un barrido).
    n = args.repeticiones - 1
    usadas = {p: promediar(trazas[p][:-1]) for p in PATRONES}
    media = {p: usadas[p][0] for p in PATRONES}
    u_media = {p: usadas[p][1] / np.sqrt(n) for p in PATRONES}
    u, dentro = {}, {}
    for p in PATRONES:
        expandida = incertidumbre_corregida(media, u_media, trazas[p][-1], usadas[p][1])
        u[p] = expandida
        dentro[p] = np.mean(np.concatenate([np.abs(residuo[p].real) <= expandida.real,
                                            np.abs(residuo[p].imag) <= expandida.imag]))

    print("\nResiduo tras corregir la repetición no usada (mediana / máximo, dB):")
    for p in PATRONES:
        print(f"  {p:8s} {np.median(db(residuo[p])):6.1f} / {db(residuo[p]).max():6.1f}")
    peor = max(PATRONES, key=lambda p: db(residuo[p]).max())
    print(f"Peor punto: {peor} a {f[np.argmax(db(residuo[peor]))] / 1e6:g} MHz")

    print(f"\nIncertidumbre propagada con rfmeasurement ({COBERTURA:.0%}), a partir de {n} repeticiones:")
    for p in PATRONES:
        print(f"  {p:8s} mediana {np.median(db(u[p])):6.1f} dB; residuo dentro de la incertidumbre en el "
              f"{dentro[p]:.0%} de los puntos")
    # El factor de cobertura de rfmeasurement supone normalidad; con una desviación típica estimada
    # con pocos grados de libertad la cobertura real es menor (t de Student).
    k = stats.norm.ppf(0.5 + COBERTURA / 2)
    esperado = 2 * stats.t.cdf(k, df=n - 1) - 1
    print(f"  Solo con ruido y {n} repeticiones se espera un {esperado:.0%}, no un {COBERTURA:.0%}. Bastante por debajo\n"
          "  de eso indica algo más que repetibilidad: deriva, reconexión o calentamiento.")

    print("\nPresupuesto del Γ corregido de la carga (parte real), con Monte Carlo como contraste:")
    for i in np.unique([np.argmin(np.abs(f - x)) for x in np.geomspace(f[0], f[-1], 4)]):
        gammas = {q: media[q][i] for q in PATRONES} | {"medida": trazas["carga"][-1][i]}
        us = {q: u_media[q][i] for q in PATRONES} | {"medida": usadas["carga"][1][i]}
        ev = evaluar(modelo_sol(gammas, us, f_hz=f[i]), n_muestras=2000)
        mayor = ev.presupuesto.ranked[0]
        print(f"  {f[i] / 1e6:9.3f} MHz: u = {ev.lineal.standard_uncertainty:.1e} (lineal), "
              f"{ev.resultado.standard_uncertainty:.1e} (Monte Carlo); domina {mayor.source.name} "
              f"({mayor.percentage_of_variance:.0f} % de la varianza)")

    figuras.mkdir(parents=True, exist_ok=True)
    ruta_figura = figuras / f"{campana}_{cal_id}.png"
    figura(f, residuo, u, ruta_figura, f"Prueba de calibración SOL por software · {cal_id}")
    print(f"\nTérminos: {carpeta / (cal_id + '_terminos.npz')}\nFigura:   {ruta_figura}")


if __name__ == "__main__":
    main()
