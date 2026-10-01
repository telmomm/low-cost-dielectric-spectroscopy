# Registro de decisiones

Una fila por decisión que condicione el diseño, el análisis o lo que se afirma en un artículo.
Las puertas del [ROADMAP](../ROADMAP.md) (G0–G3) se registran aquí con la evidencia que las respalda.

## Tomadas

| Fecha | Decisión | Motivo |
|---|---|---|
| 2026-10-01 | Un solo repositorio para los tres artículos, con una carpeta por artículo en `PAPER/` | Comparten instrumento, código y modelo de incertidumbre |
| 2026-10-01 | Los .s1p en bruto se versionan en git | Son pequeños y serán el dataset abierto |
| 2026-10-01 | Se añade la puerta G0 (novedad) antes de fabricar más allá de la sonda v1 | El SOTA muestra validaciones de bajo coste en tejido ya publicadas |
| 2026-10-01 | Vida útil de la calibración y modelo de inversión entran como factores | SOTA: calibración válida unos minutos; el modelo capacitivo es una fuente de error de primer orden |
| 2026-10-01 | Comunicación con el equipo mediante pynanovna; rfmeasurement para contexto, validación e incertidumbre | rfmeasurement deja los drivers fuera de su alcance (`docs/scope.md`); es el reparto ya usado en `nanovna-calibration` |
| 2026-10-01 | La SOL de la cadena de medida es la del firmware; `cal_sol_id` identifica la que estaba cargada | El equipo entrega por USB el S11 ya corregido por la calibración cargada. Se guarda tal cual; `lcds.sol` queda como herramienta auxiliar |
| 2026-10-01 | Regla de pasividad propia para un puerto (`lcds.acquisition.PasividadUnPuerto`) | `PassivityRule` de rfmeasurement 0.1.0 da FAIL en toda red de un puerto: `Network.passivity` de scikit-rf lanza `ValueError` para un puerto e `is_passive` lo convierte en `False`. Sigue igual en la 0.2.0. Temporal, hasta corregirlo en rfmeasurement |
| 2026-10-01 | rfmeasurement ≥ 0.2.0 desde PyPI; los resultados se empaquetan con `rfmeasurement.reporting` | La 0.2.0 trae `ProvenanceGraph`, `record_id`, captura de entorno, metadatos e informes; ya no hace falta depender de un commit |
| 2026-10-01 | El presupuesto por fuentes usa los coeficientes de la propagación lineal; valor, incertidumbre e intervalo salen de Monte Carlo | `build_budget` de rfmeasurement trabaja con coeficientes de sensibilidad; la conversión no es lineal, así que lo que se reporta es Monte Carlo, y la diferencia entre ambos queda en el registro |

## Abiertas

| Decisión | Cuándo | De qué depende |
|---|---|---|
| G0: enunciado de novedad del Artículo 1 | Fin de octubre | Lectura de los competidores directos |
| ¿Cómo aplica el firmware su calibración cuando el tramo barrido no coincide con el intervalo calibrado? | Fase 0 | Comprobación con el equipo conectado. No afecta a ε* con el modelo capacitivo mientras la calibración cargada no cambie, pero sí al Γ que se vea en el conector |
| Papel de la SOL en el presupuesto: con el modelo capacitivo, calibrar la sonda con corto, aire y agua da el mismo ε* sea cual sea la SOL (comprobado numéricamente: diferencia ~1e-9), siempre que no cambie entre la terna y la muestra. La SOL contaría como fuente solo con modelos de inversión no bilineales | Fase 2 | Qué modelos de inversión se van a comparar |
| Patrón de cortocircuito de la sonda | Fase 2 | Repetibilidad medida de cada variante |
| Diámetro de la sonda (SMA de panel o semirrígido de 0,141″) | Fase 2–3 | Sensibilidad a baja frecuencia en el piloto de rango útil |
| G1: umbrales, banda mínima y criterios de rechazo | Fin de noviembre | Pilotos |
| Revista del Artículo 1 | Fase 5 | Si el peso del resultado es metrológico o de hardware abierto |
| Sesión con VNA de banco | Fase 3–4 | Acceso a un grupo de RF |
