import numpy as np

from lcds.probe import epsilon_bilinear, gamma_capacitive
from lcds.reference import debye, water

F = np.logspace(np.log10(50e3), np.log10(3e9), 201)
C0, CF = 0.02e-12, 0.03e-12


def red_de_error(gamma):
    """Cable y errores residuales entre la apertura y el plano de medida: una bilineal cualquiera."""
    e00, e11, e10e01 = 0.05 - 0.02j, 0.1 + 0.07j, 0.8 * np.exp(-1j * 2 * np.pi * F * 1.5e-9)
    return e00 + e10e01 * gamma / (1 - e11 * gamma)


def test_recupera_un_liquido_no_usado_para_calibrar():
    eps_agua = water(F, 25.0)
    eps_muestra = debye(F, eps_s=33.0, eps_inf=5.0, tau_s=50e-12, sigma_s_m=0.5)  # sintético

    g_corto = red_de_error(-np.ones_like(F, dtype=complex))
    g_aire = red_de_error(gamma_capacitive(F, 1.0, C0, CF))
    g_agua = red_de_error(gamma_capacitive(F, eps_agua, C0, CF))
    g_muestra = red_de_error(gamma_capacitive(F, eps_muestra, C0, CF))

    eps = epsilon_bilinear(g_muestra, g_corto, g_aire, g_agua, eps_agua)
    # Por debajo de ~1 MHz el problema está mal condicionado (Gamma ≈ 1): es una limitación
    # física que la campaña debe caracterizar, no un fallo numérico.
    banda = F > 1e6
    np.testing.assert_allclose(eps[banda], eps_muestra[banda], rtol=1e-6)


def test_devuelve_los_patrones():
    eps_agua = water(F, 25.0)
    g_corto = red_de_error(-np.ones_like(F, dtype=complex))
    g_aire = red_de_error(gamma_capacitive(F, 1.0, C0, CF))
    g_agua = red_de_error(gamma_capacitive(F, eps_agua, C0, CF))

    banda = F > 1e6
    eps = epsilon_bilinear(g_agua, g_corto, g_aire, g_agua, eps_agua)
    np.testing.assert_allclose(eps[banda], eps_agua[banda], rtol=1e-6)
    eps = epsilon_bilinear(g_aire, g_corto, g_aire, g_agua, eps_agua)
    np.testing.assert_allclose(eps[banda], 1.0, atol=1e-6)
