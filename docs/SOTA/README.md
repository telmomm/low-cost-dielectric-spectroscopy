# Estado del arte inicial: síntesis y consecuencias para la línea

Síntesis de los dos informes de Consensus guardados en esta carpeta (generados el 1 de octubre de 2026;
los PDF no se versionan):

| Informe | Corpus | Pregunta |
|---|---|---|
| `Metrological_characterization_of_a_low-cost_vector.pdf` | 50 artículos (9 búsquedas) | ¿Pueden los VNA de bajo coste caracterizar con exactitud materiales biológicos con OECP? |
| `open-ended_coaxial_probe_low-cost_VNA_NanoVNA_d.pdf` | 100 artículos (6 búsquedas) | ¿Pueden medir de forma fiable las propiedades dieléctricas de tejidos? |

> **Aviso.** Son síntesis automáticas. Todas las cifras de este documento salen de los informes, no de
> los artículos: hay que comprobarlas en la fuente primaria antes de citarlas. La columna `leido` de
> [matriz_literatura.csv](matriz_literatura.csv) registra qué se ha verificado.

## 0. Resultado de la fase 1 (lectura de las fuentes primarias)

Las secciones 1 a 3 resumen los informes de Consensus tal como llegaron. Esta sección recoge lo que
cambia tras leer los artículos; donde haya contradicción, manda esta. Búsqueda en
[busqueda.md](busqueda.md) y extracción en [matriz_literatura.csv](matriz_literatura.csv).

**Puerta G0: superada, de forma provisional.** De los 20 trabajos con VNA de bajo coste retenidos,
ninguno publica un presupuesto de incertidumbre por fuentes (GUM o Monte Carlo) para una sonda coaxial.
Es provisional por dos motivos: la búsqueda se ha hecho en índices abiertos y no en Scopus ni WoS, y
diez de los trabajos solo se han podido leer por el resumen.

### Cifras comprobadas

| Cifra de los informes | Fuente primaria | Resultado |
|---|---|---|
| Presión: −0,31 % y −0,32 % por kPa, de 7,7 a 77 kPa | Maenhout 2020a | Correcta: −0,31 ± 0,09 % (ε′) y −0,32 ± 0,14 % (ε″) por kPa, hígado bovino, 0,5–20 GHz |
| Deshidratación: hasta 9 % en 35 min | Maenhout 2020b | Correcta: hígado porcino; con el montaje modificado el cambio se reduce a la mitad |
| Calibración válida unos 5 min | Linha 2025 | Correcta, pero es una observación empírica sin cuantificar, y del pocketVNA 2.0 |
| MAPE «desde 0,66 %» | Linha 2025 | Correcta con matices: es el mejor caso (corteza renal, por encima de 200 MHz) y sobre datos **ajustados** a un modelo de Cole-Cole tras un filtrado temporal, no sobre la medida directa |
| NanoVNA fiable de 1 a 500 MHz, inestable por encima de 700 MHz | González-Teruel 2022 | Engañosa: ver abajo |

### Correcciones a los informes

1. **El límite de 500–700 MHz no se traslada a nuestro equipo.** González-Teruel usó un nanoVNA-H, que
   por encima de 300 MHz mide con armónicos, y lo comparó con un Agilent 4395A que solo llega a
   500 MHz: «comparable hasta 500 MHz» significa que ahí se acaba la referencia. El ruido por encima de
   700 MHz es de ese hardware. El NanoVNA-F V2 es otro diseño; su banda útil hay que medirla.
2. **Arias-Rodríguez 2025 no valida un VNA barato.** Lo barato es la sonda SMA; las medidas son con un
   Keysight P9374B y, en parte, con un PicoVNA 106. No es un competidor en la clase NanoVNA.
3. **Linha 2025 usa el modelo de línea virtual con dos patrones** (aire y agua), no el capacitivo, y su
   exactitud depende del posprocesado (filtrado temporal y ajuste a un modelo de relajación).
4. **Ya hay trabajo de bajo coste in vivo**, al contrario de lo que indicaban las matrices de cobertura:
   Schiavoni 2023 mide piel en 11 voluntarios con un nanoVNA y una sonda coaxial truncada, y Cataldo 2022
   aborda la hidratación de la piel con un VNA portátil. Afecta al planteamiento del Artículo 3.
5. **Aydın 2019 no mide permitividad** (caracteriza antenas con un miniVNA). Se excluye.
6. **«García 2025» es Rangel et al.**: NanoVNA V2 Plus4 frente a un Agilent E5071B.

### El antecedente más cercano en incertidumbre

Małek et al. (2026, *IEEE TMTT*) usan un NanoVNA V2.2 con un sensor planar para aceites. Incluyen un
análisis de incertidumbre, pero solo de tipo A y con dos componentes (instrumento, a partir de 31
repeticiones, e imperfecciones físicas); descartan el tipo B por coste de cálculo y señalan que la hoja
de datos del NanoVNA no trae presupuesto de incertidumbre. No es una sonda coaxial ni un material
biológico. Es el trabajo que hay que citar y superar.

### Incertidumbre de la sonda coaxial con equipo de banco

El análisis que se quiere hacer ya existe para VNA de laboratorio: Gabriel y Peyman (2006) y, sobre
todo, Bao et al. (2021, *IEEE TMTT*), que cuantifican la incertidumbre del líquido de calibración, la
deriva y la posición de la sonda. El método no es la novedad; lo es aplicarlo a un equipo de esta clase,
donde la deriva y el ruido pesan mucho más. Hay además una librería abierta para la sonda coaxial,
PyOECP (Yoon et al., 2022), que conviene revisar antes de ampliar `lcds.probe` con más modelos.

### Enunciado de novedad que se sostiene

Los trabajos de bajo coste reportan un error frente a una referencia (MAPE, RMSE, desviación entre
sondas) y, como mucho, repetibilidad. Ninguno separa las fuentes, propaga la incertidumbre a ε* ni
deriva de ella la banda útil. Además, el único con equipo de esta clase en tejido (Linha 2025) reporta
el error tras ajustar a un modelo de relajación, lo que suaviza el ruido y no describe la incertidumbre
de una medida directa. Eso es lo que aporta el Artículo 1.

## 1. Qué dice el estado del arte

1. **El bajo coste ya está validado en condiciones controladas.** Varios trabajos comparan un VNA
   barato con sonda propia frente a un sistema comercial, en líquidos y en tejido ex vivo, con errores
   de pocos puntos porcentuales en bandas restringidas (Linha 2025; Arias-Rodríguez 2025; García 2025;
   Moreno-Merín 2026). Los informes califican esta afirmación como evidencia **fuerte**.
2. **El NanoVNA en concreto tiene una banda fiable estrecha.** En el único trabajo con NanoVNA y sonda
   coaxial del corpus (suelos, González-Teruel 2022) el equipo era comparable a un VNA comercial entre
   1 y 500 MHz y perdía estabilidad por encima de 700 MHz. Que los VNA de mano más baratos funcionen
   bien a varios GHz es evidencia **débil**.
3. **La calibración caduca rápido.** Con un pocketVNA, las medidas debían terminarse en los cinco
   minutos siguientes a la calibración, sobre todo por debajo de 0,5 GHz y por encima de 2,5 GHz
   (Linha 2025).
4. **El modelo de inversión pesa tanto como el hardware.** El modelo capacitivo se desvía por encima
   de 3–4 GHz y con muestras conductoras; el modelo de radiación fue el mejor en muestras biológicas
   (Arias-Rodríguez 2025; Šarolić y Matković 2022; Berube 1996).
5. **En tejido, los factores biológicos igualan o superan al instrumento.** Presión de contacto:
   −0,31 % (ε′) y −0,32 % (ε″) por kPa entre 7,7 y 77 kPa. Deshidratación: hasta un 9 % en 35 minutos.
   Profundidad sensible: 0,44–0,62 mm con sonda de 2,20 mm y 0,75–0,98 mm con sonda de 3,58 mm
   (Maenhout 2020a, 2020b; Chen 2025; Meaney 2014).
6. **El marco de incertidumbre para tejidos ya existe**, pero para equipos de laboratorio
   (Gabriel y Peyman 2006), y hay una guía práctica de medida reciente (Farrugia 2024).

## 2. Dónde está el hueco

Las matrices de cobertura de los dos informes coinciden:

| Cruce | Artículos | Lectura |
|---|---|---|
| VNA de bajo coste × comparación con equipo comercial | 18 | Saturado: una validación más no es novedad |
| VNA de bajo coste × líquidos de referencia | 29 | Saturado |
| VNA de bajo coste × datos de incertidumbre | 5 (informe 1) / 17 (informe 2) | Hay cifras de error, pero rara vez un presupuesto por fuentes |
| VNA de bajo coste × protocolos estandarizados | 4 | Hueco |
| Biopsias × incertidumbre | 0 | Hueco |
| In vivo × comparación comercial / incertidumbre | 0 / 0 | Hueco (Artículo 3) |

Preguntas abiertas que formulan los propios informes y que esta línea puede responder:

- ¿Qué presupuesto de incertidumbre y qué estándar de metadatos deben acompañar a una medida
  dieléctrica biológica de bajo coste? → **Artículo 1**
- ¿Mantiene un equipo de clase NanoVNA la exactitud calibrada en tejido ex vivo heterogéneo durante
  tiempos de medida realistas? → **Artículo 2**
- ¿Qué protocolo controla presión, hidratación y movimiento del cable lo bastante para ser
  reproducible entre laboratorios? → **Artículos 1 y 2**

## 3. Consecuencias para el planteamiento de la línea

| # | El documento de la línea dice | El SOTA obliga a |
|---|---|---|
| C1 | «Los trabajos con NanoVNA son pocos y no biomédicos» | Reescribir la motivación: ya hay validaciones de bajo coste en tejido, una de ellas en *IEEE TIM* (Linha 2025). La novedad defendible es el **presupuesto de incertidumbre completo por fuentes (GUM + Monte Carlo)** y el protocolo con metadatos, no la validación |
| C2 | Medir de 50 kHz a 3 GHz y «dejar que los datos decidan» | Se mantiene, pero la expectativa realista es una banda útil de unos cientos de MHz. El criterio go/no-go de «≥ 1 década» sigue siendo alcanzable; conviene fijar por adelantado qué banda mínima haría el sistema útil para tejidos |
| C3 | Deriva: barridos cada 10–15 min durante 2–4 h | Añadir la **vida útil de la calibración** como factor explícito (resolución de minutos tras calibrar). Condiciona cuántas muestras caben entre recalibraciones |
| C4 | Modelo capacitivo «para empezar» | Añadir el **modelo de inversión como factor de análisis** (capacitivo, radiación, línea virtual). No cuesta medidas nuevas: se aplica a los mismos .s1p |
| C5 | Marco GUM + Monte Carlo | Añadir Gabriel y Peyman (2006) y Farrugia (2024) como referencias del marco y del protocolo, y Cho (2024) para los errores aleatorios del VNA |
| C6 | Art. 2: célula de carga y registro del tiempo | Dimensionar con las cifras del punto 5: el intervalo de presión, el tiempo máximo por pieza y el grosor mínimo de muestra salen de ahí |
| C7 | VNA de banco «opcional» | Sube de prioridad: todos los competidores directos comparan con un sistema comercial. Sin esa sesión, el artículo se apoya solo en líquidos de referencia |

## 4. Lecturas prioritarias

Orden de lectura para la fase 1 del [ROADMAP](../../ROADMAP.md). Los DOI proceden de los informes.

**Competidores directos (leer completos y extraer a la matriz)**

1. Linha et al. (2025), *IEEE TIM* 74 — pocketVNA + sonda de 2,2 mm en tejido, hasta 3 GHz. [10.1109/tim.2025.3561426](https://doi.org/10.1109/tim.2025.3561426)
2. Arias-Rodríguez et al. (2025), *Sensors* 25 — sonda SMA de bajo coste hasta 6 GHz, tres modelos, reproducibilidad entre sondas. [10.3390/s25133935](https://doi.org/10.3390/s25133935)
3. González-Teruel et al. (2022), *Comput. Electron. Agric.* 195 — NanoVNA + OECP en suelos. [10.1016/j.compag.2022.106847](https://doi.org/10.1016/j.compag.2022.106847)
4. Joof et al. (2024), SIU — pocket VNA + OECP, estimación multifrecuencia. [10.1109/siu61531.2024.10601009](https://doi.org/10.1109/siu61531.2024.10601009)
5. García et al. (2025), GMEPE/PAHCE — VNA de precisión frente a bajo coste. [10.1109/gmepe/pahce65777.2025.11002836](https://doi.org/10.1109/gmepe/pahce65777.2025.11002836)
6. Moreno-Merín et al. (2026), ICMWIA — sonda semirrígida de 0,047″ hasta 20 GHz. [10.1109/icmwia67461.2026.11448512](https://doi.org/10.1109/icmwia67461.2026.11448512)
7. Zhu et al. (2024), *Int. J. Agric. Biol. Eng.* — espectrómetro portátil con mini-VNA. [10.25165/j.ijabe.20241703.7170](https://doi.org/10.25165/j.ijabe.20241703.7170)
8. Aboyewa et al. (2022), *Rev. Sci. Instrum.* 93 — circuito de RF sencillo para OECP. [10.1063/5.0095909](https://doi.org/10.1063/5.0095909)
9. Małek et al. (2026), *IEEE TMTT* — NanoVNA V2.2 con sensor planar y análisis de incertidumbre de tipo A. [10.1109/tmtt.2026.3664936](https://doi.org/10.1109/tmtt.2026.3664936)
10. Erkoreka y Martinez-Perdiguero (2024), arXiv:2402.00498 — NanoVNA V2 con condensador de placas paralelas, cristal líquido, 10 MHz–1 GHz.
11. Schiavoni et al. (2023), *IEEE Access* — nanoVNA con sonda coaxial in vivo en piel. [10.1109/access.2023.3243843](https://doi.org/10.1109/access.2023.3243843)

**Incertidumbre y protocolo**

- Gabriel y Peyman (2006), *Phys. Med. Biol.* 51 — análisis de errores e incertidumbre. [10.1088/0031-9155/51/23/006](https://doi.org/10.1088/0031-9155/51/23/006)
- Farrugia et al. (2024), *IEEE Access* 12 — guía práctica de medida. [10.1109/access.2024.3352728](https://doi.org/10.1109/access.2024.3352728)
- La Gioia et al. (2018), *Diagnostics* 8 — retos y prácticas habituales. [10.3390/diagnostics8020040](https://doi.org/10.3390/diagnostics8020040)
- Bao et al. (2021), *IEEE TMTT* 69 — efecto de la incertidumbre de medida en el ajuste de relajaciones. [10.1109/tmtt.2021.3093895](https://doi.org/10.1109/tmtt.2021.3093895)
- Cho et al. (2024), *IEEE TIM* 73 — errores aleatorios de un VNA con modelo residual. [10.1109/tim.2024.3481555](https://doi.org/10.1109/tim.2024.3481555)

**Modelos de sonda**

- Marsland y Evans (1987). [10.1049/ip-h-2:19870068](https://doi.org/10.1049/ip-h-2:19870068)
- Misra y Foster (1990), *IEEE TMTT* 38. [10.1109/22.44150](https://doi.org/10.1109/22.44150)
- Berube et al. (1996), *IEEE TMTT* 44 — comparación de cuatro modelos. [10.1109/22.539951](https://doi.org/10.1109/22.539951)
- Šarolić y Matković (2022), *Sensors* 22 — límites del modelo capacitivo. [10.3390/s22166024](https://doi.org/10.3390/s22166024)
- Dilman et al. (2022), *IEEE TIM* 71. [10.1109/tim.2022.3147878](https://doi.org/10.1109/tim.2022.3147878)

**Para el Artículo 2 (tejido)**

- Maenhout et al. (2020a), *Sensors* 20 — presión de contacto. [10.3390/s20072060](https://doi.org/10.3390/s20072060)
- Maenhout et al. (2020b), *IEEE J-ERM* 4 — deshidratación. [10.1109/jerm.2019.2953401](https://doi.org/10.1109/jerm.2019.2953401)
- Meaney et al. (2014), *BMC Med. Phys.* 14 — volumen sensible. [10.1186/1756-6649-14-3](https://doi.org/10.1186/1756-6649-14-3)
- Aydınalp et al. (2022), *Sensors* 22 — profundidad sensible y apertura. [10.3390/s22030760](https://doi.org/10.3390/s22030760)
- Cavagnaro y Ruvio (2020), *Sensors* 20 — tamaño de muestra. [10.3390/s20133756](https://doi.org/10.3390/s20133756)
- Chen et al. (2025), *Front. Bioeng. Biotechnol.* 13. [10.3389/fbioe.2025.1575142](https://doi.org/10.3389/fbioe.2025.1575142)
- Porter et al. (2024), *ASME Open J. Eng.* — estado actual y técnicas emergentes. [10.1115/1.4064746](https://doi.org/10.1115/1.4064746)

## 5. Pendiente de esta carpeta

- Repetir las cadenas Q1 y Q2 en Scopus y WoS ([busqueda.md](busqueda.md)).
- Conseguir y leer los diez trabajos de pago que solo se han visto por el resumen; sobre todo Rangel
  2025 (NanoVNA V2 Plus4), Joof 2024 y Moreno-Merín 2026.
- Conseguir Peyman et al. (2007) para implementar el modelo de las disoluciones de NaCl, y el artículo
  original de Kaatze (1989) para cerrar la comprobación del agua.
