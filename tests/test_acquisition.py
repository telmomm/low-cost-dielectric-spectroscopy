import json

import numpy as np
import pytest

from lcds.acquisition import a_measurement, barrer, medir
from lcds.metadata import Medida


class VNAFalso:
    """Imita la parte de pynanovna.VNA que usa lcds: set_sweep, sweep e info."""

    def __init__(self, s11=lambda f: 0.9 * np.exp(-1j * 2 * np.pi * f * 1e-9)):
        self.s11 = s11

    def set_sweep(self, inicio, fin, puntos):
        self.f = np.linspace(inicio, fin, puntos)

    def sweep(self):
        return list(self.s11(self.f)), [0j] * self.f.size, list(self.f.astype(int))

    def info(self):
        return {"Serial Number": "SN123", "Version": "0.5.8"}


def test_barrer_une_los_tramos_sin_repetir_frecuencias():
    f, s11 = barrer(VNAFalso(), segmentos=((1e6, 10e6), (10e6, 100e6)), n_puntos=11)
    assert f.size == s11.size == 21  # 10 MHz aparece en los dos tramos y se queda una vez
    assert np.all(np.diff(f) > 0)


def test_a_measurement_lleva_el_contexto():
    medida = Medida(campana="prueba", muestra="agua", temp_muestra_c=25.0, sonda_id="v1")
    f, s11 = barrer(VNAFalso(), segmentos=((1e6, 10e6),), n_puntos=11)
    m = a_measurement(f, s11, medida)
    assert m.data.nports == 1
    assert m.context.dut == "agua"
    assert m.context.temperature_c == 25.0
    assert m.context.fixture == "v1"
    assert m.context.frequency_range_hz == (1e6, 10e6)


def test_medir_guarda_con_validacion_e_identificacion_del_equipo(tmp_path):
    medida = Medida(campana="prueba", muestra="aire")
    ruta, medicion = medir(VNAFalso(), medida, segmentos=((1e6, 10e6),), n_puntos=11, raiz=tmp_path)

    meta = json.loads(ruta.with_suffix(".json").read_text())
    assert meta["vna_serie"] == "SN123"
    assert meta["vna_firmware"] == "0.5.8"
    assert meta["validacion"]["integrity.frequency_grid"] == "pass"
    assert meta["validacion"]["physics.reciprocity"] == "not_applicable"
    assert not medicion.validation.has_failures
    assert meta["procedencia"]["record_id"] == medicion.provenance[0].record_id
    assert meta["procedencia"]["parameters"]["vna_serie"] == "SN123"


def test_un_s11_no_pasivo_se_guarda_anotado(tmp_path):
    medida = Medida(campana="prueba", muestra="corto")
    vna = VNAFalso(s11=lambda f: 1.05 * np.ones_like(f, dtype=complex))
    ruta, _ = medir(vna, medida, segmentos=((1e6, 10e6),), n_puntos=11, raiz=tmp_path)
    assert ruta.exists()
    assert json.loads(ruta.with_suffix(".json").read_text())["validacion"]["physics.passivity"] == "fail"


def test_un_barrido_con_valores_no_finitos_no_se_guarda(tmp_path):
    medida = Medida(campana="prueba", muestra="agua")
    vna = VNAFalso(s11=lambda f: np.full(f.size, np.nan + 0j))
    with pytest.raises(RuntimeError):
        medir(vna, medida, segmentos=((1e6, 10e6),), n_puntos=11, raiz=tmp_path)
    assert not list(tmp_path.rglob("*.s1p"))
