"""Piloto del cortocircuito de la sonda: ¿se repite al recolocarlo, y da igual cobre que aluminio?

Uso, con la sonda ya rebajada y montada en el puerto 1:
    .venv/bin/python scripts/piloto_corto.py --sonda v1          # unos 25 minutos
    .venv/bin/python scripts/piloto_corto.py --reanalizar corto_20261003T090000Z
    .venv/bin/python scripts/piloto_corto.py --simulado

No hacen falta líquidos. Para cada material (lámina de cobre y papel de aluminio) se coloca el
cortocircuito varias veces sobre la cara de la sonda, retirándolo del todo entre una y otra, y se
barre dos veces cada vez. Entre colocaciones se mide la sonda al aire.

Responde a tres preguntas:

1. ¿Cuánto cambia el cortocircuito de una colocación a otra, frente al ruido de un barrido?
2. ¿Dan lo mismo el cobre y el aluminio?
3. ¿Se comporta la sonda al aire como una capacidad pequeña? Sale de la diferencia de fase entre
   aire y corto, y da una primera estimación de la capacidad de la apertura.

Las desviaciones se dan divididas por la distancia entre aire y corto, |Γ aire − Γ corto|: es la
escala con la que la calibración de la sonda convierte Γ en permitividad, así que un 1 % ahí es
del orden de un 1 % en el resultado.
"""

import argparse
import glob
import re
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
from lcds.probe import gamma_capacitive
from lcds.sol import combinar
from medir_sonda import SondaSimulada
from prueba_sol import FONDO, REJILLA, TINTA, TINTA_2, esperar_intro

CAMPANA = "piloto_corto"
MATERIALES = {"cobre": "la lámina de cobre", "aluminio": "el papel de aluminio"}
COLOR = {"cobre": "#eb6834", "aluminio": "#2a78d6"}
Z0 = 50.0


class SondaConCortoImperfecto(SondaSimulada):
    """Sonda ficticia (0,05 pF al aire) tras un tramo de línea ideal; el corto cambia en cada colocación."""

    def __init__(self):
        super().__init__()
        self.defecto = 0.0

    def colocar(self, material):
        self.corto = material is not None
        self.defecto = self.rng.normal(0, {"cobre": 0.004, "aluminio": 0.012}.get(material, 0.0))

    def sweep(self):
        f = self.f
        if self.corto:
            gamma = -np.exp(1j * self.defecto * f / 1e9)
        else:
            gamma = gamma_capacitive(f, 1.0, 0.05e-12)
        ruido = 1 + self.rng.normal(0, 5e-4, f.size) + 1j * self.rng.normal(0, 5e-4, f.size)
        return list(gamma * np.exp(-2j * np.pi * f * 0.3e-9) * ruido), [0j] * f.size, list(f)


def cargar_tanda(sesion, raw):
    """Barridos de una tanda guardada: {muestra: {colocación: [trazas]}}."""
    datos, f = {}, None
    for ruta in sorted(glob.glob(str(raw / CAMPANA / "*" / "*.s1p"))):
        f_i, s11, meta = cargar_medida(ruta)
        if meta["cal_sonda_id"] != sesion:
            continue
        f = f_i
        colocacion = int(re.search(r"colocación (\d+)", meta["notas"]).group(1))
        datos.setdefault(meta["muestra"], {}).setdefault(colocacion, []).append(s11)
    if f is None:
        raise SystemExit(f"No hay barridos de la tanda {sesion} en {raw / CAMPANA}")
    return f, datos


def por_tramo(f, valores, formato="{:6.2f}"):
    return "  ".join(formato.format(np.nanmedian(valores[(f >= a) & (f <= b)])) for a, b in SEGMENTOS)


def analizar(f, datos, sesion, figuras):
    aire = np.array([combinar(t) for t in datos["aire"].values()])
    ref_aire = combinar(aire)

    # ¿Hubo contacto? Un barrido es un cortocircuito de verdad si queda lejos del aire. Se compara
    # con el barrido más alejado, porque una lámina que no toca el conductor central se parece al aire.
    materiales = [m for m in MATERIALES if f"corto_{m}" in datos]
    tramos = [(f >= a) & (f <= b) for a, b in SEGMENTOS]

    def distancias(s):  # distancia al aire en cada tramo: el contacto puede perderse a mitad de un barrido
        return np.array([np.median(np.abs(s - ref_aire)[k]) for k in tramos])

    lejania = {m: {c: [distancias(s) for s in t] for c, t in datos[f"corto_{m}"].items()} for m in materiales}
    tope = np.max([d for m in materiales for ds in lejania[m].values() for d in ds], axis=0)

    def contacto(ds):  # fracción de tramos, entre todos los barridos de la colocación, con contacto
        return float(np.mean([d > 0.7 * tope for d in ds]))

    print(f"\nTanda {sesion}. Contacto de cada colocación (cuenta un tramo si llega al 70 % del más alejado del aire)")
    cortos = {}
    for m in materiales:
        buenas = [c for c, ds in lejania[m].items() if contacto(ds) == 1]
        estado = " ".join(f"{c}:{'sí' if c in buenas else ('a medias' if contacto(ds) > 0 else 'no')}"
                          for c, ds in sorted(lejania[m].items()))
        print(f"   {m:9s} {len(buenas)} de {len(lejania[m])} colocaciones con contacto en todos los tramos  ({estado})")
        if len(buenas) >= 2:
            cortos[m] = np.array([combinar(datos[f"corto_{m}"][c]) for c in buenas])
    if not cortos:
        raise SystemExit("Ningún material tiene al menos dos colocaciones con contacto: no hay nada que comparar.")
    ref_corto = combinar(np.concatenate(list(cortos.values())))
    escala = np.abs(ref_aire - ref_corto)  # distancia aire-corto: la escala de la calibración de la sonda

    # Ruido de un barrido: mitad de la diferencia entre los dos barridos de una misma colocación
    pares = [np.abs(t[0] - t[1]) / 2 for t in datos["aire"].values() if len(t) >= 2]
    ruido = np.median(pares, axis=0) / escala

    print("\nTramos (MHz): " + "  ".join(f"{a / 1e6:g}-{b / 1e6:g}" for a, b in SEGMENTOS))
    print("\n1) Dispersión entre colocaciones con contacto, en % de la distancia aire-corto (mediana por tramo)")
    print(f"   ruido de un barrido (aire) {por_tramo(f, 100 * ruido)}")
    dispersion = {}
    for nombre, t in (("aire", aire), *cortos.items()):
        centro = combinar(t)
        dispersion[nombre] = np.sqrt(np.mean(np.abs(t - centro) ** 2, axis=0) * len(t) / (len(t) - 1)) / escala
        etiqueta = "aire" if nombre == "aire" else f"corto de {nombre}"
        print(f"   {etiqueta:22s}   {por_tramo(f, 100 * dispersion[nombre])}   ({len(t)} colocaciones)")
    for m in cortos:  # ¿se mantiene el corto mientras se sujeta? diferencia entre los dos barridos de una colocación
        dentro = np.median([np.abs(t[0] - t[1]) / 2 for c, t in datos[f"corto_{m}"].items()
                            if contacto(lejania[m][c]) == 1], axis=0) / escala
        print(f"   {'  ' + m + ', mientras se sujeta':24s} {por_tramo(f, 100 * dentro)}")

    if len(cortos) == 2:
        diferencia = np.abs(combinar(cortos["cobre"]) - combinar(cortos["aluminio"])) / escala
        print("\n2) Diferencia entre el corto de cobre y el de aluminio, en % de la distancia aire-corto")
        print(f"   {'':25s}{por_tramo(f, 100 * diferencia)}")

    # Aire frente a corto: una apertura capacitiva da Γ aire / Γ corto = −exp(−2j·atan(ωCZ0))
    cociente = -ref_aire / ref_corto
    theta = -np.angle(cociente) / 2
    capacidad = np.tan(theta) / (2 * np.pi * f * Z0)
    tiempo = theta / (2 * np.pi * f)  # si fuera un trozo de línea en vez de una capacidad
    print("\n3) La sonda al aire frente al corto")
    print(f"   |Γ aire / Γ corto|        {por_tramo(f, np.abs(cociente), '{:6.3f}')}")
    print(f"   desfase respecto a 180°   {por_tramo(f, np.degrees(2 * theta), '{:6.2f}')}  (grados)")
    print(f"   capacidad equivalente     {por_tramo(f, 1e12 * capacidad, '{:6.3f}')}  (pF)")
    print(f"   retardo equivalente       {por_tramo(f, 1e12 * tiempo, '{:6.1f}')}  (ps)")
    print("   Solo es fiable donde la calibración del firmware vale (por encima de 100 MHz con la que estaba\n"
          "   cargada). El desfase mezcla la capacidad de la apertura con la inductancia del cortocircuito:\n"
          "   1 nH en el corto equivale a 0,4 pF. La capacidad es, por tanto, una cota superior.")

    figuras.mkdir(parents=True, exist_ok=True)
    ruta = figuras / f"{CAMPANA}_{sesion}.png"
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": REJILLA, "text.color": TINTA,
                         "axes.labelcolor": TINTA_2, "xtick.color": TINTA_2, "ytick.color": TINTA_2})
    fig, eje = plt.subplots(figsize=(8, 4.6), facecolor=FONDO)
    eje.set_facecolor(FONDO)
    eje.loglog(f, 100 * ruido, color=TINTA_2, lw=1.0, ls="--", label="ruido de un barrido")
    for m in cortos:
        eje.loglog(f, 100 * dispersion[m], color=COLOR[m], lw=1.3, label=f"corto de {m}, entre colocaciones")
    eje.set_title("Repetibilidad del cortocircuito, en % de la distancia entre aire y corto", loc="left",
                  fontsize=10, color=TINTA)
    eje.set_xlabel("Frecuencia (Hz)")
    eje.grid(True, which="major", color=REJILLA, lw=0.6)
    eje.spines[["top", "right"]].set_visible(False)
    eje.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150, facecolor=FONDO)
    plt.close(fig)
    print(f"\nFigura: {ruta}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--colocaciones", type=int, default=6, help="veces que se coloca cada material")
    ap.add_argument("--barridos", type=int, default=2, help="barridos por colocación")
    ap.add_argument("--materiales", nargs="+", default=list(MATERIALES), choices=list(MATERIALES))
    ap.add_argument("--sonda", default=None, help="identificador de la sonda (hardware/README.md)")
    ap.add_argument("--puerto", default=None)
    ap.add_argument("--reanalizar", metavar="ID", help="analiza una tanda ya guardada, sin medir")
    ap.add_argument("--simulado", action="store_true")
    args = ap.parse_args()

    if args.reanalizar:
        analizar(*cargar_tanda(args.reanalizar, RAW), args.reanalizar, FIGURAS)
        return
    if args.colocaciones < 3 or args.barridos < 2:
        ap.error("hacen falta al menos 3 colocaciones y 2 barridos por colocación")

    sesion = "corto_" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    temporal = Path(tempfile.mkdtemp(prefix="piloto_corto_")) if args.simulado else None
    raw, figuras = (temporal / "raw", temporal) if temporal else (RAW, FIGURAS)
    vna = SondaConCortoImperfecto() if args.simulado else conectar(args.puerto)
    cuenta = {}

    def serie(muestra, colocacion):
        for _ in range(args.barridos):
            cuenta[muestra] = cuenta.get(muestra, 0) + 1
            medida = Medida(campana=CAMPANA, muestra=muestra, repeticion=cuenta[muestra], sonda_id=args.sonda,
                            cal_sonda_id=sesion, notas=f"colocación {colocacion}")
            medir(vna, medida, raiz=raw)

    try:
        if not args.simulado:
            print(f"Calibración del firmware: {calibracion_firmware(vna)} (no la cambies durante la prueba)")
        total = args.colocaciones * len(args.materiales)
        print(f"Tanda {sesion}: {args.colocaciones} colocaciones de cada material, {args.barridos} barridos cada vez.")
        print("Presiona el cortocircuito contra toda la cara y no lo sueltes mientras dura la medida.\n")
        paso = 0
        for material in args.materiales:
            for i in range(1, args.colocaciones + 1):
                paso += 1
                if args.simulado:
                    vna.colocar(None)
                else:
                    esperar_intro(f"[{paso}/{total}] Sonda al aire, limpia y sin nada cerca. Pulsa Intro… ")
                serie("aire", paso)
                if args.simulado:
                    vna.colocar(material)
                else:
                    esperar_intro(f"[{paso}/{total}] Coloca {MATERIALES[material]} (colocación {i}) y, con ella ya "
                                  "presionada, pulsa Intro… ")
                serie(f"corto_{material}", i)
                print(f"   {material} {i}/{args.colocaciones}: hecho")
    finally:
        if not args.simulado:
            desconectar(vna)

    analizar(*cargar_tanda(sesion, raw), sesion, figuras)


if __name__ == "__main__":
    main()
