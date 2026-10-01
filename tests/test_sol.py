import numpy as np
import pytest

from lcds.sol import corregir, promediar, terminos_error

F = np.linspace(1e6, 3e9, 51)
ED = 0.05 - 0.02j + 0 * F
ER = 0.8 * np.exp(-1j * 2 * np.pi * F * 1.5e-9)
ES = 0.1 + 0.07j + 0 * F


def medido(gamma):
    return (ED + ER * gamma) / (1 - ES * gamma)


def test_recupera_los_terminos_de_error_y_corrige():
    ed, er, es = terminos_error(medido(1), medido(-1), medido(0))
    np.testing.assert_allclose(ed, ED, atol=1e-12)
    np.testing.assert_allclose(er, ER, atol=1e-12)
    np.testing.assert_allclose(es, ES, atol=1e-12)

    gamma = 0.6 * np.exp(-1j * 2 * np.pi * F * 0.3e-9)
    np.testing.assert_allclose(corregir(medido(gamma), ed, er, es), gamma, atol=1e-12)


def test_promediar_da_media_e_incertidumbre_por_partes():
    rng = np.random.default_rng(0)
    trazas = 0.5 + 0.2j + rng.normal(0, 1e-3, (200, F.size)) + 1j * rng.normal(0, 4e-3, (200, F.size))
    media, u = promediar(trazas)
    assert np.mean(media).real == pytest.approx(0.5, abs=1e-4)
    assert np.mean(u.real) == pytest.approx(1e-3, rel=0.05)
    assert np.mean(u.imag) == pytest.approx(4e-3, rel=0.05)


def test_promediar_exige_repeticiones():
    with pytest.raises(ValueError):
        promediar(np.ones((1, F.size)))
