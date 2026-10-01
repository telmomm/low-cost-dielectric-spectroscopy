# Planning — Artículo 1: caracterización metrológica

Título provisional: *Metrological characterization of a low-cost vector network analyzer for open-ended
coaxial probe dielectric spectroscopy of biological materials*

Diseño completo en [../../PROTOCOLO.md](../../PROTOCOLO.md). Marco de reporte: GUM (JCGM 100 y 101).

## Enunciado de novedad

Pendiente de la puerta G0. Borrador: *primer presupuesto de incertidumbre por fuentes de un sistema
NanoVNA + sonda coaxial para materiales biológicos, con el rango útil derivado de él y con hardware,
datos y código abiertos.* Los trabajos frente a los que hay que defenderlo están en
[../../docs/SOTA/README.md](../../docs/SOTA/README.md).

## Revista objetivo

- [ ] Elegir revista → crear `v1/` con `main.tex`, `references.bib`, `assets/` y `Definitions/` (plantilla)

| Candidata | Encaje | A tener en cuenta |
|---|---|---|
| *IEEE Trans. Instrum. Meas.* | Foco metrológico | Publicó el competidor más cercano (Linha 2025): los revisores lo conocerán |
| *Measurement* | Foco metrológico | |
| *HardwareX* | Foco en el instrumento abierto | Exige documentación de fabricación completa |
| *Sensors* | Rápida; concentra buena parte del área | Coste del APC |

## Mapa notebook → manuscrito

| Notebook | Sección | Figuras / tablas |
|---|---|---|
| `01`–`04` (pilotos) | Methods · Measurement protocol | Deriva y vida de la calibración (suplementario) |
| `10_art1_repetibilidad` | Results · Repeatability | Componentes de tipo A |
| `11_art1_temperatura` | Results · Temperature sensitivity | |
| `12_art1_validacion_liquidos` | Results · Validation with reference liquids | Error frente a frecuencia |
| `13_art1_modelos_inversion` | Results · Probe model comparison | |
| `14_art1_presupuesto_incertidumbre` | Results · Uncertainty budget | Tabla del presupuesto; **figura clave** |

Las figuras finales se copian de `resultados/figuras/` a `v1/assets/`.

## Envío

- [ ] Cover Letter
- [ ] Highlights
- [ ] Graphical Abstract (`diagrams/`)
- [ ] Depósito en Zenodo (datos, código, diseño de la sonda) y DOI en el manuscrito
- [ ] Preprint
