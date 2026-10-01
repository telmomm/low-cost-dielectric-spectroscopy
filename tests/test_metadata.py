import json

import numpy as np
import pytest

from lcds.metadata import Medida, guardar_medida


def test_guarda_s1p_y_json(tmp_path):
    f = np.linspace(1e6, 3e9, 11)
    s11 = np.exp(-1j * np.linspace(0, 1, 11))
    medida = Medida(campana="prueba", muestra="agua", temp_muestra_c=25.1)

    ruta = guardar_medida(f, s11, medida, raiz=tmp_path)

    datos = np.loadtxt(ruta, comments=("!", "#"))
    np.testing.assert_allclose(datos[:, 1] + 1j * datos[:, 2], s11, rtol=1e-8)

    meta = json.loads(ruta.with_suffix(".json").read_text())
    assert meta["temp_muestra_c"] == 25.1
    assert meta["operador"] is None
    assert meta["n_puntos"] == 11

    with pytest.raises(FileExistsError):
        guardar_medida(f, s11, medida, raiz=tmp_path)
