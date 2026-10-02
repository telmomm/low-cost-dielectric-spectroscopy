# 2026-10-02 — Prueba de saltos y piloto de deriva sin sonda

- **Equipo:** NanoVNA-F V2, firmware 0.5.0, patrones conectados directamente al puerto. Calibración del
  firmware activa. El equipo llevaba encendido al menos hora y media (no se anotó el tiempo exacto).
- **Barrido:** 50 kHz–1,45 GHz en cinco tramos de 101 puntos.

## Prueba de saltos (`piloto_saltos`, 08:33–08:43 UTC)

Abierto fijo. 12 barridos leídos con el equipo barriendo en continuo y 12 con el barrido pausado,
alternados. Un salto es un punto que se aparta más de 0,03 de la mediana de su serie.

| | Continuo | Pausado |
|---|---|---|
| Puntos con salto | 1,46 % | 1,21 % |
| Barridos afectados | 12 de 12 | 12 de 12 |
| Ruido de los puntos sin salto, por tramo (dB) | −61 −59 −57 −53 −45 | −62 −59 −57 −53 −45 |

- **Pausar no los quita.** La sospecha de que el firmware reescribía los datos mientras se leían queda
  descartada. La opción `pausar` se deja desactivada.
- **Son saltos de fase.** El módulo apenas cambia (cociente con la mediana entre 0,99 y 1,02, salvo
  casos aislados) y la fase salta entre 1° y 7°.
- **Dependen de la posición dentro del tramo, no de la frecuencia.** Entre los puntos 20 y 40 de cada
  tramo de 101 la tasa es del 4–7 %; en el resto, por debajo del 1 %. Por eso reaparecen siempre en las
  mismas zonas: 0,25 MHz, 2,8 MHz, 30 MHz, 350–425 MHz y 1125–1160 MHz.
- **En los peores puntos fallan hasta el 42 % de los barridos** (379 MHz). La mediana de cinco
  repeticiones mejora el percentil 99 del error de −36 a −45 dB, pero no protege esos puntos.

## Piloto de deriva (`piloto_deriva`, tanda `deriva_20261002T084525Z`, 08:45–09:49 UTC)

Calibración con carga, abierto y corto (3 barridos cada uno) y, con el corto sin tocar, 61 barridos a
uno por minuto. Cada barrido se corrige con los términos del principio.

**Incidencia.** Los barridos de calibración se sucedieron sin pausa: el aviso para cambiar de patrón no
esperó, probablemente por pulsaciones de Intro acumuladas. La primera repetición del abierto es todavía
la carga, la primera del corto es todavía el abierto y la segunda del corto cambia a mitad del tramo de
1–10 MHz. Los `.s1p` se conservan tal cual; el análisis descarta esos tramos comparando cada uno con el
de la última repetición. La calibración queda con una o dos repeticiones por patrón en lugar de tres.

| Tramo (MHz) | Repetibilidad a 1 min (dB) | Error a 0 min | 15 min | 30 min | 45 min | 60 min |
|---|---|---|---|---|---|---|
| 0,05–1 | −65 | −61 | −60 | −58 | −56 | −53 |
| 1–10 | −63 | −60 | −57 | −58 | −56 | −54 |
| 10–100 | −64 | −62 | −61 | −61 | −62 | −60 |
| 100–1000 | −57 | −54 | −54 | −54 | −56 | −55 |
| 1000–1450 | −48 | −45 | −46 | −46 | −46 | −47 |

- **Por encima de 10 MHz no se aprecia deriva en una hora.** El error se queda en el nivel del ruido.
- **Por debajo de 10 MHz hay una deriva lenta**, de −60 a −53 dB (un 0,1 % en módulo al cabo de la hora).
- **Entre 1 y 1,45 GHz manda el ruido, no la deriva:** −45 dB desde el primer minuto.

Lo que este piloto no cubre: el calentamiento desde frío, la sonda, un cable, y la reconexión. Es la
deriva de un equipo ya caliente con un patrón que no se toca.

## Qué cambia para la próxima sesión

- Los avisos de los scripts vacían ahora las pulsaciones acumuladas antes de esperar el Intro.
- Averiguar si los saltos van con la posición o con el tiempo dentro del barrido: repetir con 51 puntos
  por tramo y ver si la zona afectada se desplaza.
- Repetir el piloto de deriva desde frío, anotando `--encendido-min`.

## Variante con 51 puntos por tramo (`piloto_saltos`, `saltos_puntos_20261002T101044Z`, 10:11–10:19 UTC)

Abierto fijo. 12 barridos con tramos de 101 puntos y 12 con tramos de 51, alternados, sobre las mismas
frecuencias de inicio y fin. Un barrido completo tarda unos 24 s con 101 puntos y unos 16 s con 51.

| | 101 puntos | 51 puntos |
|---|---|---|
| Puntos con salto (umbral 0,03) | 1,33 % | 2,52 % |
| Número de punto de los saltos (mediana) | 32 | 14 |
| Posición dentro del tramo (mediana) | 32 % | 28 % |
| Décima del tramo más afectada | 20–40 % (3,3–3,7 %) | 20–30 % (14 %) |
| Frecuencias más afectadas (MHz) | 2,9 · 29,8 · 361–388 · 1126–1157 | 3,2–3,5 · 33–37 · 280 |
| Salto de fase (mediana / máximo) | 1,8° / 6,8° | 2,0° / 7,2° |

- **No van con el número de punto.** Con 51 puntos la zona afectada pasa a los puntos 12–15; si
  fuera el número de punto, habría seguido en los puntos 28–36.
- **Tampoco con una frecuencia fija.** En el tramo de 10–100 MHz, los saltos están en 29,8 MHz con
  101 puntos y en 33–37 MHz con 51, aunque las dos mallas tienen puntos en ambas frecuencias.
- **Van con la posición relativa dentro del tramo:** en torno al 20–35 % de su recorrido, sea cual sea
  el tramo y el número de puntos. Hay zonas menores hacia el 45–50 % y el 85–90 %.
- La causa sigue sin conocerse. El ruido de los puntos sin salto es el mismo con 51 puntos que con 101.

**Consecuencia práctica.** Como la zona depende de dónde empieza y acaba cada tramo, se puede esquivar
midiendo cada frecuencia en dos tramos desplazados entre sí, de modo que lo que cae en la zona mala de
uno quede en la zona limpia del otro. Cuesta el doble de tiempo de barrido.

## Dos juegos de tramos desplazados (`piloto_saltos`, `saltos_tramos_20261002T103052Z`, 10:30–10:41 UTC)

Abierto fijo. 12 barridos con el juego A (cortes en 1, 10, 100 y 1000 MHz) y 12 con el juego B (cortes
en 0,3, 3, 30 y 300 MHz), alternados. Umbral de salto: 0,03.

| | Juego A | Juego B | Combinación |
|---|---|---|---|
| Puntos con salto | 1,03 % | 0,88 % | 0,55 % |
| Dentro de su zona (15–40 % de cada tramo) | 2,18 % | 2,05 % | — |
| Fuera de su zona | 0,63 % | 0,47 % | — |
| La zona de A, medida con cada juego | 2,18 % | 0,53 % | — |
| La zona de B, medida con cada juego | 0,95 % | 2,05 % | — |
| Peor frecuencia (barridos con salto) | 33 % | 50 % | 17 % |
| Frecuencias con salto en ≥ 25 % de los barridos | 4 | — | 0 |

La combinación toma de cada juego los puntos de fuera de su zona: 742 frecuencias en lugar de 501.

- **Por encima de 100 MHz la zona se mueve con el tramo.** En A los saltos están en 350–415 MHz y en
  1125–1160 MHz; en B esas frecuencias salen limpias y los saltos pasan a 530–760 MHz, que es el
  20–40 % de su tramo de 300–1450 MHz. Ahí están las tasas altas, y ahí el desplazamiento funciona.
- **Por debajo de 100 MHz el patrón es menos claro.** Aparecen saltos en 1–3 MHz y en 55–90 MHz con los
  dos juegos, con tasas bajas (uno o dos barridos de doce por frecuencia). Con doce barridos no se
  puede decir si dependen de la frecuencia.
- **La combinación reduce los saltos a la mitad y elimina las frecuencias peores**, pero no los quita
  todos: queda un 0,55 %, con un máximo del 17 % en 1,41 MHz.

Con más estadística, los 61 barridos del corto del piloto de deriva (juego A) dan la misma imagen: un
1,08 % de puntos con salto, concentrados en el 20–40 % de los tramos de 100–1000 MHz (8–13 %) y
1000–1450 MHz (6–10 %), y mucho menos en los tramos bajos. La frecuencia peor, 361 MHz, salta en el
46 % de los barridos: con el juego A solo, la mediana de cinco repeticiones caería en un salto el 42 %
de las veces en ese punto. Tras combinar, con una tasa máxima del 17 %, esa probabilidad baja al 4 %.
