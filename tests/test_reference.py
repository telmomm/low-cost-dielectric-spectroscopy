import numpy as np
import pytest

from lcds.reference import conductivity, debye, ethanol, methanol, water, water_params


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


def test_agua_reproduce_la_tabla_de_una_fuente_secundaria():
    # Gezehegn et al. (2021), tabla 1: valores de las ecuaciones de Kaatze. La fila de 23 °C no se
    # usa: su tau (8,50 ps) no sale de las ecuaciones que el propio artículo reproduce (8,72 ps).
    tabla = ((30, 76.61, 4.95, 7.29), (40, 73.18, 4.67, 5.78), (50, 69.90, 4.40, 4.72), (60, 66.77, 4.13, 3.95))
    for temp, eps_s, eps_inf, tau_ps in tabla:
        s, inf, tau = water_params(temp)
        assert s == pytest.approx(eps_s, abs=0.01)
        assert inf == pytest.approx(eps_inf, abs=0.01)
        assert tau * 1e12 == pytest.approx(tau_ps, abs=0.01)


# Valores "best-fit" de la sección 8 del informe NPL MAT 23: (GHz, eps', eps'')
METANOL_25 = ((0.1, 32.63, 0.86), (0.5, 31.99, 4.21), (1.0, 30.17, 7.83), (3.0, 19.73, 13.53), (5.0, 13.23, 12.21))
ETANOL_20 = ((0.1, 24.86, 2.46), (0.5, 19.66, 9.15), (1.0, 12.93, 10.19), (3.0, 5.99, 5.47), (5.0, 5.08, 3.62))


@pytest.mark.parametrize("modelo, temp, tabla", [(methanol, 25, METANOL_25), (ethanol, 20, ETANOL_20)])
def test_alcoholes_reproducen_las_tablas_del_npl(modelo, temp, tabla):
    for f_ghz, real, imag in tabla:
        eps = modelo(f_ghz * 1e9, temp)
        assert eps.real == pytest.approx(real, abs=0.015)
        assert -eps.imag == pytest.approx(imag, abs=0.015)


def test_alcoholes_interpolan_en_temperatura_y_rechazan_fuera_de_rango():
    assert methanol(1e9, 20).real > methanol(1e9, 22.5).real > methanol(1e9, 25).real
    with pytest.raises(ValueError):
        ethanol(1e9, 5)
