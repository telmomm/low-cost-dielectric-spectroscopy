"""Dibuja cómo colocar la sonda v1 en el líquido: cuánto sumergir y cuánto líquido dejar alrededor.

Es un esquema con distancias de partida, no a escala; el piloto del agua las comprueba.
    .venv/bin/python hardware/sonda/v1/esquema_inmersion.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Rectangle

METAL, PTFE, CENTRAL, AGUA, VASO = "#9aa3ad", "#ffffff", "#c9a227", "#cde2fb", "#52514e"
TINTA, TINTA_2, FONDO, ROJO, VERDE = "#0b0b0b", "#52514e", "#fcfcfb", "#d03b3b", "#0ca30c"


def cota(eje, p0, p1, texto, lado="derecha", color=TINTA):
    eje.annotate("", p0, p1, arrowprops=dict(arrowstyle="<->", color=color, lw=1.0))
    x, y = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    if p0[0] == p1[0]:  # cota vertical
        eje.text(x + (0.8 if lado == "derecha" else -0.8), y, texto, fontsize=8.5, color=color, va="center",
                 ha="left" if lado == "derecha" else "right")
    else:
        eje.text(x, y + 0.9, texto, fontsize=8.5, color=color, ha="center")


def sonda(eje, x0, cara, alto=14):
    borde = dict(ec=TINTA, lw=0.8)
    eje.add_patch(Rectangle((x0 - 6, cara), 12, alto, fc=METAL, **borde))
    eje.add_patch(Rectangle((x0 - 3.6, cara), 7.2, alto, fc=PTFE, **borde))
    eje.add_patch(Rectangle((x0 - 1.1, cara), 2.2, alto, fc=CENTRAL, **borde))
    eje.add_patch(Rectangle((x0 - 3, cara + alto), 6, 6, fc=CENTRAL, alpha=0.4, **borde))  # lado SMA


def bien(eje):
    nivel, fondo, x0 = 30, 0, 0
    eje.add_patch(Rectangle((-22, fondo), 44, nivel, fc=AGUA, ec="none"))
    eje.plot([-22, -22, 22, 22], [nivel + 12, fondo, fondo, nivel + 12], color=VASO, lw=2.5)
    cara = nivel - 5
    sonda(eje, x0, cara)
    for r in (2.5, 5, 8):  # zona donde está el campo, delante de la apertura
        eje.add_patch(Arc((x0, cara), 2 * r, 2 * r, theta1=180, theta2=360, ec="#2a78d6", lw=0.9, ls=":"))
    cota(eje, (9, cara), (9, nivel), "3–5 mm sumergida:\nbasta con cubrir la cara")
    cota(eje, (0, fondo), (0, cara - 8.5), "≥ 20 mm de agua\npor debajo", lado="derecha")
    cota(eje, (-22, 12), (-6, 12), "≥ 15 mm hasta la pared")
    eje.annotate("el campo solo llega a unos\nmilímetros de la cara", (5, cara - 5), (11, cara - 12), fontsize=8, color="#1c5cab",
                 arrowprops=dict(arrowstyle="-", color="#1c5cab", lw=0.6))
    eje.text(0, 47, "lado SMA y equipo: siempre secos", fontsize=8.5, color=ROJO, ha="center", weight="bold")
    eje.text(-21, -4, "vaso de vidrio o plástico, sin metal cerca", fontsize=8.5, color=TINTA_2)
    eje.set_title("BIEN · colocación de partida", loc="left", fontsize=10, color=VERDE)


def mal(eje):
    nivel, fondo = 30, 0
    # 1) burbuja
    eje.add_patch(Rectangle((-22, fondo), 20, nivel, fc=AGUA, ec="none"))
    eje.plot([-22, -22, -2, -2], [nivel + 8, fondo, fondo, nivel + 8], color=VASO, lw=2.5)
    sonda(eje, -12, nivel - 5, alto=12)
    eje.add_patch(Circle((-11, nivel - 6.2), 1.4, fc=FONDO, ec=TINTA, lw=0.8))
    eje.annotate("burbuja en la cara", (-11, nivel - 6.2), (-20, 14), fontsize=8.5, color=ROJO,
                 arrowprops=dict(arrowstyle="->", color=ROJO))
    eje.text(-12, -4, "inclina la sonda al entrar\ny mira la cara desde abajo", fontsize=8, color=TINTA_2, ha="center", va="top")
    # 2) demasiado cerca del fondo o de la pared
    eje.add_patch(Rectangle((4, fondo), 20, 9, fc=AGUA, ec="none"))
    eje.plot([4, 4, 24, 24], [nivel + 8, fondo, fondo, nivel + 8], color=VASO, lw=2.5)
    sonda(eje, 12, 3, alto=12)
    cota(eje, (5.5, 0), (5.5, 3), "fondo\na 3 mm", lado="derecha", color=ROJO)
    eje.text(14, -4, "poco líquido debajo:\nla sonda «ve» el fondo", fontsize=8, color=TINTA_2, ha="center", va="top")
    eje.set_title("MAL · lo que hay que evitar", loc="left", fontsize=10, color=ROJO)


fig, ejes = plt.subplots(1, 2, figsize=(12.5, 6), facecolor=FONDO, gridspec_kw=dict(width_ratios=[1, 1.15]))
for eje, dibujo, xlim in zip(ejes, (bien, mal), ((-26, 34), (-26, 34))):
    dibujo(eje)
    eje.set_xlim(*xlim)
    eje.set_ylim(-11, 52)
    eje.set_aspect("equal")
    eje.axis("off")
fig.text(0.01, 0.01, "Esquema, no a escala. Las distancias son un punto de partida conservador: el piloto del agua las comprueba.",
         fontsize=8, color=TINTA_2)
fig.tight_layout()
fig.savefig(Path(__file__).with_suffix(".png"), dpi=140, facecolor=FONDO)
