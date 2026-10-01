"""Rutas del repositorio, para que notebooks y scripts no dependan del directorio de trabajo."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
REFERENCIA = DATA / "referencia"

RESULTADOS = ROOT / "resultados"
FIGURAS = RESULTADOS / "figuras"
