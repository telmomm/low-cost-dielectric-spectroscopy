import json

import numpy as np
import pytest

from lcds.probe import gamma_capacitive
from lcds.reference import conductivity, debye, water
from lcds.acquisition import medir
from lcds.metadata import Medida
from lcds.provenance import registrar
from lcds.uncertainty import evaluar, informe, metadatos, modelo, modelo_sol
from test_acquisition import VNAFalso

F = 500e6
C0, CF = 0.02e-12, 0.03e-12
EPS_MUESTRA = debye(F, eps_s=33.0, eps_inf=5.0, tau_s=50e-12, sigma_s_m=0.5)  # sintético
GAMMAS = {
    "muestra": complex(gamma_capacitive(F, EPS_MUESTRA, C0, CF)),
    "corto": -1 + 0j,
    "aire": complex(gamma_capacitive(F, 1.0, C0, CF)),
    "agua": complex(gamma_capacitive(F, water(F, 25.0), C0, CF)),
}


def incertidumbres(u_muestra=1e-4, u_resto=1e-4):
    return {k: (u_muestra if k == "muestra" else u_resto) * (1 + 1j) for k in GAMMAS}


def test_valor_central_y_acuerdo_entre_monte_carlo_y_lineal():
    m = modelo(F, GAMMAS, incertidumbres(), temp_agua_c=25.0, u_temp_agua_c=0.1)
    resultado = evaluar(m, n_muestras=4000).resultado
    u_lineal = resultado.provenance[0].parameters["u_lineal"]

    assert resultado.value == pytest.approx(EPS_MUESTRA.real, abs=3 * resultado.standard_uncertainty)
    assert resultado.standard_uncertainty == pytest.approx(u_lineal, rel=0.1)
    inferior, superior = resultado.coverage_interval
    assert inferior < EPS_MUESTRA.real < superior
    assert resultado.coverage_probability == 0.95


def test_el_presupuesto_ordena_las_fuentes():
    m = modelo(F, GAMMAS, incertidumbres(u_muestra=1e-2, u_resto=1e-5), 25.0, 0.01)
    presupuesto = evaluar(m, n_muestras=500).presupuesto
    assert presupuesto.ranked[0].source.name.startswith("gamma_muestra")

    m = modelo(F, GAMMAS, incertidumbres(u_muestra=1e-6, u_resto=1e-6), 25.0, 1.0)
    presupuesto = evaluar(m, n_muestras=500).presupuesto
    assert presupuesto.ranked[0].source.name == "temp_agua"


def test_sigma_y_trazabilidad_del_resultado():
    m = modelo(F, GAMMAS, incertidumbres(), 25.0, 0.1, magnitud="sigma")
    resultado = evaluar(m, n_muestras=2000, entradas=("id_muestra", "id_cal_sonda")).resultado
    assert resultado.unit == "S/m"
    assert resultado.value == pytest.approx(float(conductivity(F, EPS_MUESTRA)), rel=0.02)
    registro = resultado.provenance[0]
    assert registro.inputs == ("id_muestra", "id_cal_sonda")
    assert registro.parameters["semilla"] == 42


def test_paquete_reproducible_de_un_resultado(tmp_path):
    medida = Medida(campana="prueba", muestra="metanol", cal_sol_id="sol01")
    _, medicion = medir(VNAFalso(), medida, segmentos=((1e6, 10e6),), n_puntos=11, raiz=tmp_path)
    id_adquisicion = medicion.provenance[0].record_id
    conversion = registrar("convertir_a_permitividad", entradas=(id_adquisicion,))

    m = modelo(F, GAMMAS, incertidumbres(), 25.0, 0.1)
    ev = evaluar(m, n_muestras=500, entradas=(conversion.record_id,))
    paquete = metadatos(medicion, ev, registros=(conversion,))

    json.dumps(paquete, default=str)  # serializable
    assert paquete["reproducibility_level"] == 4
    assert paquete["context"]["calibration"] == "SOL del firmware (sol01)"
    assert paquete["configuration"]["propagation"]["method"] == "monte_carlo"
    assert [n["operation"] for n in paquete["provenance"]["nodes"]] == [
        "adquirir_barrido", "convertir_a_permitividad", "propagar_incertidumbre",
    ]
    assert paquete["provenance"]["external_sources"] == []
    assert sum(c["porcentaje_varianza"] for c in paquete["presupuesto"]) == pytest.approx(100, abs=0.1)
    assert "eps'" in informe(medicion, ev, registros=(conversion,))


def test_incertidumbre_de_un_gamma_corregido_por_sol():
    ed, er, es = 0.05 - 0.02j, 0.8 * np.exp(-0.7j), 0.1 + 0.07j
    medido = lambda g: (ed + er * g) / (1 - es * g)
    real = 0.3 - 0.4j
    gammas = {"abierto": medido(1), "corto": medido(-1), "carga": medido(0), "medida": medido(real)}
    u = {k: 1e-4 * (1 + 1j) for k in gammas}

    for parte, esperado in (("re", real.real), ("im", real.imag)):
        ev = evaluar(modelo_sol(gammas, u, parte=parte, f_hz=1e9), n_muestras=4000)
        assert ev.resultado.value == pytest.approx(esperado, abs=3 * ev.resultado.standard_uncertainty)
        assert ev.resultado.standard_uncertainty == pytest.approx(ev.lineal.standard_uncertainty, rel=0.1)
        assert 5e-5 < ev.resultado.standard_uncertainty < 1e-3

    # si solo es incierta la medida, es ella la que domina el presupuesto
    u_solo_medida = {k: (1e-3 if k == "medida" else 1e-7) * (1 + 1j) for k in gammas}
    presupuesto = evaluar(modelo_sol(gammas, u_solo_medida), n_muestras=300).presupuesto
    assert presupuesto.ranked[0].source.name.startswith("gamma_medida")
