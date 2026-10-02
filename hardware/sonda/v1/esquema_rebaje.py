"""Dibuja el esquema del rebaje de la sonda v1 (corte longitudinal antes y después, y cara final).

Es un esquema, no un plano: las proporciones son aproximadas y hay que comprobarlas en la pieza.
    .venv/bin/python hardware/sonda/v1/esquema_rebaje.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle

METAL, TUERCA, PTFE, CENTRAL, JUNTA = "#9aa3ad", "#c9cfd6", "#ffffff", "#c9a227", "#d03b3b"
TINTA, TINTA_2, FONDO, CORTE = "#0b0b0b", "#52514e", "#fcfcfb", "#d03b3b"
X_CORTE = 5.5  # el PTFE acaba en x = 6


def simetrico(eje, x, ancho, r0, r1, **estilo):
    """Rectángulo de radio r0..r1, dibujado arriba y abajo del eje (sección de una pieza de revolución)."""
    for signo in (1, -1):
        eje.add_patch(Rectangle((x, signo * r0), ancho, signo * (r1 - r0), **estilo))


def cuerpo_comun(eje, x_fin):
    borde = dict(ec=TINTA, lw=0.8)
    simetrico(eje, -4.5, 4.5, 0.0, 2.6, fc=CENTRAL, alpha=0.35, **borde)   # lado SMA, simplificado
    simetrico(eje, 0, x_fin, 3.6, 5.6, fc=METAL, **borde)                   # cuerpo
    simetrico(eje, 0, x_fin, 1.15, 3.6, fc=PTFE, **borde)                   # PTFE
    eje.add_patch(Rectangle((-4.5, -1.15), 4.5 + x_fin, 2.3, fc=CENTRAL, **borde))  # conductor central


def antes(eje):
    borde = dict(ec=TINTA, lw=0.8)
    cuerpo_comun(eje, 6)
    simetrico(eje, 6, 6, 3.6, 4.1, fc=METAL, hatch="///", **borde)          # manguito ranurado
    eje.add_patch(Rectangle((6, -0.8), 5.0, 1.6, fc=CENTRAL, **borde))      # pin
    eje.add_patch(Polygon([(11, 0.8), (12, 0), (11, -0.8)], fc=CENTRAL, **borde))
    simetrico(eje, 2.5, 10.5, 6.6, 7.8, fc=TUERCA, **borde)                 # tuerca
    simetrico(eje, 2.5, 1.2, 5.6, 6.6, fc=TUERCA, **borde)
    simetrico(eje, 6.1, 0.8, 4.3, 6.5, fc=JUNTA, **borde)                   # junta roja
    eje.plot([X_CORTE, X_CORTE], [-9.2, 9.2], color=CORTE, lw=1.6, ls="--")
    eje.text(X_CORTE, 9.6, "corte", color=CORTE, ha="center", va="bottom", fontsize=9, weight="bold")
    eje.annotate("se quita todo lo que\nqueda a la derecha", (X_CORTE + 0.3, -9.0), (9.3, -11.2),
                 color=CORTE, fontsize=8, ha="center", arrowprops=dict(arrowstyle="->", color=CORTE))
    notas = (("tuerca de acoplamiento", (11.5, 7.2), (15.5, 8.6)), ("junta roja", (6.5, 5.6), (15.5, 6.0)),
             ("manguito ranurado", (10.5, 3.85), (15.5, 3.6)), ("aire", (9, 2.3), (15.5, 1.6)),
             ("pin", (10, 0.3), (15.5, -0.6)), ("PTFE", (3.5, -2.4), (0.5, -8.2)),
             ("conductor central", (1.5, -0.6), (-4.5, -10.0)), ("cuerpo metálico", (2.5, -4.9), (-4.5, -6.6)))
    for texto, punto, sitio in notas:
        eje.annotate(texto, punto, sitio, fontsize=8, color=TINTA, va="center",
                     ha="right" if sitio[0] < 0 else "left", arrowprops=dict(arrowstyle="-", color=TINTA_2, lw=0.6))
    eje.text(-2.2, 3.4, "lado SMA\n(no se toca)", fontsize=8, color=TINTA_2, ha="center")
    eje.set_title("ANTES · corte longitudinal del lado N", loc="left", fontsize=10, color=TINTA)


def despues(eje):
    cuerpo_comun(eje, X_CORTE)
    eje.plot([X_CORTE, X_CORTE], [-5.6, 5.6], color=CORTE, lw=2.2)
    eje.annotate("cara plana:\nlos tres al mismo nivel", (X_CORTE, 4.6), (9.5, 7.6), fontsize=8.5, color=CORTE,
                 weight="bold", ha="left", arrowprops=dict(arrowstyle="->", color=CORTE))
    eje.annotate("aquí va el líquido\n(o el cortocircuito)", (X_CORTE + 0.4, 0), (9.5, 0), fontsize=8, color=TINTA,
                 va="center", arrowprops=dict(arrowstyle="->", color=TINTA_2))
    for texto, punto, sitio in (("PTFE", (3.5, -2.4), (0.5, -8.2)), ("conductor central", (1.5, -0.6), (-4.5, -10.0)),
                                ("cuerpo metálico", (2.5, -4.9), (-4.5, -6.6))):
        eje.annotate(texto, punto, sitio, fontsize=8, color=TINTA, va="center",
                     ha="right" if sitio[0] < 0 else "left", arrowprops=dict(arrowstyle="-", color=TINTA_2, lw=0.6))
    eje.text(-2.2, 3.4, "lado SMA,\nal NanoVNA", fontsize=8, color=TINTA_2, ha="center")
    eje.set_title("DESPUÉS · corte longitudinal", loc="left", fontsize=10, color=TINTA)


def cara(eje):
    for radio, color in ((5.6, METAL), (3.6, PTFE), (1.15, CENTRAL)):
        eje.add_patch(Circle((0, 0), radio, fc=color, ec=TINTA, lw=0.8))
    for texto, punto, sitio in (("cuerpo metálico\n(conductor exterior)", (4.2, 2.2), (7.0, 6.2)),
                                ("PTFE\n(≈ 7 mm de diámetro)", (2.2, -0.9), (7.0, -1.0)),
                                ("conductor central\n(≈ 2 mm)", (0.4, -0.7), (7.0, -6.4))):
        eje.annotate(texto, punto, sitio, fontsize=8, color=TINTA, va="center",
                     arrowprops=dict(arrowstyle="-", color=TINTA_2, lw=0.6))
    eje.set_title("DESPUÉS · la cara, vista de frente", loc="left", fontsize=10, color=TINTA)
    eje.text(0, -8.6, "sin ranuras, sin huecos, sin rebabas", fontsize=8.5, color=CORTE, ha="center", weight="bold")


fig, ejes = plt.subplots(1, 3, figsize=(15, 5.6), facecolor=FONDO, gridspec_kw=dict(width_ratios=[1.35, 1.1, 0.95]))
for eje, dibujo, limites in zip(ejes, (antes, despues, cara), ((-12, 23), (-12, 19), (-7, 15))):
    dibujo(eje)
    eje.set_xlim(*limites)
    eje.set_ylim(-12.5, 11)
    eje.set_aspect("equal")
    eje.axis("off")
fig.text(0.01, 0.01, "Esquema, no a escala: comprobar las medidas en la pieza.", fontsize=8, color=TINTA_2)
fig.tight_layout()
fig.savefig(Path(__file__).with_suffix(".png"), dpi=140, facecolor=FONDO)
