"""Piloto de deriva sin sonda: ¿cuánto tiempo vale una calibración SOL?

Uso:
    .venv/bin/python scripts/piloto_deriva.py --encendido-min 5      # una hora, desatendido
    .venv/bin/python scripts/piloto_deriva.py --reanalizar deriva_20261002T090000Z
    .venv/bin/python scripts/piloto_deriva.py --simulado

Se miden los tres patrones en el orden carga, abierto y corto, y se calculan los términos de
error. El corto se queda conectado, sin tocar nada, y el equipo lo barre cada minuto. Cada
barrido se corrige con los términos del principio: lo que se aparte de -1 es deriva del equipo.

Se usa el corto porque refleja toda la señal, como hará la sonda: es el caso desfavorable.
`--encendido-min` son los minutos que llevaba encendido el equipo al empezar; con un valor
pequeño el piloto mide también el calentamiento. Ctrl+C lo detiene antes y analiza lo que haya.
"""

import argparse
import glob
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from lcds.acquisition import SEGMENTOS, calibracion_firmware, conectar, desconectar, medir
from lcds.metadata import Medida, cargar_medida
from lcds.paths import FIGURAS, PROCESSED, RAW
from lcds.provenance import guardar_registros, registrar
from lcds.sol import combinar, corregir, incoherentes, terminos_error
from prueba_sol import FONDO, REJILLA, TINTA, TINTA_2, VNASimulado, db, esperar_intro

CAMPANA = "piloto_deriva"
ORDEN = ("carga", "abierto", "corto")  # el corto, el último: se queda puesto para la serie
IDEAL = {"abierto": 1 + 0j, "corto": -1 + 0j, "carga": 0j}
RAMPA = ("#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b")  # un tono, de baja a alta frecuencia
UMBRALES_DB = (-50, -40, -30)


class VNAConDeriva(VNASimulado):
    """Equipo ficticio cuya fase y ganancia se van desplazando con cada barrido."""

    def __init__(self):
        super().__init__()
        self.barridos = 0

    def sweep(self):
        self.barridos += 1
        s11, s21, f = super().sweep()
        t = self.barridos / 5  # cinco tramos por barrido completo
        deriva = (1 + 2e-4 * t) * np.exp(1j * 2e-4 * t * np.asarray(f) / 1e9)
        return list(np.asarray(s11) * deriva), s21, f


def nombre_tramo(a, b):
    return f"{a / 1e6:g}–{b / 1e6:g} MHz"


def cargar_tanda(cal_id, raw):
    """Barridos de una tanda guardada, separados en patrones de calibración y serie de deriva."""
    patrones, serie = {}, []
    for ruta in sorted(glob.glob(str(raw / CAMPANA / "*" / "*.s1p"))):
        f, s11, meta = cargar_medida(ruta)
        if meta["cal_sol_id"] != cal_id:
            continue
        if meta["muestra"].startswith("sol_"):
            patrones.setdefault(meta["muestra"][4:], []).append((s11, meta))
        else:
            serie.append((s11, meta))
    if not serie:
        raise SystemExit(f"No hay barridos de la tanda {cal_id} en {raw / CAMPANA}")
    return f, patrones, serie


def analizar(f, patrones, serie, cal_id, processed, figuras):
    tramos = [(f >= a) & (f <= b) for a, b in SEGMENTOS]

    # Un barrido tarda unos 24 s y recorre los tramos uno a uno: si el patrón se cambió con la
    # medida en marcha, una repetición puede ser buena en unos tramos y no en otros. Se compara
    # cada tramo con el de la última repetición, que es la que seguro se tomó con el patrón puesto.
    medias = {}
    for p in ORDEN:
        todas = np.array([s for s, _ in patrones[p]])
        medias[p] = np.empty(f.size, dtype=complex)
        for (a, b), k in zip(SEGMENTOS, tramos):
            malas = incoherentes(todas[:, k], referencia=todas[-1, k])
            if malas:
                print(f"AVISO: {p}, {nombre_tramo(a, b)}: se descartan las repeticiones "
                      f"{[i + 1 for i in malas]} (el patrón aún no estaba puesto)")
            medias[p][k] = combinar(np.delete(todas[:, k], malas, axis=0))
    ed, er, es = terminos_error(*(medias[p] for p in ("abierto", "corto", "carga")))

    def instante(meta):
        return datetime.strptime(meta["timestamp_utc"], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)

    t0 = instante(patrones["corto"][-1][1])  # la calibración acaba con el último barrido del corto
    minutos = np.array([(instante(m) - t0).total_seconds() / 60 for _, m in serie])
    corregido = np.array([corregir(s, ed, er, es) for s, _ in serie])
    error = np.abs(corregido - IDEAL["corto"])
    fase = np.degrees(np.angle(-corregido))  # 0° si no hay deriva
    modulo = np.abs(corregido) - 1

    # Suelo: diferencia entre barridos consecutivos de la serie, es decir, la repetibilidad a un minuto
    suelo = np.abs(np.diff(corregido, axis=0)) / np.sqrt(2)

    curva = np.array([[np.median(error[i, k]) for k in tramos] for i in range(len(serie))])  # (tiempo, tramo)

    print(f"\nTanda {cal_id}: {len(serie)} barridos a lo largo de {minutos[-1]:.0f} min")
    encendido = serie[0][1].get("minutos_desde_encendido")
    if encendido is not None:
        print(f"El equipo llevaba {encendido:.0f} min encendido al empezar la serie")
    print("\nError mediano del corto corregido, |Γ − (−1)| en dB, por tramo")
    marcas = sorted({0, len(serie) // 4, len(serie) // 2, 3 * len(serie) // 4, len(serie) - 1})
    cabecera = "  tramo                 suelo  " + "  ".join(f"{minutos[i]:4.0f}min" for i in marcas)
    print(cabecera)
    for j, (a, b) in enumerate(SEGMENTOS):
        print(f"  {nombre_tramo(a, b):20s} {db(np.median(suelo[:, tramos[j]])):5.0f}  "
              + "  ".join(f"{db(curva[i, j]):7.0f}" for i in marcas))

    print("\nMinutos hasta superar cada nivel de error (mediana del tramo); «—» si no se alcanza")
    print("  tramo               " + "  ".join(f"{u:>7d} dB" for u in UMBRALES_DB))
    for j, (a, b) in enumerate(SEGMENTOS):
        celdas = []
        for u in UMBRALES_DB:
            sobre = np.flatnonzero(db(curva[:, j]) > u)
            celdas.append(f"{minutos[sobre[0]]:7.0f}   " if sobre.size else "      —   ")
        print(f"  {nombre_tramo(a, b):20s}" + "  ".join(celdas))

    print("\nAl final de la serie: cambio de módulo y de fase del corto corregido (mediana por tramo)")
    for j, (a, b) in enumerate(SEGMENTOS):
        print(f"  {nombre_tramo(a, b):20s} módulo {100 * np.median(modulo[-1, tramos[j]]):+6.2f} %   "
              f"fase {np.median(fase[-1, tramos[j]]):+6.2f}°")

    carpeta = processed / CAMPANA
    carpeta.mkdir(parents=True, exist_ok=True)
    np.savez(carpeta / f"{cal_id}_deriva.npz", f_hz=f, minutos=minutos, corregido=corregido, ed=ed, er=er, es=es)
    calibracion = registrar("calcular_terminos_sol", parametros={"cal_sol_id": cal_id, "patrones": "ideales"},
                            entradas=[m["procedencia"]["record_id"] for p in ORDEN for _, m in patrones[p]])
    deriva = registrar("analizar_deriva", parametros={"cal_sol_id": cal_id, "patron": "corto"},
                       entradas=[calibracion.record_id] + [m["procedencia"]["record_id"] for _, m in serie])
    guardar_registros([calibracion, deriva], carpeta / f"{cal_id}_deriva.procedencia.json")

    figuras.mkdir(parents=True, exist_ok=True)
    ruta = figuras / f"{CAMPANA}_{cal_id}.png"
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": REJILLA, "text.color": TINTA,
                         "axes.labelcolor": TINTA_2, "xtick.color": TINTA_2, "ytick.color": TINTA_2})
    fig, eje = plt.subplots(figsize=(8, 4.6), facecolor=FONDO)
    eje.set_facecolor(FONDO)
    for j, (a, b) in enumerate(SEGMENTOS):
        eje.plot(minutos, db(curva[:, j]), color=RAMPA[j], lw=1.6, label=nombre_tramo(a, b))
    eje.set_title("Deriva tras calibrar: error mediano del corto corregido, |Γ − (−1)| (dB)",
                  loc="left", fontsize=10, color=TINTA)
    eje.set_xlabel("Minutos desde la calibración")
    eje.grid(True, color=REJILLA, lw=0.6)
    eje.spines[["top", "right"]].set_visible(False)
    eje.legend(frameon=False, title="Tramo de frecuencia", fontsize=8, title_fontsize=8,
               loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig.tight_layout()
    fig.savefig(ruta, dpi=150, facecolor=FONDO)
    plt.close(fig)
    print(f"\nResultados: {carpeta / (cal_id + '_deriva.npz')}\nFigura:     {ruta}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--duracion", type=float, default=60, help="minutos de la serie")
    ap.add_argument("--intervalo", type=float, default=60, help="segundos entre barridos")
    ap.add_argument("--repeticiones", type=int, default=3, help="barridos por patrón al calibrar")
    ap.add_argument("--encendido-min", type=float, default=None,
                    help="minutos que llevaba encendido el equipo al empezar")
    ap.add_argument("--pausar", action="store_true", help="pausar el barrido continuo del equipo al medir")
    ap.add_argument("--puerto", default=None)
    ap.add_argument("--reanalizar", metavar="ID", help="analiza una tanda ya guardada, sin medir")
    ap.add_argument("--simulado", action="store_true")
    args = ap.parse_args()

    if args.reanalizar:
        analizar(*cargar_tanda(args.reanalizar, RAW), args.reanalizar, PROCESSED, FIGURAS)
        return

    temporal = Path(tempfile.mkdtemp(prefix="piloto_deriva_")) if args.simulado else None
    raw, processed, figuras = (temporal / "raw", temporal / "processed", temporal) if temporal else (RAW, PROCESSED, FIGURAS)
    cal_id = "deriva_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    inicio = time.monotonic()

    def encendido():
        if args.encendido_min is None:
            return None
        return args.encendido_min + (time.monotonic() - inicio) / 60

    reloj = [datetime.now(timezone.utc)]

    def medida(muestra, repeticion):
        m = Medida(campana=CAMPANA, muestra=muestra, repeticion=repeticion, cal_sol_id=cal_id,
                   minutos_desde_encendido=encendido())
        if args.simulado:  # sin esperas reales, el reloj se adelanta un minuto por barrido
            reloj[0] += timedelta(minutes=1)
            m.timestamp_utc = reloj[0].strftime("%Y%m%dT%H%M%SZ")
        return m

    vna = VNAConDeriva() if args.simulado else conectar(args.puerto)
    try:
        if not args.simulado:
            print(f"Calibración del firmware: {calibracion_firmware(vna)}")
        print(f"Tanda {cal_id}. Calibración: {args.repeticiones} barridos por patrón.\n")
        for patron in ORDEN:
            if args.simulado:
                vna.gamma = IDEAL[patron]
            else:
                esperar_intro(f"Conecta el patrón «{patron}» y, con él ya puesto, pulsa Intro… ")
            for i in range(1, args.repeticiones + 1):
                medir(vna, medida(f"sol_{patron}", i), raiz=raw, pausar=args.pausar)
            print(f"  {patron}: hecho")

        n = max(2, int(args.duracion * 60 / max(args.intervalo, 1)) + 1) if not args.simulado else 30
        print(f"\nSerie de deriva: {n} barridos, uno cada {args.intervalo:g} s. No toques el equipo ni el corto.")
        print("Ctrl+C para detenerla antes; se analiza lo que haya.")
        try:
            siguiente = time.monotonic()
            for i in range(1, n + 1):
                if not args.simulado:
                    time.sleep(max(0.0, siguiente - time.monotonic()))
                    siguiente += args.intervalo
                medir(vna, medida("corto_deriva", i), raiz=raw, pausar=args.pausar)
                print(f"  barrido {i}/{n}", end="\r", flush=True)
        except KeyboardInterrupt:
            print("\nSerie detenida a mano.")
    finally:
        if not args.simulado:
            desconectar(vna)

    analizar(*cargar_tanda(cal_id, raw), cal_id, processed, figuras)


if __name__ == "__main__":
    main()
