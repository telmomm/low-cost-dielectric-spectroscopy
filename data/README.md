# Datos

```
raw/<campaña>/<AAAAMMDD>/<AAAAMMDDTHHMMSSZ>_<muestra>_rNN.s1p   barrido en bruto (Touchstone, RI, 50 Ω)
raw/<campaña>/<AAAAMMDD>/<AAAAMMDDTHHMMSSZ>_<muestra>_rNN.json  metadatos de ese barrido
processed/                                                      derivados (no se versionan)
referencia/                                                     tablas de permitividad de referencia, con fuente
```

Los archivos de `raw/` los escribe `lcds.metadata.guardar_medida`, que se niega a sobrescribir.
Lo que se guarda es el S11 tal como lo entrega el equipo por USB: ya corregido por la calibración SOL
cargada en el firmware y sin ninguna corrección por software. La conversión a ε* se hace siempre
después, desde estos archivos.

## Campañas

| Carpeta | Contenido |
|---|---|
| `cadena_minima` | primeras ternas aire / corto / agua (fase 2) |
| `piloto_deriva`, `piloto_vida_calibracion`, `piloto_rango_util`, `piloto_ruido`, `piloto_cable` | fase 3 |
| `art1_liquidos` | campaña del Artículo 1 |
| `art2_tejidos` | campaña del Artículo 2 |

## Nombres de muestra

`aire`, `corto`, `agua`, `metanol`, `etanol`, `nacl_0p1`, `nacl_0p5`, `nacl_1p0` (porcentaje en masa,
con `p` en lugar de la coma). Si se miden los patrones SOL como comprobación, se guardan como una muestra más (`sol_abierto`,
`sol_corto`, `sol_carga`).

## Metadatos

| Campo | Significado |
|---|---|
| `campana`, `muestra`, `repeticion` | identifican el barrido |
| `timestamp_utc` | instante de la medida |
| `temp_muestra_c`, `temp_ambiente_c` | temperaturas en °C |
| `operador` | quién mide |
| `cal_sol_id` | calibración SOL cargada en el firmware durante el barrido (cambia en cada recalibración del equipo) |
| `cal_sonda_id` | terna aire / corto / agua con la que se convierte este barrido |
| `sonda_id`, `vna_serie`, `vna_firmware` | identificación del hardware |
| `promediado`, `n_puntos`, `f_inicio_hz`, `f_fin_hz` | configuración del barrido |
| `minutos_desde_encendido` | para los análisis de deriva |
| `fuerza_contacto_n` | solo muestras sólidas (Artículo 2) |
| `notas` | incidencias y, si procede, motivo de rechazo |
| `validacion` | estado de cada regla de rfmeasurement para ese barrido (`pass`, `warning`, `fail`…) |
| `procedencia` | registro de trazabilidad de la adquisición (`record_id`, versiones de software, tramos del barrido) |

Los resultados derivados guardan su cadena de registros en un `*.procedencia.json` junto al resultado;
`lcds.provenance.cargar_grafo` reconstruye con ellos el camino de una cifra hasta sus barridos en bruto.

Un campo sin valor se guarda como `null`. El Artículo 2 añadirá los campos de tejido (especie, pieza,
localización, tiempo post mortem), siguiendo la guía de Farrugia et al. (2024).
