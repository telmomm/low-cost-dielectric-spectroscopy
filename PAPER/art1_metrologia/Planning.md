# Planning — Artículo 1: caracterización metrológica

Título provisional: *Metrological characterization of a low-cost vector network analyzer for open-ended
coaxial probe dielectric spectroscopy of biological materials*

Diseño completo en [../../PROTOCOLO.md](../../PROTOCOLO.md). Marco de reporte: GUM (JCGM 100 y 101).

## Enunciado de novedad

*Primer presupuesto de incertidumbre por fuentes (GUM y Monte Carlo) de un sistema NanoVNA con sonda
coaxial de extremo abierto para materiales biológicos, con la banda útil derivada de ese presupuesto y
con hardware, datos, código y trazabilidad abiertos.*

Puerta G0 superada de forma provisional el 1 de octubre de 2026
([../../docs/SOTA/README.md](../../docs/SOTA/README.md), sección 0). Frente a quién hay que defenderlo:

| Trabajo | Qué hace | Qué deja sin hacer |
|---|---|---|
| Linha 2025 (*IEEE TIM*) | pocketVNA en tejido ex vivo; MAPE frente a un sistema comercial | Error sobre datos filtrados y ajustados; sin fuentes separadas; vida de la calibración sin cuantificar |
| Małek 2026 (*IEEE TMTT*) | NanoVNA V2.2 con sensor planar; incertidumbre de tipo A | Dos componentes; sin tipo B ni Monte Carlo; no es sonda coaxial ni material biológico |
| González-Teruel 2022 | nanoVNA-H con sonda coaxial en suelos | Error frente a referencia solo hasta 500 MHz; otro hardware |
| Arias-Rodríguez 2025 (*Sensors*) | Sonda SMA barata, tres modelos, reproducibilidad | El VNA no es de bajo coste; sin presupuesto |

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
