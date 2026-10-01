import numpy as np

from lcds.acquisition import medir
from lcds.metadata import Medida, cargar_medida
from lcds.provenance import a_dict, cargar_grafo, desde_dict, guardar_registros, registrar
from test_acquisition import VNAFalso


def test_registro_ida_y_vuelta():
    r = registrar("corregir_sol", entradas=("a", "b"), parametros={"cal_sol_id": "sol01"})
    assert desde_dict(a_dict(r)) == r
    assert "lcds" in r.software_version and "rfmeasurement" in r.software_version


def test_un_resultado_se_sigue_hasta_sus_barridos(tmp_path):
    raw, derivados = tmp_path / "raw", tmp_path / "processed"
    derivados.mkdir()
    ids = []
    for i, muestra in enumerate(("corto", "aire", "agua", "metanol")):
        medida = Medida(campana="prueba", muestra=muestra, timestamp_utc=f"20261001T10000{i}Z")
        ruta, _ = medir(VNAFalso(), medida, segmentos=((1e6, 10e6),), n_puntos=11, raiz=raw)
        f, s11, meta = cargar_medida(ruta)
        assert f.size == s11.size == 11 and np.iscomplexobj(s11)
        ids.append(meta["procedencia"]["record_id"])

    calibracion = registrar("calibrar_sonda", entradas=ids[:3])
    permitividad = registrar("convertir_a_permitividad", entradas=(ids[3], calibracion.record_id))
    guardar_registros([calibracion, permitividad], derivados / "metanol.procedencia.json")

    grafo = cargar_grafo(raw, derivados)
    assert set(grafo.ancestors(permitividad.record_id)) == {*ids, calibracion.record_id}
    assert grafo.external_sources == ()
    assert grafo.topological_order()[-1] == permitividad.record_id
