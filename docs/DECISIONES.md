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

## Abiertas

| Decisión | Cuándo | De qué depende |
|---|---|---|
| G0: enunciado de novedad del Artículo 1 | Fin de octubre | Lectura de los competidores directos |
| Driver de adquisición: protocolo binario V2 o consola de texto | Fase 0 | Comprobación con el equipo conectado |
| Patrón de cortocircuito de la sonda | Fase 2 | Repetibilidad medida de cada variante |
| Diámetro de la sonda (SMA de panel o semirrígido de 0,141″) | Fase 2–3 | Sensibilidad a baja frecuencia en el piloto de rango útil |
| G1: umbrales, banda mínima y criterios de rechazo | Fin de noviembre | Pilotos |
| Revista del Artículo 1 | Fase 5 | Si el peso del resultado es metrológico o de hardware abierto |
| Sesión con VNA de banco | Fase 3–4 | Acceso a un grupo de RF |
