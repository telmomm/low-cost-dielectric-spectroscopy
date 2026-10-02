# Espectroscopía dieléctrica de bajo coste para aplicaciones biomédicas

Línea de investigación que cuantifica con qué incertidumbre un NanoVNA-F V2 con una sonda coaxial de
extremo abierto mide la permitividad de materiales biológicos, y si esa incertidumbre basta para
distinguir tejidos. Tres artículos encadenados: caracterización metrológica, tejido ex vivo y
aplicación clínica.

- Planteamiento de la línea: **[linea_investigacion_nanovna_biomedico.md](linea_investigacion_nanovna_biomedico.md)**
- Pasos, fechas y puertas de decisión: **[ROADMAP.md](ROADMAP.md)**
- Diseño experimental del Artículo 1: **[PROTOCOLO.md](PROTOCOLO.md)**
- Estado del arte y hueco: **[docs/SOTA/README.md](docs/SOTA/README.md)**

## Estructura

```
docs/
  SOTA/            informes de partida (PDF, no se versionan), síntesis y matriz de literatura
  DECISIONES.md    registro de decisiones y de puertas go/no-go
  cuaderno/        una entrada por sesión de laboratorio
hardware/          sonda, soporte, lista de materiales e identificación del equipo
src/lcds/
  reference.py     modelos de los líquidos de referencia (agua de Kaatze; el resto, tras verificar)
  probe.py         conversión Γ → ε* con el modelo capacitivo (bilineal, tres patrones)
  metadata.py      guardado de cada barrido como .s1p en bruto + .json de metadatos
  acquisition.py   barrido con el NanoVNA (pynanovna), contexto, validación y registro de trazabilidad
  sol.py           SOL por software (formulación de nanovna-calibration); auxiliar, fuera de la cadena principal
  uncertainty.py   modelo de medida de ε′ y σ, Monte Carlo, presupuesto por fuentes y paquete reproducible
  provenance.py    registros de trazabilidad y grafo de una medida a sus barridos en bruto
  paths.py         rutas del repositorio
tests/             pruebas del paquete con datos sintéticos
scripts/           se lanzan a mano con el equipo conectado; todos admiten --simulado
  prueba_sol.py    patrones SOL y corrección por software, con comprobación
  prueba_saltos.py lectura con y sin pausar el barrido del equipo
  prueba_saltos_puntos.py  tramos de 101 y de 51 puntos: ¿los saltos van con el punto o con la frecuencia?
  piloto_deriva.py deriva tras calibrar, con el corto conectado y sin sonda
  medir_sonda.py   terna de la sonda y líquidos: de los .s1p a ε′ y σ con incertidumbre
notebooks/         00 → …, se ejecutan en orden (ver notebooks/README.md)
data/
  raw/             .s1p + .json, inmutables y versionados (serán el dataset abierto)
  processed/       derivados, se regeneran con los notebooks
  referencia/      tablas de permitividad de referencia con su fuente
resultados/        tablas y figuras
PAPER/
  art1_metrologia/ Planning.md, diagrams/ y, al elegir revista, v1/ con el manuscrito LaTeX
  art2_tejidos/    Planning.md
  art3_clinico/    Planning.md
```

## Librerías en las que se apoya

| Librería | Papel |
|---|---|
| [pynanovna](https://pypi.org/project/pynanovna/) | Comunicación USB con el NanoVNA-F V2 |
| [rfmeasurement](https://github.com/telmomm/rfmeasurement) | Contexto de la medida, validación de cada barrido, propagación de incertidumbre, presupuesto, trazabilidad e informes reproducibles (≥ 0.2.0) |
| [scikit-rf](https://scikit-rf.readthedocs.io/) | Redes y Touchstone |

`lcds` solo añade lo específico de la sonda coaxial. La comunicación y el uso de
rfmeasurement siguen el proyecto [nanovna-calibration](https://github.com/telmomm/nanovna-calibration).
La adquisición está probada con un equipo simulado, no todavía con el NanoVNA conectado.

Cada revisión de un manuscrito crea una carpeta nueva (`v2/`, `v3/`…) con `main_original.tex`,
`main_revised.tex` (latexdiff) y las respuestas a revisores `Reviewer_N.tex`.

## Puesta en marcha

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -e .
.venv/bin/python -m ipykernel install --user --name lcds --display-name "LCDS (.venv)"
.venv/bin/python -m pytest
```

## Reglas del repositorio

1. Los datos en bruto no se editan ni se sobrescriben. Una medida rechazada se queda, con el motivo en
   sus metadatos.
2. El líquido con el que se calibra la sonda no se usa para validar.
3. Umbrales y criterios de rechazo se escriben en el protocolo antes de la campaña; los cambios
   posteriores se anotan como desviaciones.
4. Ninguna cifra de la bibliografía entra en el código o en el manuscrito sin comprobarla en la fuente
   primaria.
