"""Calibración SOL de un puerto por software, con la formulación de nanovna-calibration.

Modelo:      Gamma_m = (e_d + e_r·Gamma) / (1 - e_s·Gamma)
Corrección:  Gamma   = (Gamma_m - e_d) / (e_r + e_s·Gamma_m)

No forma parte de la cadena principal: el equipo ya entrega el S11 corregido por la calibración
de su firmware. Sirve para estudiar la repetibilidad de la SOL a partir de patrones medidos y
para una segunda corrección por software cuando haga falta mover el plano de referencia.

Por defecto los patrones son ideales (abierto = 1, corto = -1, carga = 0). Esa idealización es
una fuente de incertidumbre de tipo B del presupuesto (PROTOCOLO.md, sección 8).
"""

import numpy as np

PATRONES_IDEALES = (1 + 0j, -1 + 0j, 0 + 0j)  # abierto, corto, carga


def promediar(trazas):
    """Media y desviación típica de varias repeticiones de un mismo patrón o muestra.

    Devuelve (media, u): `u` es complejo, con la desviación típica experimental (ddof=1) de la
    parte real y de la imaginaria por separado, que es lo que necesita lcds.uncertainty.
    """
    trazas = np.asarray(trazas, dtype=complex)
    if trazas.ndim != 2 or trazas.shape[0] < 2:
        raise ValueError("hacen falta al menos dos repeticiones sobre la misma malla de frecuencias")
    return trazas.mean(axis=0), trazas.real.std(axis=0, ddof=1) + 1j * trazas.imag.std(axis=0, ddof=1)


def terminos_error(abierto_m, corto_m, carga_m, patrones=PATRONES_IDEALES):
    """Términos de error (e_d, e_r, e_s) a cada frecuencia a partir de los tres patrones medidos."""
    medidos = np.stack([abierto_m, corto_m, carga_m], axis=-1).astype(complex)  # (n_f, 3)
    reales = np.broadcast_to(np.asarray(patrones, dtype=complex), medidos.shape)
    matriz = np.stack([np.ones_like(medidos), reales, medidos * reales], axis=-1)  # (n_f, 3, 3)
    solucion = np.linalg.solve(matriz, medidos[..., None])[..., 0]
    return solucion[:, 0], solucion[:, 1], solucion[:, 2]


def corregir(gamma_m, ed, er, es):
    """Aplica la corrección SOL a un Gamma medido sobre la misma malla de frecuencias."""
    return (np.asarray(gamma_m) - ed) / (er + es * np.asarray(gamma_m))
