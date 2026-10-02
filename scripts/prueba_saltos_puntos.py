"""¿Los saltos van con el número de punto o con la frecuencia? Compara tramos de 101 y de 51 puntos.

Uso, con un abierto o un corto fijo en el puerto 1 y sin tocar nada durante la prueba:
    .venv/bin/python scripts/prueba_saltos_puntos.py              # unos 9 minutos
    .venv/bin/python scripts/prueba_saltos_puntos.py --simulado   # sin equipo, para probar el flujo

En la prueba del 2 de octubre los saltos de fase se concentraban entre los puntos 20 y 40 de cada
tramo de 101, es decir, entre el 20 y el 40 % del tramo. Con 101 puntos no se puede saber cuál de
las dos cosas manda. Con 51 puntos por tramo, sobre las mismas frecuencias de inicio y fin:

- si la zona afectada sigue en los puntos 20-40, los saltos van con el número de punto (o con el
  tiempo desde que empieza el barrido), y pasa a ocupar del 40 al 80 % del tramo;
- si sigue entre el 20 y el 40 % del tramo (puntos 10-20), van con la frecuencia.

Las dos series se intercalan para que la deriva no favorezca a ninguna.
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
from prueba_saltos import saltos
from prueba_sol import FONDO, REJILLA, TINTA, TINTA_2, VNASimulado, db

PUNTOS = (101, 51)
COLOR = {101: "#2a78d6", 51: "#eb6834"}


class VNAConSaltos(VNASimulado):
    """Equipo ficticio con saltos de fase entre los puntos 20 y 40 de cada barrido."""

    def sweep(self):
        s11, s21, f = super().sweep()
        s11 = np.asarray(s11)
        zona = (np.arange(s11.size) >= 20) & (np.arange(s11.size) < 40)
        salta = zona & (self.rng.random(s11.size) < 0.08)
        return list(np.where(salta, s11 * np.exp(1j * np.radians(4)), s11)), s21, f


def posiciones(f, n):
    """Número de punto (0..n-1) de cada frecuencia dentro de su tramo.

    Al unir los tramos, el punto compartido por dos tramos contiguos se queda en el primero, de
    modo que los tramos siguientes empiezan en su punto 1.
    """
    indice = np.empty(f.size, dtype=int)
    for j, (a, b) in enumerate(SEGMENTOS):
        k = np.flatnonzero((f >= a) & (f <= b) if j == 0 else (f > a) & (f <= b))
        indice[k] = np.arange(n - k.size, n)
    return indice


def tiempos(vna, n):
    """Segundos que tarda el equipo en barrer cada tramo con n puntos."""
    duracion = []
    for a, b in SEGMENTOS:
        t0 = time.monotonic()
        vna.set_sweep(int(a), int(b), n)
        duracion.append(time.monotonic() - t0)
    return duracion


def figura(tasa, ruta):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": REJILLA, "text.color": TINTA,
                         "axes.labelcolor": TINTA_2, "xtick.color": TINTA_2, "ytick.color": TINTA_2})
    fig, ejes = plt.subplots(2, 1, figsize=(8, 5.8), sharey=True, facecolor=FONDO)
    paneles = (("indice", "Número de punto dentro del tramo", "Saltos según el número de punto (% de los barridos)"),
               ("fraccion", "Posición dentro del tramo (% del intervalo de frecuencias)",
                "Saltos según la posición en frecuencia (% de los barridos)"))
    for eje, (clave, rotulo_x, titulo) in zip(ejes, paneles):
        eje.set_facecolor(FONDO)
        for n in PUNTOS:
            x = np.arange(n) if clave == "indice" else 100 * np.arange(n) / (n - 1)
            eje.plot(x, 100 * tasa[n], color=COLOR[n], lw=1.6, label=f"{n} puntos por tramo")
        eje.set_title(titulo, loc="left", fontsize=9, color=TINTA)
        eje.set_xlabel(rotulo_x)
        eje.grid(True, color=REJILLA, lw=0.6)
        eje.spines[["top", "right"]].set_visible(False)
    ejes[0].legend(frameon=False, fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(ruta, dpi=150, facecolor=FONDO)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--barridos", type=int, default=12, help="barridos completos por serie")
    ap.add_argument("--umbral", type=float, default=0.03, help="desviación de Gamma que cuenta como salto")
    ap.add_argument("--patron", default="abierto", help="qué hay conectado al puerto (para los metadatos)")
    ap.add_argument("--puerto", default=None)
    ap.add_argument("--simulado", action="store_true")
    args = ap.parse_args()

    sello = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    temporal = Path(tempfile.mkdtemp(prefix="prueba_saltos_puntos_")) if args.simulado else None
    raw, figuras = (temporal / "raw", temporal) if temporal else (RAW, FIGURAS)
    vna = VNAConSaltos() if args.simulado else conectar(args.puerto)
    trazas, frecuencias = {n: [] for n in PUNTOS}, {}
    try:
        if not args.simulado:
            print("1) Tiempo de barrido por tramo (s) y por punto (ms)")
            print("   tramos (MHz): " + "  ".join(f"{a / 1e6:g}-{b / 1e6:g}" for a, b in SEGMENTOS))
            for n in PUNTOS:
                d = tiempos(vna, n)
                print(f"   {n:3d} puntos: " + "  ".join(f"{x:5.2f}" for x in d)
                      + f"   → {1000 * np.mean(d) / n:.0f} ms por punto")

        print(f"\n2) Series alternadas: {args.barridos} barridos de cada tipo")
        for i in range(1, args.barridos + 1):
            for n in PUNTOS:
                medida = Medida(campana="piloto_saltos", muestra=f"{args.patron}_{n}puntos", repeticion=i,
                                cal_sol_id=f"saltos_puntos_{sello}", notas=f"prueba de saltos; {n} puntos por tramo")
                _, medicion = medir(vna, medida, n_puntos=n, raiz=raw)
                trazas[n].append(medicion.data.s[:, 0, 0])
                frecuencias[n] = medicion.data.f
            print(f"   barrido {i}/{args.barridos}", end="\r", flush=True)
    finally:
        if not args.simulado:
            desconectar(vna)

    print(f"\n\n3) Saltos (desviación mayor que {args.umbral:g} respecto a la mediana de la serie)")
    tasa, centro = {}, {}
    for n in PUNTOS:
        f = frecuencias[n]
        marcados = saltos(trazas[n], args.umbral)
        indice = posiciones(f, n)
        tasa[n] = np.array([marcados[:, indice == i].mean() if np.any(indice == i) else 0.0 for i in range(n)])
        donde = np.repeat(indice, marcados.sum(axis=0))  # el número de punto de cada salto
        t = np.array(trazas[n])
        mediana = np.median(t.real, axis=0) + 1j * np.median(t.imag, axis=0)
        ruido = np.median(np.abs(t - mediana)[~marcados])
        print(f"   {n:3d} puntos: {marcados.mean():6.2%} de los puntos con salto ({marcados.sum()} saltos); "
              f"ruido sin saltos {db(ruido):.0f} dB")
        if donde.size < 10:
            print("               demasiado pocos saltos para situarlos")
            continue
        q = np.percentile(donde, [25, 50, 75])
        centro[n] = q[1]
        print(f"               número de punto: mediana {q[1]:.0f} (mitad central: {q[0]:.0f}–{q[2]:.0f}); "
              f"posición en el tramo: mediana {100 * q[1] / (n - 1):.0f} % "
              f"({100 * q[0] / (n - 1):.0f}–{100 * q[2] / (n - 1):.0f} %)")
        decenas = [tasa[n][i:i + n // 10].mean() for i in range(0, n - n % 10, max(n // 10, 1))][:10]
        print("               tasa por décimas del tramo: " + " ".join(f"{x:5.1%}" for x in decenas))

    if len(centro) == 2:
        por_punto = abs(centro[101] - centro[51])
        por_frecuencia = abs(centro[101] / 100 - centro[51] / 50)
        print("\n4) Lectura")
        if por_punto <= 6 and por_frecuencia > 0.15:
            print("   La zona afectada cae en los mismos números de punto con 101 y con 51: los saltos van con\n"
                  "   el número de punto o con el tiempo desde el inicio del barrido, no con la frecuencia.")
        elif por_frecuencia <= 0.08 and por_punto > 6:
            print("   La zona afectada cae en la misma parte del intervalo de frecuencias con 101 y con 51:\n"
                  "   los saltos van con la frecuencia, no con el número de punto.")
        else:
            print("   No queda claro: la zona afectada no coincide ni por número de punto ni por frecuencia.\n"
                  "   Mira la figura y la tasa por décimas.")

    figuras.mkdir(parents=True, exist_ok=True)
    ruta = figuras / f"piloto_saltos_puntos_{sello}.png"
    figura(tasa, ruta)
    print(f"\nBarridos guardados en {raw / 'piloto_saltos'}\nFigura: {ruta}")


if __name__ == "__main__":
    main()
