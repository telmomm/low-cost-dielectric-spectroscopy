"""Conversión del coeficiente de reflexión a permitividad con el modelo capacitivo (bilineal).

En el modelo capacitivo la admitancia de la apertura es afín en eps, y todo lo que hay entre la
apertura y el plano de medida (sonda, conector, cable, errores residuales del VNA) es una
transformación bilineal. La razón doble se conserva, así que tres patrones bastan y no hace
falta conocer ni la capacidad de la sonda ni la red de error (Marsland y Evans, 1987).

Esta calibración (Gamma -> eps) es independiente de la SOL del VNA (medida bruta -> Gamma) y
tiene su propia contribución en el presupuesto de incertidumbre.
"""

import numpy as np


def epsilon_bilinear(gamma, gamma_short, gamma_open, gamma_ref, eps_ref, eps_open=1.0):
    """Permitividad compleja de la muestra a partir de tres patrones.

    gamma        Gamma medido con la muestra.
    gamma_short  Gamma con la apertura en cortocircuito (admitancia infinita).
    gamma_open   Gamma con la sonda al aire (eps_open).
    gamma_ref    Gamma con el líquido de referencia, de permitividad eps_ref.

    Todos los argumentos son arrays complejos sobre el mismo eje de frecuencias.
    """
    cross = ((gamma - gamma_open) * (gamma_ref - gamma_short)) / (
        (gamma - gamma_short) * (gamma_open - gamma_ref)
    )
    return eps_open + (eps_open - eps_ref) * cross


def gamma_capacitive(f_hz, eps, c0_f, cf_f=0.0, z0=50.0):
    """Gamma ideal en la apertura según el modelo capacitivo: Y = j·w·(C0·eps + Cf).

    Sirve para simular medidas (pruebas y Monte Carlo), no para invertir datos reales.
    """
    w = 2 * np.pi * np.asarray(f_hz, dtype=float)
    y = 1j * w * (c0_f * np.asarray(eps) + cf_f) * z0
    return (1 - y) / (1 + y)
