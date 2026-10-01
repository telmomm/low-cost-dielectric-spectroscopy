"""Guardado de cada barrido como Touchstone (.s1p) en bruto más un .json con los metadatos.

El esquema de metadatos está descrito en data/README.md. Los campos sin valor se guardan como
null: un metadato ausente tiene que verse, no rellenarse por defecto.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np

from .paths import RAW


@dataclass
class Medida:
    campana: str  # p. ej. "piloto_deriva", "art1_liquidos"
    muestra: str  # p. ej. "aire", "corto", "agua", "metanol", "nacl_0p5"
    repeticion: int = 1
    temp_muestra_c: Optional[float] = None
    temp_ambiente_c: Optional[float] = None
    operador: Optional[str] = None
    cal_sol_id: Optional[str] = None  # identificador de la calibración SOL en uso
    cal_sonda_id: Optional[str] = None  # identificador de la terna aire/corto/agua asociada
    sonda_id: Optional[str] = None
    vna_serie: Optional[str] = None
    vna_firmware: Optional[str] = None
    promediado: Optional[int] = None
    minutos_desde_encendido: Optional[float] = None
    fuerza_contacto_n: Optional[float] = None  # solo muestras sólidas
    notas: str = ""
    timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )


def guardar_medida(f_hz, s11, medida, raiz=RAW, z0=50.0, extra=None):
    """Escribe <raiz>/<campaña>/<fecha>/<timestamp>_<muestra>_rNN.s1p y su .json. Devuelve la ruta del .s1p.

    `extra` son campos adicionales para el .json (p. ej. el resumen de validación).
    """
    f_hz = np.asarray(f_hz, dtype=float)
    s11 = np.asarray(s11, dtype=complex)
    if f_hz.shape != s11.shape:
        raise ValueError("f_hz y s11 deben tener la misma longitud")

    carpeta = Path(raiz) / medida.campana / medida.timestamp_utc[:8]
    carpeta.mkdir(parents=True, exist_ok=True)
    base = carpeta / f"{medida.timestamp_utc}_{medida.muestra}_r{medida.repeticion:02d}"
    s1p, meta = base.with_suffix(".s1p"), base.with_suffix(".json")
    if s1p.exists():
        raise FileExistsError(f"{s1p} ya existe: los datos en bruto no se sobrescriben")

    with open(s1p, "w") as fh:
        fh.write(f"! {medida.campana} / {medida.muestra} / r{medida.repeticion:02d}\n")
        fh.write(f"# HZ S RI R {z0:g}\n")
        for f, s in zip(f_hz, s11):
            fh.write(f"{f:.1f} {s.real:.9e} {s.imag:.9e}\n")

    info = asdict(medida)
    info.update(n_puntos=int(f_hz.size), f_inicio_hz=float(f_hz[0]), f_fin_hz=float(f_hz[-1]))
    info.update(extra or {})
    meta.write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n")
    return s1p


def cargar_medida(ruta_s1p):
    """Lee un barrido guardado por `guardar_medida`. Devuelve (f_hz, s11, metadatos)."""
    ruta_s1p = Path(ruta_s1p)
    datos = np.loadtxt(ruta_s1p, comments=("!", "#"))
    meta = json.loads(ruta_s1p.with_suffix(".json").read_text())
    return datos[:, 0], datos[:, 1] + 1j * datos[:, 2], meta
