"""¿Se esquivan los saltos midiendo con dos juegos de tramos solapados y desplazados?

Uso, con un abierto o un corto fijo en el puerto 1 y sin tocar nada durante la prueba:
    .venv/bin/python scripts/prueba_saltos_tramos.py              # unos 10 minutos
    .venv/bin/python scripts/prueba_saltos_tramos.py --simulado   # sin equipo, para probar el flujo

Los saltos de fase se concentran en torno al 20-35 % del recorrido de cada tramo, no en sus
extremos. Un solape pequeño entre tramos vecinos no los evita, porque la zona afectada apenas se
mueve; hace falta que cada frecuencia se mida en dos tramos que empiecen en sitios muy distintos.

El juego A son los tramos de siempre, cortados en 1, 10, 100 y 1000 MHz. El juego B corta en 0,3,
3, 30 y 300 MHz, de modo que la zona afectada de cada tramo de A cae en la parte final de un
tramo de B, y al revés. La prueba alterna barridos de A y de B y comprueba tres cosas:

1. que cada juego tiene sus saltos en su propia zona (15-40 % de cada tramo);
2. que las frecuencias malas de un juego salen limpias en el otro;
3. cuántos saltos quedan al combinarlos, quedándose en cada juego solo con los puntos de fuera
   de su zona.
"""

import argparse
import tempfile
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from lcds.acquisition import F_START_HZ, F_STOP_HZ, SEGMENTOS, conectar, desconectar, medir
from lcds.metadata import Medida
from lcds.paths import FIGURAS, RAW
from prueba_saltos import saltos
from prueba_saltos_puntos import VNAConSaltos
from prueba_sol import FONDO, REJILLA, TINTA, TINTA_2, db

JUEGOS = {
    "A": SEGMENTOS,
    "B": ((F_START_HZ, 0.3e6), (0.3e6, 3e6), (3e6, 30e6), (30e6, 300e6), (300e6, F_STOP_HZ)),
}
ZONA = (0.15, 0.40)  # parte del recorrido de cada tramo donde se concentran los saltos
COLOR = {"A": "#2a78d6", "B": "#eb6834"}


def en_zona(f, segmentos):
    """Puntos que caen en la zona afectada de alguno de los tramos."""
    dentro = np.zeros(f.size, dtype=bool)
    for a, b in segmentos:
        dentro |= (f >= a + ZONA[0] * (b - a)) & (f <= a + ZONA[1] * (b - a))
    return dentro


def figura(f, tasa, ruta):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": REJILLA, "text.color": TINTA,
                         "axes.labelcolor": TINTA_2, "xtick.color": TINTA_2, "ytick.color": TINTA_2})
    fig, ejes = plt.subplots(2, 1, figsize=(8, 5.8), sharex=True, sharey=True, facecolor=FONDO)
    for eje, (nombre, segmentos) in zip(ejes, JUEGOS.items()):
        eje.set_facecolor(FONDO)
        for i, (a, b) in enumerate(segmentos):
            eje.axvspan(a + ZONA[0] * (b - a), a + ZONA[1] * (b - a), color=COLOR[nombre], alpha=0.12, lw=0,
                        label="zona del 15–40 % de cada tramo" if i == 0 else None)
        eje.semilogx(f[nombre], 100 * tasa[nombre], color=COLOR[nombre], lw=1.2, label="barridos con salto")
        cortes = ", ".join(f"{b / 1e6:g}" for _, b in segmentos[:-1])
        eje.set_title(f"Juego {nombre} (cortes en {cortes} MHz): barridos con salto en cada frecuencia (%)",
                      loc="left", fontsize=9, color=TINTA)
        eje.grid(True, which="major", color=REJILLA, lw=0.6)
        eje.spines[["top", "right"]].set_visible(False)
        eje.margins(x=0.02)
        eje.legend(frameon=False, fontsize=8, loc="upper left")
    ejes[-1].set_xlabel("Frecuencia (Hz)")
    fig.tight_layout()
    fig.savefig(ruta, dpi=150, facecolor=FONDO)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--barridos", type=int, default=12, help="barridos completos de cada juego")
    ap.add_argument("--umbral", type=float, default=0.03, help="desviación de Gamma que cuenta como salto")
    ap.add_argument("--patron", default="abierto", help="qué hay conectado al puerto (para los metadatos)")
    ap.add_argument("--puerto", default=None)
    ap.add_argument("--simulado", action="store_true")
    args = ap.parse_args()

    sello = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    temporal = Path(tempfile.mkdtemp(prefix="prueba_saltos_tramos_")) if args.simulado else None
    raw, figuras = (temporal / "raw", temporal) if temporal else (RAW, FIGURAS)
    vna = VNAConSaltos() if args.simulado else conectar(args.puerto)
    trazas, f = {j: [] for j in JUEGOS}, {}
    try:
        print(f"Series alternadas: {args.barridos} barridos de cada juego de tramos")
        for i in range(1, args.barridos + 1):
            for nombre, segmentos in JUEGOS.items():
                medida = Medida(campana="piloto_saltos", muestra=f"{args.patron}_tramos{nombre}", repeticion=i,
                                cal_sol_id=f"saltos_tramos_{sello}", notas=f"prueba de saltos; juego de tramos {nombre}")
                _, medicion = medir(vna, medida, segmentos=segmentos, raiz=raw)
                trazas[nombre].append(medicion.data.s[:, 0, 0])
                f[nombre] = medicion.data.f
            print(f"   barrido {i}/{args.barridos}", end="\r", flush=True)
    finally:
        if not args.simulado:
            desconectar(vna)

    marcados = {j: saltos(trazas[j], args.umbral) for j in JUEGOS}
    tasa = {j: marcados[j].mean(axis=0) for j in JUEGOS}
    propia = {j: en_zona(f[j], JUEGOS[j]) for j in JUEGOS}

    print(f"\n\n1) Saltos de cada juego (desviación mayor que {args.umbral:g} respecto a su mediana)")
    for j in JUEGOS:
        print(f"   juego {j}: {marcados[j].mean():6.2%} en total; {marcados[j][:, propia[j]].mean():6.2%} dentro de su "
              f"zona (15–40 % de cada tramo); {marcados[j][:, ~propia[j]].mean():6.2%} fuera")

    print("\n2) Las frecuencias de la zona de un juego, medidas con el otro")
    for j, otro in (("A", "B"), ("B", "A")):
        ajena = en_zona(f[otro], JUEGOS[j])  # puntos del otro juego en las frecuencias malas de este
        print(f"   zona de {j}: {marcados[j][:, propia[j]].mean():6.2%} de saltos medida con {j}; "
              f"{marcados[otro][:, ajena].mean():6.2%} medida con {otro}")

    print("\n3) Combinación: de cada juego, solo los puntos de fuera de su zona")
    buenos = np.concatenate([marcados[j][:, ~propia[j]] for j in JUEGOS], axis=1)
    f_comb = np.concatenate([f[j][~propia[j]] for j in JUEGOS])
    orden = np.argsort(f_comb)
    print(f"   juego A solo:  {f['A'].size} frecuencias; {marcados['A'].mean():6.2%} de puntos con salto; "
          f"peor frecuencia: salto en el {tasa['A'].max():.0%} de los barridos")
    print(f"   combinación:   {f_comb.size} frecuencias; {buenos.mean():6.2%} de puntos con salto; "
          f"peor frecuencia: salto en el {buenos.mean(axis=0).max():.0%} de los barridos")
    hueco = np.diff(np.log10(f_comb[orden])).max()
    print(f"   mayor hueco entre frecuencias consecutivas de la combinación: un factor {10 ** hueco:.2f}")
    for j in JUEGOS:
        t = np.array(trazas[j])
        mediana = np.median(t.real, axis=0) + 1j * np.median(t.imag, axis=0)
        print(f"   ruido de los puntos sin salto, juego {j}: {db(np.median(np.abs(t - mediana)[~marcados[j]])):.0f} dB")

    figuras.mkdir(parents=True, exist_ok=True)
    ruta = figuras / f"piloto_saltos_tramos_{sello}.png"
    figura(f, tasa, ruta)
    print(f"\nBarridos guardados en {raw / 'piloto_saltos'}\nFigura: {ruta}")


if __name__ == "__main__":
    main()
