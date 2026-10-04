"""Piloto del agua: ¿se repite la inmersión, y cuánta agua hace falta debajo y alrededor de la sonda?

Uso, con la sonda montada en el puerto 1 y solo agua destilada:
    .venv/bin/python scripts/piloto_agua.py --sonda v1
    .venv/bin/python scripts/piloto_agua.py --reanalizar agua_20261005T090000Z
    .venv/bin/python scripts/piloto_agua.py --simulado

Se mide la sonda al aire y luego en agua en la colocación de referencia (cara sumergida 3-5 mm,
al menos 20 mm de agua debajo y 15 mm hasta las paredes; ver hardware/sonda/v1). Después, cada
condición que se quiera probar, escribiendo una etiqueta: «reinmersion 1», «fondo 10 mm»,
«fondo 5 mm», «pared 5 mm», «sumergida 15 mm»… Tras cada una se ve cuánto se aparta de la
referencia, tramo a tramo.

La desviación se da en % de la distancia entre agua y aire, |Γ agua − Γ aire|. Es del orden del
error relativo que esa condición dejaría en la permitividad, y no necesita cortocircuito ni
ningún otro líquido. Compárala con el ruido: lo que no lo supere, no se distingue.
"""

import argparse
import glob
import tempfile
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from lcds.acquisition import SEGMENTOS, calibracion_firmware, conectar, desconectar, medir
from lcds.metadata import Medida, cargar_medida
from lcds.paths import FIGURAS, RAW
from lcds.reference import water
from lcds.sol import combinar
from medir_sonda import SondaSimulada, pedir_numero
from prueba_sol import FONDO, REJILLA, TINTA, TINTA_2, esperar_intro

CAMPANA = "piloto_agua"
REFERENCIA = "referencia"
RAMPA = ("#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b")  # un tono, en el orden en que se midió
SIMULADAS = (("reinmersion 1", 1.0), ("fondo 10 mm", 0.999), ("fondo 5 mm", 0.99), ("fondo 2 mm", 0.93))


def cargar_tanda(sesion, raw):
    """Barridos de una tanda guardada: ({condición: [trazas]} en orden de medida, temperatura del agua)."""
    datos, f, temp = {}, None, None
    for ruta in sorted(glob.glob(str(raw / CAMPANA / "*" / "*.s1p"))):
        f_i, s11, meta = cargar_medida(ruta)
        if meta["cal_sonda_id"] != sesion:
            continue
        f = f_i
        datos.setdefault(meta["notas"], []).append(s11)
        temp = meta["temp_muestra_c"] if meta["temp_muestra_c"] is not None else temp
    if f is None:
        raise SystemExit(f"No hay barridos de la tanda {sesion} en {raw / CAMPANA}")
    return f, datos, temp


def por_tramo(f, valores, formato="{:7.2f}"):
    return " ".join(formato.format(np.nanmedian(valores[(f >= a) & (f <= b)])) for a, b in SEGMENTOS)


def desviacion(trazas, datos):
    """Desviación de una condición respecto al agua de referencia, relativa a la distancia agua-aire."""
    referencia = combinar(datos[REFERENCIA])
    return np.abs(combinar(trazas) - referencia) / np.abs(referencia - combinar(datos["aire"]))


def ruido(datos):
    """Ruido de un barrido en la referencia, en las mismas unidades que la desviación."""
    referencia = np.array(datos[REFERENCIA])
    dispersion = np.sqrt(np.mean(np.abs(referencia - combinar(referencia)) ** 2, axis=0) * len(referencia) / (len(referencia) - 1))
    return dispersion / np.abs(combinar(referencia) - combinar(datos["aire"]))


def analizar(f, datos, temp, sesion, figuras):
    condiciones = [c for c in datos if c not in ("aire", REFERENCIA)]
    print(f"\nTanda {sesion}" + ("" if temp is None else f", agua a {temp:g} °C"))
    print("Desviación respecto al agua de referencia, en % de la distancia agua-aire (mediana por tramo)")
    print(f"   {'tramos (MHz)':22s} " + " ".join(f"{a / 1e6:g}-{b / 1e6:g}".rjust(7) for a, b in SEGMENTOS))
    print(f"   {'ruido de un barrido':22s} {por_tramo(f, 100 * ruido(datos))}")
    for c in condiciones:
        print(f"   {c[:22]:22s} {por_tramo(f, 100 * desviacion(datos[c], datos))}   ({len(datos[c])} barridos)")

    # La sonda en agua frente al aire: desfase añadido y capacidad que le corresponde
    cociente = combinar(datos[REFERENCIA]) / combinar(datos["aire"])
    theta = -np.angle(cociente) / 2
    capacidad = np.tan(theta) / (2 * np.pi * f * 50.0)
    print("\nAgua frente a aire (fiable solo donde vale la calibración del firmware, por encima de 100 MHz)")
    print(f"   {'|Γ agua / Γ aire|':22s} {por_tramo(f, np.abs(cociente), '{:7.3f}')}")
    print(f"   {'desfase añadido (°)':22s} {por_tramo(f, np.degrees(2 * theta), '{:7.1f}')}")
    print(f"   {'capacidad añadida (pF)':22s} {por_tramo(f, 1e12 * capacidad, '{:7.2f}')}")
    if temp is not None:
        eps = water(f, temp).real
        print(f"   {'C0 = añadida/(ε′−1) (pF)':22s} {por_tramo(f, 1e12 * capacidad / (eps - 1), '{:7.3f}')}")
        print("   C0 es la capacidad de la apertura en vacío según el modelo capacitivo: si el modelo vale, sale\n"
              "   parecida en los tramos altos. Si cae con la frecuencia, el agua ya no es una carga pequeña.")

    if not condiciones:
        return
    figuras.mkdir(parents=True, exist_ok=True)
    ruta = figuras / f"{CAMPANA}_{sesion}.png"
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": REJILLA, "text.color": TINTA,
                         "axes.labelcolor": TINTA_2, "xtick.color": TINTA_2, "ytick.color": TINTA_2})
    fig, eje = plt.subplots(figsize=(8.6, 4.8), facecolor=FONDO)
    eje.set_facecolor(FONDO)
    eje.loglog(f, 100 * ruido(datos), color=TINTA_2, lw=1.0, ls="--", label="ruido de un barrido")
    for i, c in enumerate(condiciones):
        color = RAMPA[round(i * (len(RAMPA) - 1) / max(len(condiciones) - 1, 1))]
        eje.loglog(f, 100 * desviacion(datos[c], datos), color=color, lw=1.3, label=c)
    eje.set_title("Desviación respecto al agua de referencia, en % de la distancia entre agua y aire",
                  loc="left", fontsize=10, color=TINTA)
    eje.set_xlabel("Frecuencia (Hz)")
    eje.grid(True, which="major", color=REJILLA, lw=0.6)
    eje.spines[["top", "right"]].set_visible(False)
    eje.legend(frameon=False, fontsize=8, title="En el orden en que se midió", title_fontsize=8,
               loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig.tight_layout()
    fig.savefig(ruta, dpi=150, facecolor=FONDO)
    plt.close(fig)
    print(f"\nFigura: {ruta}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--barridos", type=int, default=3, help="barridos por condición")
    ap.add_argument("--sonda", default=None, help="identificador de la sonda (hardware/README.md)")
    ap.add_argument("--puerto", default=None)
    ap.add_argument("--reanalizar", metavar="ID", help="analiza una tanda ya guardada, sin medir")
    ap.add_argument("--simulado", action="store_true")
    args = ap.parse_args()

    if args.reanalizar:
        analizar(*cargar_tanda(args.reanalizar, RAW), args.reanalizar, FIGURAS)
        return
    if args.barridos < 2:
        ap.error("hacen falta al menos 2 barridos por condición")

    sesion = "agua_" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    temporal = Path(tempfile.mkdtemp(prefix="piloto_agua_")) if args.simulado else None
    raw, figuras = (temporal / "raw", temporal) if temporal else (RAW, FIGURAS)
    vna = SondaSimulada() if args.simulado else conectar(args.puerto)
    cuenta, datos, temp = {}, {}, 25.0

    def serie(muestra, etiqueta, temp_c=None):
        for _ in range(args.barridos):
            cuenta[muestra] = cuenta.get(muestra, 0) + 1
            medida = Medida(campana=CAMPANA, muestra=muestra, repeticion=cuenta[muestra], sonda_id=args.sonda,
                            cal_sonda_id=sesion, temp_muestra_c=temp_c, notas=etiqueta)
            _, medicion = medir(vna, medida, raiz=raw)
            datos.setdefault(etiqueta, []).append(medicion.data.s[:, 0, 0])
        return medicion.data.f

    try:
        if not args.simulado:
            print(f"Calibración del firmware: {calibracion_firmware(vna)} (no la cambies durante la prueba)")
            esperar_intro("Sonda al aire, limpia, seca y sin nada cerca. Pulsa Intro… ")
        else:
            vna.poner("aire", temp)
        serie("aire", "aire")
        if not args.simulado:
            esperar_intro("Agua de referencia: cara sumergida 3–5 mm, sin burbujas, con 20 mm de agua debajo y 15 mm "
                          "hasta las paredes. Pulsa Intro… ")
            temp = pedir_numero("  Temperatura del agua (°C): ")
        else:
            vna.poner("agua", temp)
        f = serie("agua", REFERENCIA, temp)
        print(f"Referencia medida. Ruido de un barrido, % por tramo: {por_tramo(f, 100 * ruido(datos))}")

        pendientes = list(SIMULADAS)
        while True:
            if args.simulado:
                if not pendientes:
                    break
                etiqueta, factor = pendientes.pop(0)
                vna.eps = lambda fr, k=factor: water(fr, temp) * k
            else:
                etiqueta = input("\nCondición a probar (p. ej. «reinmersion 1», «fondo 5 mm»; Intro vacío para terminar): ").strip()
                if not etiqueta:
                    break
                if etiqueta in datos:
                    print("  Esa etiqueta ya está usada; elige otra.")
                    continue
                esperar_intro("  Coloca la sonda, comprueba que no hay burbujas y pulsa Intro… ")
            serie("agua", etiqueta, temp)
            print(f"  {etiqueta}: desviación % por tramo: {por_tramo(f, 100 * desviacion(datos[etiqueta], datos))}")
    finally:
        if not args.simulado:
            desconectar(vna)

    analizar(*cargar_tanda(sesion, raw), sesion, figuras)


if __name__ == "__main__":
    main()
