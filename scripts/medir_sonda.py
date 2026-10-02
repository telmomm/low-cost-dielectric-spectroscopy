"""Medida con la sonda coaxial: terna de calibración y líquidos, de los .s1p a eps' y sigma.

Uso:
    .venv/bin/python scripts/medir_sonda.py --sonda v1
    .venv/bin/python scripts/medir_sonda.py --simulado

Primero se mide la terna de la sonda: cortocircuito en la apertura, aire y agua desionizada a
temperatura conocida. Después, cada muestra que se quiera. La conversión usa el modelo capacitivo
(bilineal con tres patrones), que absorbe cualquier corrección fija entre la apertura y el dato
guardado: no hace falta una SOL aparte, pero la calibración del firmware no debe cambiar entre
la terna y las muestras.

Para cada muestra se calcula eps' y sigma con su incertidumbre expandida (motor de
rfmeasurement; fuentes: repetibilidad de los cuatro coeficientes de reflexión y temperatura del
agua). Si la muestra es metanol, etanol o agua, se compara con su modelo de referencia. El agua
sirve para comprobar el flujo, no para validar: es el líquido de calibración.
"""

import argparse
import csv
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from rfmeasurement.uncertainty import expand, propagate_linear

from lcds.acquisition import SEGMENTOS, calibracion_firmware, conectar, desconectar, medir
from lcds.metadata import Medida
from lcds.paths import FIGURAS, PROCESSED, RAW
from lcds.probe import epsilon_bilinear, gamma_capacitive
from lcds.provenance import guardar_registros, registrar
from lcds.reference import conductivity, ethanol, methanol, water
from lcds.sol import promediar
from lcds.uncertainty import evaluar, modelo
from prueba_sol import FONDO, REJILLA, TINTA, TINTA_2, esperar_intro

TERNA = ("corto", "aire", "agua")
INSTRUCCION = {
    "corto": "Pon el cortocircuito sobre la apertura de la sonda",
    "aire": "Deja la sonda al aire, limpia y seca",
    "agua": "Sumerge la sonda en agua desionizada, sin burbujas en la apertura",
}
REFERENCIAS = {"metanol": methanol, "etanol": ethanol, "agua": water}
COBERTURA = 0.95
AZUL = "#2a78d6"


class SondaSimulada:
    """Sonda capacitiva ficticia tras una red de error fija, con ruido proporcional a la señal."""

    def __init__(self):
        self.rng = np.random.default_rng(3)
        self.eps = lambda f: np.ones_like(f)
        self.corto = False

    def set_sweep(self, inicio, fin, puntos):
        self.f = np.linspace(inicio, fin, puntos)

    def sweep(self):
        gamma = -np.ones(self.f.size, complex) if self.corto else gamma_capacitive(self.f, self.eps(self.f), 0.03e-12, 0.02e-12)
        medido = 0.03 - 0.01j + 0.9 * np.exp(-2j * np.pi * self.f * 0.3e-9) * gamma / (1 - (0.05 + 0.04j) * gamma)
        ruido = 1 + self.rng.normal(0, 5e-4, self.f.size) + 1j * self.rng.normal(0, 5e-4, self.f.size)
        return list(medido * ruido), [0j] * self.f.size, list(self.f)

    def info(self):
        return {"Serial Number": "simulado", "Version": "simulado"}

    def poner(self, material, temp_c):
        self.corto = material == "corto"
        self.eps = {"aire": lambda f: np.ones_like(f)}.get(material) or (
            lambda f: REFERENCIAS.get(material, methanol)(f, temp_c))


def pedir_numero(texto):
    while True:
        try:
            return float(input(texto).replace(",", "."))
        except ValueError:
            print("  Escribe un número, por ejemplo 23.5")


def serie(vna, muestra, n, base, raw, pausar, temp_c=None):
    """Mide n repeticiones de una muestra. Devuelve (f, trazas, record_id de cada barrido)."""
    trazas, ids = [], []
    for i in range(1, n + 1):
        medida = Medida(muestra=muestra, repeticion=i, temp_muestra_c=temp_c, **base)
        _, medicion = medir(vna, medida, raiz=raw, pausar=pausar)
        trazas.append(medicion.data.s[:, 0, 0])
        ids.append(medicion.provenance[0].record_id)
        print(f"  {muestra} {i}/{n}", end="\r", flush=True)
    dispersion = np.median(np.abs(np.array(trazas) - np.mean(trazas, axis=0)), axis=1).max()
    print(f"  {muestra}: {n} barridos" + ("" if dispersion < 0.05 else
          f"  AVISO: las repeticiones no coinciden entre sí ({dispersion:.2f}); ¿burbuja o sonda movida?"))
    return medicion.data.f, trazas, ids


def incertidumbre(f, gammas, u_gammas, temp_agua, u_temp):
    """Incertidumbre expandida de eps' y sigma a cada frecuencia (propagación lineal)."""
    salida = {}
    for magnitud in ("eps_real", "sigma"):
        U = np.full(f.size, np.nan)
        for i in range(f.size):
            g = {k: complex(v[i]) for k, v in gammas.items()}
            u = {k: complex(v[i]) for k, v in u_gammas.items()}
            try:
                lineal = propagate_linear(modelo(f[i], g, u, temp_agua, u_temp, magnitud))
                U[i] = expand(lineal.value, lineal.standard_uncertainty, COBERTURA)[0]
            except (ValueError, ZeroDivisionError, FloatingPointError):
                pass
        salida[magnitud] = U
    return salida


def figura(f, eps, sigma, U, ref, titulo, ruta):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": REJILLA, "text.color": TINTA,
                         "axes.labelcolor": TINTA_2, "xtick.color": TINTA_2, "ytick.color": TINTA_2})
    fig, ejes = plt.subplots(2, 1, figsize=(8, 6.2), sharex=True, facecolor=FONDO)
    paneles = ((eps.real, U["eps_real"], None if ref is None else ref.real, "Permitividad relativa, ε′"),
               (sigma, U["sigma"], None if ref is None else conductivity(f, ref), "Conductividad equivalente, σ (S/m)"))
    fiable = f >= 10e6  # por debajo la sonda apenas tiene sensibilidad: no debe fijar la escala
    for eje, (valor, banda, referencia, rotulo) in zip(ejes, paneles):
        eje.set_facecolor(FONDO)
        eje.fill_between(f, valor - banda, valor + banda, color=AZUL, alpha=0.2, lw=0,
                         label=f"incertidumbre expandida ({COBERTURA:.0%})")
        eje.semilogx(f, valor, color=AZUL, lw=1.4, label="medida")
        guia = valor[fiable]
        if referencia is not None:
            eje.semilogx(f, referencia, color=TINTA, lw=1.0, ls="--", label="referencia")
            guia = np.concatenate([guia, referencia])
        bajo, alto = np.nanpercentile(guia, [2, 98])
        margen = 0.25 * (alto - bajo) or 1.0
        eje.set_ylim(bajo - margen, alto + margen)
        eje.set_title(rotulo, loc="left", fontsize=9, color=TINTA)
        eje.grid(True, which="major", color=REJILLA, lw=0.6)
        eje.spines[["top", "right"]].set_visible(False)
        eje.margins(x=0.02)
    ejes[1].legend(frameon=False, fontsize=8, loc="upper left")
    ejes[1].set_xlabel("Frecuencia (Hz)")
    fig.suptitle(titulo, x=0.02, ha="left", fontsize=10, color=TINTA)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(ruta, dpi=150, facecolor=FONDO)
    plt.close(fig)


def resumen(f, eps, sigma, U, ref):
    def pct(x):
        return f"{x:7.1f}" if np.isfinite(x) and abs(x) < 1e4 else "   >1e4"

    print("    tramo (MHz)        ε′ mediana   U(ε′) %   σ mediana (S/m)   U(σ) %"
          + ("   error ε′ %   error σ %   dentro de U" if ref is not None else ""))
    for a, b in SEGMENTOS:
        k = (f >= a) & (f <= b)
        linea = (f"    {a / 1e6:7.2f}–{b / 1e6:<7g}  {np.median(eps.real[k]):9.2f}   "
                 f"{pct(100 * np.nanmedian(U['eps_real'][k] / np.abs(eps.real[k])))}   {np.median(sigma[k]):13.4f}   "
                 f"{pct(100 * np.nanmedian(U['sigma'][k] / np.abs(sigma[k])))}")
        if ref is not None:
            sigma_ref = conductivity(f, ref)
            dentro = np.mean(np.concatenate([np.abs(eps.real[k] - ref.real[k]) <= U["eps_real"][k],
                                             np.abs(sigma[k] - sigma_ref[k]) <= U["sigma"][k]]))
            linea += (f"   {pct(100 * np.median(np.abs(eps.real[k] - ref.real[k]) / ref.real[k]))}"
                      f"     {pct(100 * np.median(np.abs(sigma[k] - sigma_ref[k]) / sigma_ref[k]))}      {dentro:5.0%}")
        print(linea)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--campana", default="cadena_minima")
    ap.add_argument("--sonda", default=None, help="identificador de la sonda (hardware/README.md)")
    ap.add_argument("--operador", default=None)
    ap.add_argument("--repeticiones", type=int, default=5)
    ap.add_argument("--u-temp", type=float, default=0.5, help="incertidumbre típica del termómetro, °C")
    ap.add_argument("--pausar", action="store_true", help="pausar el barrido continuo del equipo al medir")
    ap.add_argument("--puerto", default=None)
    ap.add_argument("--simulado", action="store_true")
    args = ap.parse_args()
    if args.repeticiones < 2:
        ap.error("hacen falta al menos 2 repeticiones para estimar la repetibilidad")

    sesion = "sonda_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    temporal = Path(tempfile.mkdtemp(prefix="medir_sonda_")) if args.simulado else None
    raw, processed, figuras = (temporal / "raw", temporal / "processed", temporal) if temporal else (RAW, PROCESSED, FIGURAS)
    carpeta = processed / args.campana
    carpeta.mkdir(parents=True, exist_ok=True)
    figuras.mkdir(parents=True, exist_ok=True)
    base = dict(campana=args.campana, sonda_id=args.sonda, operador=args.operador, cal_sonda_id=sesion)
    n = args.repeticiones
    vna = SondaSimulada() if args.simulado else conectar(args.puerto)
    try:
        if not args.simulado:
            print(f"Calibración del firmware: {calibracion_firmware(vna)} (no la cambies durante la sesión)")
        print(f"Sesión {sesion}. Terna de la sonda, {n} barridos por patrón.\n")
        medias, us, ids_terna, temp_agua = {}, {}, [], 25.0
        for patron in TERNA:
            temp = None
            if args.simulado:
                vna.poner(patron, temp_agua)
            else:
                esperar_intro(f"{INSTRUCCION[patron]} y, cuando esté listo, pulsa Intro… ")
            if patron == "agua":
                temp = temp_agua = 25.0 if args.simulado else pedir_numero("  Temperatura del agua (°C): ")
            f, trazas, ids = serie(vna, patron, n, base, raw, args.pausar, temp)
            medias[patron], us[patron] = promediar(trazas)
            ids_terna += ids
        fin_terna = time.monotonic()
        eps_agua = water(f, temp_agua)
        calibracion = registrar("calibrar_sonda", entradas=ids_terna,
                                parametros={"cal_sonda_id": sesion, "modelo": "capacitivo (bilineal)",
                                            "temp_agua_c": temp_agua, "referencia_agua": "Kaatze 1989"})

        pendientes = [("metanol", 25.0)] if args.simulado else None
        while True:
            if args.simulado:
                if not pendientes:
                    break
                nombre, temp = pendientes.pop(0)
                vna.poner(nombre, temp)
            else:
                nombre = input("\nNombre de la muestra (metanol, etanol, nacl_0p5…; Intro vacío para terminar): ").strip().lower()
                if not nombre:
                    break
                esperar_intro("  Limpia y seca la sonda, sumérgela sin burbujas y, cuando esté lista, pulsa Intro… ")
                temp = pedir_numero("  Temperatura de la muestra (°C): ")
            print(f"  Han pasado {(time.monotonic() - fin_terna) / 60:.1f} min desde la terna")
            f, trazas, ids = serie(vna, nombre, n, base, raw, args.pausar, temp)
            media, u = promediar(trazas)

            eps = epsilon_bilinear(media, medias["corto"], medias["aire"], medias["agua"], eps_agua)
            sigma = conductivity(f, eps)
            gammas = {"muestra": media, **medias}
            u_gammas = {k: v / np.sqrt(n) for k, v in {"muestra": u, **us}.items()}  # de las medias
            U = incertidumbre(f, gammas, u_gammas, temp_agua, args.u_temp)
            modelo_ref = REFERENCIAS.get(nombre)
            try:
                ref = modelo_ref(f, temp) if modelo_ref else None
            except ValueError as error:  # temperatura fuera de las tablas
                print(f"  Sin referencia: {error}")
                ref = None

            print(f"\n  {nombre} a {temp:g} °C" + ("" if ref is None else " (con referencia)"))
            resumen(f, eps, sigma, U, ref)
            if nombre == "agua":
                print("    El agua es el líquido de calibración: esta comparación solo comprueba el flujo.")

            print("    Presupuesto de ε′ (lineal) y contraste con Monte Carlo:")
            for i in np.unique([np.argmin(np.abs(f - x)) for x in (10e6, 100e6, 1e9)]):
                g = {k: complex(v[i]) for k, v in gammas.items()}
                ug = {k: complex(v[i]) for k, v in u_gammas.items()}
                ev = evaluar(modelo(f[i], g, ug, temp_agua, args.u_temp), n_muestras=2000)
                mayor = ev.presupuesto.ranked[0]
                print(f"      {f[i] / 1e6:7.1f} MHz: ε′ = {ev.lineal.value:.2f}, u = {ev.lineal.standard_uncertainty:.2g} "
                      f"(lineal) / {ev.resultado.standard_uncertainty:.2g} (Monte Carlo); domina "
                      f"{mayor.source.name} ({mayor.percentage_of_variance:.0f} %)")

            sello = f"{sesion}_{nombre}"
            with open(carpeta / f"{sello}.csv", "w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["f_hz", "eps_real", "eps_imag", "sigma_s_m", "U_eps_real", "U_sigma_s_m",
                            "ref_eps_real", "ref_eps_imag", "ref_sigma_s_m"])
                for i in range(f.size):
                    fila_ref = ["", "", ""] if ref is None else [ref[i].real, -ref[i].imag, conductivity(f[i], ref[i])]
                    w.writerow([f[i], eps[i].real, -eps[i].imag, sigma[i], U["eps_real"][i], U["sigma"][i], *fila_ref])
            conversion = registrar("convertir_a_permitividad", entradas=[*ids, calibracion.record_id],
                                   parametros={"muestra": nombre, "temp_muestra_c": temp, "repeticiones": n})
            propagacion = registrar("propagar_incertidumbre", entradas=[conversion.record_id],
                                    parametros={"metodo": "lineal (GUM)", "cobertura": COBERTURA,
                                                "u_temp_agua_c": args.u_temp, "motor": "rfmeasurement"})
            guardar_registros([calibracion, conversion, propagacion], carpeta / f"{sello}.procedencia.json")
            figura(f, eps, sigma, U, ref, f"{nombre} a {temp:g} °C · {sesion}", figuras / f"{args.campana}_{sello}.png")
            print(f"    Guardado: {carpeta / (sello + '.csv')}\n    Figura:   {figuras / (args.campana + '_' + sello + '.png')}")
    finally:
        if not args.simulado:
            desconectar(vna)


if __name__ == "__main__":
    main()
