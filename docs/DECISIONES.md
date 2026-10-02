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
| 2026-10-01 | **G0 superada de forma provisional**: se sigue adelante con el Artículo 1 centrado en el presupuesto de incertidumbre por fuentes | De 20 trabajos con VNA de bajo coste (10 a texto completo), ninguno lo reporta. Lo más cercano es Małek 2026 (NanoVNA V2.2, sensor planar, solo tipo A). Provisional hasta repetir la búsqueda en Scopus y WoS y leer los 10 trabajos de pago. Detalle en `docs/SOTA/README.md`, sección 0 |
| 2026-10-01 | Líquidos de validación: metanol y etanol con los parámetros del informe NPL MAT 23 | Fuente primaria con incertidumbres (k = 2) y trazabilidad a patrones nacionales, de 10 a 50 °C |
| 2026-10-02 | Tiempo de lectura del puerto serie a 0,25 s en `conectar()` | El comando `scan` tarda 1,5–3 s por tramo y pynanovna, con su valor por defecto, abandona a los 2 s |
| 2026-10-02 | Un cero exacto en S11 se trata como barrido defectuoso | Con el firmware 0.5.0 el equipo devuelve ceros por encima de 1,5 GHz en vez de datos |
| 2026-10-02 | Banda de trabajo: 50 kHz–1,45 GHz (`F_START_HZ`, `F_STOP_HZ` en `lcds.acquisition`) | La misma que en `nanovna-calibration`; por encima de 1,5 GHz el equipo, con el firmware 0.5.0, devuelve ceros. La línea se plantea para esa banda y no para los 3 GHz nominales |

## Abiertas

| Decisión | Cuándo | De qué depende |
|---|---|---|
| Confirmar G0 | Octubre | Scopus y WoS; lectura de los trabajos de pago |
| Enfoque del Artículo 3: ya existe bajo coste in vivo en piel (Schiavoni 2023) e hidratación de la piel con VNA portátil (Cataldo 2022) | Tras G3 | Leer ambos a fondo antes de hablar con el colaborador clínico |
| ¿Reportar también el error tras ajustar a un modelo de relajación, como Linha 2025, para poder compararse con él? | Fase 5 | Decisión de análisis; la medida directa sigue siendo el resultado principal |
| Dónde se hace la SOL: fuera del intervalo calibrado el firmware da valores sin sentido (|S11| hasta 2 entre 1 y 100 MHz con la calibración que estaba cargada), y su comando `cal off` no tiene efecto, así que la corrección del firmware no se puede desactivar por USB | Fase 0 | Opciones: calibrar en el equipo sobre toda la banda, o SOL por software sobre los mismos tramos (`lcds.sol`), que se aplica encima de la del firmware y no interpola |
| Papel de la SOL en el presupuesto: con el modelo capacitivo, calibrar la sonda con corto, aire y agua da el mismo ε* sea cual sea la SOL (comprobado numéricamente: diferencia ~1e-9), siempre que no cambie entre la terna y la muestra. La SOL contaría como fuente solo con modelos de inversión no bilineales | Fase 2 | Qué modelos de inversión se van a comparar |
| Patrón de cortocircuito de la sonda | Fase 2 | Repetibilidad medida de cada variante |
| Diámetro de la sonda (SMA de panel o semirrígido de 0,141″) | Fase 2–3 | Sensibilidad a baja frecuencia en el piloto de rango útil |
| G1: umbrales, banda mínima y criterios de rechazo | Fin de noviembre | Pilotos |
| Revista del Artículo 1 | Fase 5 | Si el peso del resultado es metrológico o de hardware abierto |
| Sesión con VNA de banco | Fase 3–4 | Acceso a un grupo de RF |
