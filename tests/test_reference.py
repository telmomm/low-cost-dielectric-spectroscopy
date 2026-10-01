import numpy as np
import pytest

from lcds.reference import conductivity, debye, water, water_params


def test_agua_a_25_grados():
    eps_s, eps_inf, tau = water_params(25.0)
    assert eps_s == pytest.approx(78.4, abs=0.1)
    assert tau == pytest.approx(8.27e-12, rel=0.01)
    assert 4.5 < eps_inf < 5.5


def test_agua_limite_estatico_y_signo():
    eps = water(np.array([1e6, 1e9]), 25.0)
    assert eps[0].real == pytest.approx(78.4, abs=0.1)
    assert np.all(eps.imag < 0)  # convenio eps' - j·eps''


def test_la_permitividad_estatica_baja_con_la_temperatura():
    assert water_params(37.0)[0] < water_params(20.0)[0]


def test_conductividad_ionica_a_baja_frecuencia():
    f = np.array([1e5])
    eps = debye(f, eps_s=78.0, eps_inf=5.0, tau_s=8e-12, sigma_s_m=1.0)
    assert conductivity(f, eps)[0] == pytest.approx(1.0, rel=1e-3)
