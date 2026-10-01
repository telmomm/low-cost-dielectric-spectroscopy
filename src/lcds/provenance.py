"""Trazabilidad con rfmeasurement: un ProvenanceRecord por operación, enlazados por record_id.

Cada barrido en bruto lleva en su .json el registro de su adquisición. Cada resultado derivado
(términos SOL, calibración de la sonda, permitividad, incertidumbre) crea un registro cuyos
`inputs` son los record_id de los que parte, de modo que cualquier cifra publicada se puede
seguir hasta los .s1p que la produjeron.
"""

import json
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from rfmeasurement.domain import ProvenanceRecord
from rfmeasurement.provenance import ProvenanceGraph
from rfmeasurement.reporting import capture_environment


def versiones():
    """Versiones del software que interviene en una medida, como cadena para el registro."""
    entorno = capture_environment()
    partes = [f"rfmeasurement {entorno.rfmeasurement_version}", f"python {entorno.python_version}"]
    partes += [f"{paquete} {v}" for paquete, v in entorno.dependency_versions.items()]
    for paquete in ("lcds", "pynanovna"):  # lo que rfmeasurement no sigue por su cuenta
        try:
            partes.append(f"{paquete} {version(paquete)}")
        except PackageNotFoundError:
            pass
    return "; ".join(partes)


def registrar(operacion, entradas=(), parametros=None, notas=None):
    """Crea el registro de una operación. `entradas` son record_id o identificadores externos."""
    return ProvenanceRecord(
        operation=operacion,
        software_version=versiones(),
        parameters=dict(parametros or {}),
        inputs=tuple(entradas),
        notes=notas,
    )


def a_dict(registro):
    return {
        "record_id": registro.record_id,
        "operation": registro.operation,
        "software_version": registro.software_version,
        "timestamp": registro.timestamp.isoformat(),
        "parameters": registro.parameters,
        "inputs": list(registro.inputs),
        "notes": registro.notes,
    }


def desde_dict(d):
    return ProvenanceRecord(
        operation=d["operation"],
        software_version=d["software_version"],
        record_id=d["record_id"],
        timestamp=datetime.fromisoformat(d["timestamp"]),
        parameters=d.get("parameters") or {},
        inputs=tuple(d.get("inputs") or ()),
        notes=d.get("notes"),
    )


def guardar_registros(registros, ruta):
    """Guarda la cadena de registros de un resultado derivado junto a ese resultado."""
    Path(ruta).write_text(
        json.dumps([a_dict(r) for r in registros], indent=2, ensure_ascii=False, default=str) + "\n"
    )


def cargar_grafo(*carpetas):
    """Reúne en un grafo todos los registros guardados bajo las carpetas dadas.

    Lee el campo "procedencia" de los .json de las medidas y las listas escritas por
    `guardar_registros` (archivos *.procedencia.json).
    """
    registros = {}
    for carpeta in carpetas:
        for ruta in sorted(Path(carpeta).rglob("*.json")):
            contenido = json.loads(ruta.read_text())
            if isinstance(contenido, dict):
                contenido = [contenido["procedencia"]] if "procedencia" in contenido else []
            for d in contenido:
                registros[d["record_id"]] = desde_dict(d)
    return ProvenanceGraph.from_records(registros.values())
