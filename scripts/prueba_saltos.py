"""¿De dónde salen los saltos esporádicos? Compara barridos leídos con y sin pausar el equipo.

Uso, con un abierto o un corto fijo en el puerto 1 y sin tocar nada durante la prueba:
    .venv/bin/python scripts/prueba_saltos.py                 # unos 10 minutos
    .venv/bin/python scripts/prueba_saltos.py --simulado      # sin equipo, para probar el flujo

En la prueba de calibración del 2 de octubre, en un 7-9 % de los puntos alguna repetición se
apartaba de las demás en torno a 0,1. La sospecha es que el equipo sigue barriendo mientras se
leen los datos. El script lo comprueba de dos maneras:

1. Doble lectura: tras un barrido lee los datos dos veces seguidas. Si la segunda lectura
   difiere de la primera, el firmware está reescribiendo el búfer.
2. Series alternadas: barridos completos leídos como hasta ahora y con el barrido pausado,
   intercalados para que la deriva no favorezca a ninguno. Un salto es un punto que se aparta
   de la mediana de su serie más que el umbral.
"""

import argparse
import tempfile
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from lcds.acquisition import SEGMENTOS, conectar, desconectar, medir
from lcds.metadata import Medida
from lcds.paths import FIGURAS, RAW
from prueba_sol import FONDO, REJILLA, TINTA, TINTA_2, VNASimulado, db

MODOS = {"continuo": False, "pausado": True}
COLOR = {"continuo": "#2a78d6", "pausado": "#eb6834"}


def doble_lectura(vna, pausar, veces=6, espera_s=0.6):
    """Fracción de puntos que cambian entre dos lecturas seguidas del mismo barrido, por tramo."""
    consola = vna.vna.exec_command
    cambios = []
    if pausar:
        list(consola("pause"))
    try:
        for inicio, fin in SEGMENTOS:
            n = 0
            for _ in range(veces):
                vna.set_sweep(int(inicio), int(fin), 101)
                primera = list(consola("data 0"))
                time.sleep(espera_s)
                segunda = list(consola("data 0"))
                n += sum(a != b for a, b in zip(primera, segunda))
            cambios.append(n / (veces * 101))
    finally:
        if pausar:
            list(consola("resume"))
    return cambios


def saltos(trazas, umbral):
    """Matriz booleana (barrido, frecuencia): puntos que se apartan de la mediana de la serie."""
    trazas = np.array(trazas)
    mediana = np.median(trazas.real, axis=0) + 1j * np.median(trazas.imag, axis=0)
    return np.abs(trazas - mediana) > umbral


def bloques(fila):
    """Longitudes de las rachas de puntos contiguos marcados en un barrido."""
    borde = np.diff(np.concatenate([[0], fila.astype(int), [0]]))
    return np.flatnonzero(borde == -1) - np.flatnonzero(borde == 1)


def figura(f, desviacion, umbral, ruta):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": REJILLA, "text.color": TINTA,
                         "axes.labelcolor": TINTA_2, "xtick.color": TINTA_2, "ytick.color": TINTA_2})
    fig, ejes = plt.subplots(len(MODOS), 1, figsize=(8, 5.6), sharex=True, sharey=True, facecolor=FONDO)
    for eje, modo in zip(ejes, MODOS):
        eje.set_facecolor(FONDO)
        eje.semilogx(f, db(desviacion[modo]), color=COLOR[modo], lw=1.1)
        eje.axhline(db(umbral), color=TINTA_2, lw=0.8, ls="--")
        eje.annotate("umbral de salto", (f[0], db(umbral)), xytext=(2, 3), textcoords="offset points",
                     color=TINTA_2, fontsize=8)
        eje.set_title(f"Lectura con barrido {modo}: mayor desviación respecto a la mediana de la serie (dB)",
                      loc="left", fontsize=9, color=TINTA)
        eje.grid(True, which="major", color=REJILLA, lw=0.6)
        eje.spines[["top", "right"]].set_visible(False)
        eje.margins(x=0.02)
    ejes[-1].set_xlabel("Frecuencia (Hz)")
    fig.tight_layout()
    fig.savefig(ruta, dpi=150, facecolor=FONDO)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--barridos", type=int, default=12, help="barridos completos por modo")
    ap.add_argument("--umbral", type=float, default=0.03, help="desviación de Gamma que cuenta como salto")
    ap.add_argument("--patron", default="abierto", help="qué hay conectado al puerto (para los metadatos)")
    ap.add_argument("--puerto", default=None)
    ap.add_argument("--simulado", action="store_true")
    args = ap.parse_args()

    sello = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    temporal = Path(tempfile.mkdtemp(prefix="prueba_saltos_")) if args.simulado else None
    raw, figuras = (temporal / "raw", temporal) if temporal else (RAW, FIGURAS)
    vna = VNASimulado() if args.simulado else conectar(args.puerto)
    trazas = {modo: [] for modo in MODOS}
    try:
        if not args.simulado:
            print("1) Doble lectura: fracción de puntos que cambian entre dos lecturas del mismo barrido")
            print("   tramos (MHz): " + "  ".join(f"{a / 1e6:g}-{b / 1e6:g}" for a, b in SEGMENTOS))
            for modo, pausar in MODOS.items():
                print(f"   {modo:9s} " + "  ".join(f"{x:6.1%}" for x in doble_lectura(vna, pausar)))

        print(f"\n2) Series alternadas: {args.barridos} barridos por modo (unos {args.barridos * 2 * 25 // 60 + 1} min)")
        for i in range(1, args.barridos + 1):
            for modo, pausar in MODOS.items():
                medida = Medida(campana="piloto_saltos", muestra=f"{args.patron}_{modo}", repeticion=i,
                                cal_sol_id=f"saltos_{sello}", notas=f"prueba de saltos; lectura con barrido {modo}")
                _, medicion = medir(vna, medida, raiz=raw, pausar=pausar)
                trazas[modo].append(medicion.data.s[:, 0, 0])
            f = medicion.data.f
            print(f"   barrido {i}/{args.barridos}", end="\r", flush=True)
    finally:
        if not args.simulado:
            desconectar(vna)

    print(f"\n\n3) Saltos (desviación mayor que {args.umbral:g} respecto a la mediana de la serie)")
    desviacion = {}
    for modo in MODOS:
        marcados = saltos(trazas[modo], args.umbral)
        rachas = np.concatenate([bloques(fila) for fila in marcados]) if marcados.any() else np.array([0])
        t = np.array(trazas[modo])
        mediana = np.median(t.real, axis=0) + 1j * np.median(t.imag, axis=0)
        desviacion[modo] = np.abs(t - mediana).max(axis=0)
        print(f"   {modo:9s} puntos con salto: {marcados.mean():6.2%}; barridos afectados: "
              f"{marcados.any(axis=1).sum()}/{len(t)}; frecuencias afectadas: {marcados.any(axis=0).sum()}/{f.size}; "
              f"racha más larga: {rachas.max()} puntos")
        por_tramo = [marcados[:, (f >= a) & (f <= b)].mean() for a, b in SEGMENTOS]
        print("             por tramo: " + "  ".join(f"{x:6.2%}" for x in por_tramo))
        ruido = np.median(np.abs(t - mediana)[~marcados]) if (~marcados).any() else float("nan")
        print(f"             ruido de los puntos sin salto (mediana): {db(ruido):.0f} dB")

    figuras.mkdir(parents=True, exist_ok=True)
    ruta = figuras / f"piloto_saltos_{sello}.png"
    figura(f, desviacion, args.umbral, ruta)
    print(f"\nBarridos guardados en {raw / 'piloto_saltos'}\nFigura: {ruta}")


if __name__ == "__main__":
    main()
