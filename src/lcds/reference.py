"""Modelos de permitividad de los líquidos de referencia.

Convenio de todo el paquete: eps = eps' - j·eps'' (eps'' > 0 para un material con pérdidas).

Fuentes y estado de comprobación de cada modelo: data/referencia/README.md. Las disoluciones de
NaCl no están implementadas: sus coeficientes no se introducen sin haber consultado la fuente.
"""

import numpy as np

from .paths import REFERENCIA

EPS0 = 8.8541878128e-12  # F/m


def debye(f_hz, eps_s, eps_inf, tau_s, sigma_s_m=0.0):
    """Relajación de Debye de un solo polo con conductividad iónica opcional."""
    w = 2 * np.pi * np.asarray(f_hz, dtype=float)
    eps = eps_inf + (eps_s - eps_inf) / (1 + 1j * w * tau_s)
    if sigma_s_m:
        eps = eps - 1j * sigma_s_m / (w * EPS0)
    return eps


def water_params(temp_c):
    """Parámetros de Debye del agua pura en función de la temperatura (Kaatze, 1989).

    Ajuste a medidas entre -4,1 y 60 °C y por debajo de 100 GHz. A 25 °C da eps_s = 78,4 y
    tau = 8,27 ps.
    """
    t_k = temp_c + 273.15
    eps_s = 10 ** (1.94404 - 1.991e-3 * temp_c)
    eps_inf = 5.77 - 2.74e-2 * temp_c
    tau_s = 3.745e-15 * (1 + 7e-5 * (temp_c - 27.5) ** 2) * np.exp(2.2957e3 / t_k)
    return eps_s, eps_inf, tau_s


def water(f_hz, temp_c):
    """Permitividad compleja del agua desionizada a la temperatura dada."""
    return debye(f_hz, *water_params(temp_c))


def conductivity(f_hz, eps):
    """Conductividad equivalente sigma = w·eps0·eps'' en S/m."""
    w = 2 * np.pi * np.asarray(f_hz, dtype=float)
    return -w * EPS0 * np.imag(eps)


def _parametros_npl(liquido, temp_c):
    """Parámetros del informe NPL MAT 23 a `temp_c`, interpolados linealmente entre temperaturas."""
    lineas = (REFERENCIA / f"npl_mat23_{liquido}.csv").read_text().splitlines()
    tabla = np.genfromtxt([l for l in lineas if not l.startswith("#")], delimiter=",", names=True)
    if not tabla["temp_c"][0] <= temp_c <= tabla["temp_c"][-1]:
        raise ValueError(f"{liquido}: {temp_c} °C está fuera del intervalo tabulado (10-50 °C)")
    return {col: float(np.interp(temp_c, tabla["temp_c"], tabla[col])) for col in tabla.dtype.names[1:]}


def methanol(f_hz, temp_c):
    """Permitividad compleja del metanol: Debye simple, NPL Report MAT 23 (Gregory y Clarke, 2012)."""
    p = _parametros_npl("metanol", temp_c)
    f_ghz = np.asarray(f_hz, dtype=float) / 1e9
    return p["eps_inf"] + (p["eps_s"] - p["eps_inf"]) / (1 + 1j * f_ghz / p["fr_ghz"])


def ethanol(f_hz, temp_c):
    """Permitividad compleja del etanol: Debye-Gamma, NPL Report MAT 23. Válido hasta 5 GHz."""
    p = _parametros_npl("etanol", temp_c)
    f_ghz = np.asarray(f_hz, dtype=float) / 1e9
    return p["eps_h"] + (p["eps_s"] - p["eps_h"]) / (1 + 1j * f_ghz / p["fr_ghz"]) - 1j * f_ghz * p["gamma"]
