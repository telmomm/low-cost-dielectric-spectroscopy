"""Modelos de permitividad de los líquidos de referencia.

Convenio de todo el paquete: eps = eps' - j·eps'' (eps'' > 0 para un material con pérdidas).

Solo está implementada el agua. Los parámetros de metanol, etanol y disoluciones de NaCl se
añadirán cuando se hayan comprobado contra la fuente original (ver ROADMAP, fase 1): no se
introducen valores de memoria.
"""

import numpy as np

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

    Ajuste válido aproximadamente entre 0 y 50 °C. A 25 °C da eps_s = 78,4 y tau = 8,27 ps.
    PENDIENTE: comprobar los coeficientes contra el artículo original antes de la campaña.
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
