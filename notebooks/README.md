# Notebooks

Se ejecutan en orden con el kernel **LCDS (.venv)**. Cada uno lee de `data/raw` y escribe tablas en
`resultados/` y figuras en `resultados/figuras/`, con su número como prefijo. La lógica reutilizable
vive en `src/lcds`, no en los notebooks.

| Notebook | Fase | Contenido |
|---|---|---|
| `00_cadena_minima` | 2 | Primera terna aire / corto / agua y un líquido de comprobación, de .s1p a ε′ y σ |
| `01_piloto_deriva` | 3 | Deriva tras el encendido y tiempo de calentamiento |
| `02_piloto_vida_calibracion` | 3 | Degradación desde la calibración y cadencia de recalibración |
| `03_piloto_rango_util` | 3 | Error frente a frecuencia, margen dinámico y rango útil preliminar |
| `04_piloto_ruido_cable` | 3 | Ruido frente a promediado y puntos; cable fijo frente a flexionado |
| `10_art1_repetibilidad` | 4–5 | Repetibilidad de la medida y de la calibración |
| `11_art1_temperatura` | 4–5 | Sensibilidad térmica |
| `12_art1_validacion_liquidos` | 5 | Error frente a los modelos de referencia |
| `13_art1_modelos_inversion` | 5 | Capacitivo, radiación y línea virtual sobre los mismos datos |
| `14_art1_presupuesto_incertidumbre` | 5 | Presupuesto por fuentes, Monte Carlo y figura clave |
| `20_…` | 7 | Artículo 2 |

Ninguno está creado todavía: cada uno nace con los primeros datos de su fase.
