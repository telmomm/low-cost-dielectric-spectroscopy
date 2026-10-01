# Protocolo del Artículo 1: caracterización metrológica

> **Estado: borrador v0, no congelado.** Los valores marcados con «(G1)» se fijan al final de la fase
> de pilotos y antes de la campaña ([ROADMAP](ROADMAP.md), puerta G1). Después de congelarlo, los
> cambios se anotan en la sección 9.

## 1. Pregunta

¿Con qué incertidumbre mide la permitividad compleja el sistema NanoVNA-F V2 + sonda coaxial de extremo
abierto, y en qué banda de frecuencia esa incertidumbre es aceptable para materiales biológicos?

## 2. Sistema bajo ensayo

El sistema es la cadena completa: VNA, kit SOL, cable, sonda, soporte, procedimiento de calibración y
código de conversión. Identificación de cada elemento en [hardware/README.md](hardware/README.md).

Hay dos calibraciones distintas y se tratan por separado en el método y en el presupuesto:

| Calibración | Paso | Patrones |
|---|---|---|
| SOL del VNA | medida bruta → Γ en el plano del conector | cortocircuito, abierto y carga del kit |
| De la sonda | Γ → ε* | aire, cortocircuito en la apertura y agua desionizada a temperatura conocida |

## 3. Magnitudes y métricas

- ε′ y σ = ω·ε₀·ε″ en función de la frecuencia.
- Error relativo frente al modelo de referencia de cada líquido.
- Incertidumbre expandida (k = 2) por Monte Carlo (JCGM 101).
- **Rango útil:** banda continua en la que error e incertidumbre quedan dentro de los umbrales.

## 4. Umbrales fijados a priori

| Parámetro | Propuesta | Valor final |
|---|---|---|
| Error máximo en ε′ | ≤ 5 % | (G1) |
| Error máximo en σ | ≤ 10 % | (G1) |
| Banda mínima para considerar útil el sistema | ≥ 1 década | (G1) |
| Líquidos sobre los que se evalúa | metanol, etanol, NaCl 0,1–1 % | (G1) |

Regla fija: **el líquido usado para calibrar la sonda nunca se usa para validar.**

## 5. Diseño experimental

| Factor | Niveles | Responde a | n |
|---|---|---|---|
| Repetibilidad de la medida | sin recalibrar | componente de tipo A de corto plazo | ≥ 10 |
| Repetibilidad de la calibración | recalibración completa (SOL + sonda) | contribución de la calibración | ≥ 5 |
| Vida útil de la calibración | tiempo desde la calibración | cadencia de recalibración | (G1) |
| Temperatura | 20, 25, 30 y 37 °C | sensibilidad térmica | (G1) |
| Deriva tras el encendido | barridos durante 2–4 h | tiempo de calentamiento | piloto |
| Cable | fijo / flexionado de forma controlada | inestabilidad de fase | (G1) |
| Promediado y puntos | 2–3 configuraciones | ruido frente a tiempo | (G1) |
| Modelo de inversión | capacitivo, radiación, línea virtual | error de modelo (solo análisis) | — |
| Unidad de VNA (si se consigue) | 2–3 unidades | variabilidad entre unidades | — |
| VNA de banco (si se consigue) | una sesión con las mismas muestras | comparación externa | — |

Barrido de 50 kHz a 3 GHz en todas las medidas. El orden de los líquidos se aleatoriza en cada sesión.

## 6. Procedimiento de una sesión

1. Encender el VNA y esperar el tiempo de calentamiento (G1).
2. Calibración SOL en el plano del conector de la sonda. Anotar su identificador.
3. Calibración de la sonda: aire, cortocircuito y agua, con la temperatura del agua registrada.
4. Medir el líquido de comprobación. Si se sale de tolerancia (G1), repetir desde el paso 2.
5. Medir los líquidos en orden aleatorizado. Entre muestras: limpiar, secar y comprobar que no hay
   burbujas en la apertura. Registrar la temperatura en cada medida.
6. Recalibrar con la cadencia fijada (G1) y repetir la comprobación al final de la sesión.
7. Cada barrido se guarda como .s1p en bruto con su .json ([data/README.md](data/README.md)) y la
   sesión se anota en `docs/cuaderno/`.

## 7. Criterios de rechazo

Se fijan en G1 y se aplican sin mirar el resultado en ε*. Candidatos:

- Líquido de comprobación fuera de tolerancia antes o después de la serie.
- Temperatura de la muestra fuera de ± (G1) °C respecto a la nominal.
- Burbuja o contacto defectuoso anotado por el operador en el momento de la medida.
- Metadatos incompletos.

Toda medida rechazada se conserva en `data/raw` con el motivo en sus metadatos.

## 8. Presupuesto de incertidumbre

| Fuente | Tipo | Cómo se evalúa |
|---|---|---|
| Ruido de la medida | A | repetibilidad sin recalibrar |
| Repetibilidad de la calibración SOL | A | recalibraciones |
| Repetibilidad de la calibración de la sonda | A | recalibraciones |
| Deriva desde la calibración | A/B | piloto de vida de calibración |
| Movimiento del cable | A/B | factor cable |
| Temperatura del agua de calibración | B | incertidumbre del termómetro propagada por el modelo de Debye |
| Modelo de referencia del agua | B | incertidumbre publicada del modelo |
| Imperfección del cortocircuito | B | repetibilidad del patrón y variantes |
| Definición de los patrones SOL | B | datos del kit; comparación con un kit caracterizado si lo hay |
| Modelo de inversión | B | diferencia entre modelos sobre los mismos datos |
| Preparación de las disoluciones | B | pesada y conductímetro (afecta a la referencia, no al sistema) |

Propagación de Γ a ε* por Monte Carlo, porque la transformación no es lineal. Marco: JCGM 100 y 101;
Gabriel y Peyman (2006) como referencia del área.

## 9. Desviaciones del protocolo

| Fecha | Cambio | Motivo |
|---|---|---|
| | | |
