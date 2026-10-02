# Línea de investigación: espectroscopía dieléctrica de bajo coste para aplicaciones biomédicas con NanoVNA-F V2

> Documento de arranque. Define el objetivo de la línea, el alcance de cada artículo, las bases técnicas y la relación entre los tres trabajos. La motivación y las referencias se revisaron el 1 de octubre de 2026 tras la fase 1 del [ROADMAP](ROADMAP.md); el detalle está en [docs/SOTA/README.md](docs/SOTA/README.md).

---

## 1. Objetivo general

Determinar con rigor metrológico **si un analizador vectorial de redes de bajo coste (NanoVNA-F V2), combinado con una sonda coaxial de extremo abierto de fabricación sencilla, permite medir propiedades dieléctricas de materiales biológicos con una incertidumbre suficiente para distinguir tejidos** y, en último término, para aplicaciones clínicas.

### Motivación (el hueco)

- Medir permitividad con un VNA de bajo coste y una sonda coaxial ya no es novedad. Hay validaciones frente a equipos comerciales en líquidos, alimentos, suelos y tejido ex vivo (Linha et al., 2025; Zhu et al., 2024; González-Teruel et al., 2022; Fita et al., 2026), e incluso un primer uso in vivo en piel (Schiavoni et al., 2023).
- Todos esos trabajos responden a la misma pregunta, cuánto se desvía el sistema barato de una referencia, y la responden con un error global (MAPE, RMSE) y, como mucho, con la repetibilidad. Ninguno separa las fuentes de incertidumbre ni la propaga hasta ε*.
- En el trabajo más cercano en tejido (Linha et al., 2025), el error se da tras un filtrado temporal y un ajuste a un modelo de relajación, de modo que no describe la incertidumbre de una medida directa. Sus propios autores señalan como principal limitación que la calibración solo era válida unos cinco minutos, sin cuantificarlo.
- El único análisis de incertidumbre con un equipo de clase NanoVNA (Małek et al., 2026) es de tipo A, con dos componentes, para un sensor planar y líquidos no biológicos. Sus autores señalan que el fabricante no da un presupuesto de incertidumbre del equipo.
- Las guías del área (La Gioia et al., 2018; Farrugia et al., 2024) piden controlar calibración, deriva, cable, temperatura y contacto, y el marco de incertidumbre para tejidos existe desde Gabriel y Peyman (2006), pero solo se ha aplicado a equipos de laboratorio.
- **Aportación diferencial:** el primer presupuesto de incertidumbre por fuentes (GUM y Monte Carlo) de un sistema NanoVNA con sonda coaxial para materiales biológicos, con la banda útil derivada de ese presupuesto y no de la comparación con una referencia, y con datos, código y trazabilidad abiertos.

### Hipótesis de la línea

- **H1.** En un rango de frecuencias acotado (que el Artículo 1 determinará), el NanoVNA-F V2 con sonda coaxial reproduce la permitividad de líquidos de referencia con un error comparable al de sistemas de gama media.
- **H2.** La incertidumbre resultante es menor que las diferencias dieléctricas entre tejidos con distinto contenido de agua (músculo, grasa, hígado, miocardio), de modo que es posible discriminarlos.
- **H3.** Un sistema portátil basado en esta cadena de medida, junto con un modelo predictivo, puede aportar información clínicamente útil en un caso de uso concreto (por definir con un colaborador clínico).

---

## 2. Instrumento: NanoVNA-F V2

| Característica | Valor / comentario |
|---|---|
| Rango de frecuencia | 50 kHz – 3 GHz nominal; banda de trabajo de esta línea: 50 kHz – 1,45 GHz (por encima de 1,5 GHz el equipo no entrega datos por USB con el firmware 0.5.0) |
| Margen dinámico | Sin dato fiable del fabricante: hay que medirlo. Para un NanoVNA V2 se han publicado 70 dB tras calibrar (Erkoreka y Martinez-Perdiguero, 2024), pero es otro equipo |
| Puertos | 2 (S11 y S21); esta línea usa sobre todo **S11 (reflexión, 1 puerto)** |
| Calibración | SOL(T) interna. El S11 que entrega por USB ya viene corregido por la calibración cargada en el firmware |
| Control | USB, consola de texto de la familia NanoVNA-F; en este proyecto, con `pynanovna` (ver `src/lcds/acquisition.py`) |

**Tarea inicial:** documentar el firmware, el número de serie y la configuración (puntos por barrido, promediado y ancho de banda de FI si el firmware lo permite). Todo eso forma parte del método.

---

## 3. Bases técnicas

### 3.1 Método de la sonda coaxial de extremo abierto (OECP)

- La sonda (una línea coaxial cortada y pulida en contacto con la muestra) se modela como una admitancia terminal que depende de la permitividad compleja del material: ε* = ε' − jε''.
- Se mide el coeficiente de reflexión Γ en el plano del conector y se convierte en ε* mediante un modelo de la sonda.
- **Modelo recomendado para empezar:** el modelo capacitivo o bilineal. La relación entre Γ y ε* se expresa como una transformación bilineal cuyos tres coeficientes complejos se obtienen calibrando con **tres patrones conocidos: circuito abierto (aire), cortocircuito y un líquido de referencia (agua desionizada)**.
- Este segundo paso de calibración (de Γ a ε) es independiente de la calibración SOL del VNA (de medida bruta a Γ). Hay que distinguir las dos en el método y en el presupuesto de incertidumbre.

**Limitaciones conocidas que hay que caracterizar:**
- A baja frecuencia, la sonda pequeña tiene una impedancia muy desadaptada, Γ ≈ 1 y la sensibilidad cae.
- La **polarización de electrodo** en soluciones conductoras (salinas, tejidos) distorsiona la medida a baja frecuencia.
- El **volumen de medida** de la sonda es pequeño (del orden del radio exterior), así que la heterogeneidad del tejido y la presión de contacto importan.
- Las burbujas de aire y el mal contacto son la principal fuente de error en muestras sólidas.

### 3.2 Modelos de referencia para la validación

| Material | Uso | Modelo / fuente |
|---|---|---|
| Agua desionizada | Calibración (3.er patrón) | Modelo de Debye dependiente de la temperatura (Kaatze, 1989) |
| Metanol, etanol | Validación (no se usan para calibrar) | Gregory y Clarke, NPL Report MAT 23 (2012): parámetros de relajación de 10 a 50 °C con su incertidumbre. Implementado en `src/lcds/reference.py` |
| NaCl 0,1–1 % | Validación con conductividad similar a la de los tejidos | Peyman et al. (2007) + conductímetro independiente. Referencia comprobada; falta conseguir el artículo para implementar el modelo |
| Tejidos | Comparación (Artículo 2) | Gabriel et al. (1996), base de datos IT'IS |

> Regla clave: **nunca validar con el mismo líquido que se ha usado para calibrar.**

### 3.3 Marco de incertidumbre

- Seguir la GUM (JCGM 100:2008) para las componentes de tipo A y B.
- Propagar la incertidumbre de Γ a ε* por **Monte Carlo** (JCGM 101:2008), porque la transformación bilineal no es lineal.
- Expresar los resultados como error relativo de ε' y de la conductividad σ (σ = ωε₀ε'') en función de la frecuencia, con bandas de incertidumbre expandida (k = 2).

---

## 4. Estructura de la línea: tres artículos encadenados

| | Artículo 1 | Artículo 2 | Artículo 3 |
|---|---|---|---|
| **Pregunta** | ¿Con qué incertidumbre mide el sistema y en qué rango? | ¿Basta esa incertidumbre para distinguir tejidos? | ¿Aporta valor clínico en un caso de uso real? |
| **Muestras** | Líquidos de referencia | Tejido animal ex vivo | Pacientes o voluntarios (con aprobación ética) |
| **Necesita colaboradores** | No (opcional: VNA de banco) | No (opcional: anatomía patológica o veterinaria) | Sí: colaborador clínico |
| **Producto** | Método validado + presupuesto de incertidumbre + hardware abierto | Dataset abierto + análisis de discriminación | Sistema portátil + modelo predictivo |
| **Esfuerzo** | Bajo-medio | Medio | Alto |

### Cómo se relacionan

1. **El Artículo 1 → Artículo 2:** el rango de frecuencias útil y el modelo de incertidumbre del Artículo 1 se usan directamente en el Artículo 2 para poner barras de error a cada medida de tejido. Sin el Artículo 1, el Artículo 2 no podría afirmar si una diferencia entre tejidos es real o ruido del sistema.
2. **El Artículo 2 → Artículo 3:** el Artículo 2 indica qué contrastes dieléctricos son detectables con este sistema. Eso decide qué aplicación clínica es viable (por ejemplo, cambios de contenido de agua) y cuál no (por ejemplo, glucosa, cuyo efecto dieléctrico es muy pequeño).
3. **Criterios de continuidad:** cada artículo tiene una condición explícita para seguir con el siguiente (ver sección 8). Si no se cumple, el artículo sigue siendo publicable como resultado negativo útil para la comunidad.

---

## 5. Artículo 1: caracterización metrológica

**Título provisional:** *Metrological characterization of a low-cost vector network analyzer for open-ended coaxial probe dielectric spectroscopy of biological materials*

### 5.1 Objetivos específicos

1. Determinar el rango de frecuencias en el que el sistema NanoVNA-F V2 + sonda reproduce la permitividad de líquidos de referencia dentro de un error objetivo (por ejemplo, ≤ 5 % en ε' y ≤ 10 % en σ; fijar estos umbrales a priori).
2. Construir un presupuesto de incertidumbre que separe las contribuciones de cada fuente.
3. Publicar el diseño de la sonda, el soporte y el código como recursos abiertos.

### 5.2 Material

- NanoVNA-F V2 y kit de calibración SOL (documentar si es el del fabricante o uno mejor caracterizado).
- Cable coaxial corto y de fase estable, **fijado mecánicamente** (su movimiento es una fuente de error importante).
- Sonda: conector SMA de panel o semirrígido de 0,141" cortado y pulido. Documentar las dimensiones con calibre o microscopio.
- Líquidos: agua desionizada, metanol, etanol y soluciones de NaCl de concentración conocida (preparadas por pesada).
- Termopar o sonda Pt100 en la muestra; baño termostático si es posible (ver el factor de temperatura).
- Conductímetro para la verificación independiente de las soluciones salinas.
- Soporte con control de la presión de contacto: un brazo con pesas calibradas o una célula de carga barata (HX711 + galga) para el Artículo 2.

### 5.3 Diseño experimental

| Factor | Niveles | Qué responde |
|---|---|---|
| Repetibilidad de la medida | ≥ 10 medidas sin recalibrar | Componente de tipo A de corto plazo |
| Repetibilidad de la calibración | ≥ 5 recalibraciones completas (SOL + bilineal) | Contribución de la calibración |
| Temperatura | p. ej. 20, 25, 30 y 37 °C | Sensibilidad térmica; corrección del modelo del agua |
| Deriva temporal | Barridos cada 10–15 min durante 2–4 h tras el encendido | Tiempo de calentamiento necesario y estabilidad |
| Movimiento del cable | Cable fijo frente a flexionado de forma controlada | Error por inestabilidad de fase |
| Promediado / puntos | 2–3 configuraciones | Equilibrio entre ruido y tiempo |
| Unidad de VNA (opcional) | 2–3 unidades si se pueden conseguir | Variabilidad entre unidades |
| VNA de banco (opcional) | Una sesión de medidas iguales | Comparación externa, refuerza mucho el artículo |

**Rango de frecuencias:** medir de 50 kHz a 1,45 GHz y dejar que los datos decidan el rango útil. Es previsible que la banda baja quede limitada por la sensibilidad de la sonda y la polarización de electrodo, y la alta por el margen dinámico del equipo.

### 5.4 Protocolo resumido

1. Calentamiento del equipo (duración según la prueba de deriva).
2. Calibración SOL en el plano del conector de la sonda.
3. Calibración de la sonda: aire, cortocircuito (lámina metálica o mercurio-free: papel de aluminio presionado o patrón de cortocircuito plano) y agua a temperatura conocida.
4. Medida de los líquidos de validación en orden aleatorizado, con limpieza y secado entre muestras y registro de la temperatura en cada medida.
5. Guardado de los archivos Touchstone (.s1p) en bruto con metadatos (temperatura, hora, número de calibración, operador).

### 5.5 Análisis

- Conversión de Γ a ε* con el modelo bilineal (código en Python con scikit-rf para el manejo de Touchstone).
- Comparación con los modelos de referencia: error relativo frente a la frecuencia para ε' y σ.
- Presupuesto de incertidumbre (tabla por fuente) y propagación por Monte Carlo.
- Gráfica clave del artículo: **error ± incertidumbre frente a frecuencia, con el rango útil sombreado.**

### 5.6 Revistas candidatas

- *Measurement* (Elsevier) o *IEEE Transactions on Instrumentation and Measurement*: si el foco es metrológico.
- *HardwareX*: si el foco es el instrumento abierto y reproducible.
- *Sensors* o *Electronics* (MDPI): más rápidas; valorar el coste del APC.

---

## 6. Artículo 2: discriminación de tejidos ex vivo

**Título provisional:** *Can a low-cost VNA discriminate biological tissues? Ex vivo dielectric spectroscopy with uncertainty-aware analysis*

### 6.1 Objetivos

1. Medir tejidos animales ex vivo (de origen alimentario, sin necesidad de comité ético; confirmarlo con el comité de la universidad): músculo, grasa, hígado, piel y **miocardio** (enlaza con la experiencia previa en cirugía cardíaca).
2. Comparar con Gabriel et al. (1996) y con la base de datos IT'IS, teniendo en cuenta la especie, la temperatura y el tiempo post mortem.
3. Determinar si los tejidos se separan **más allá de la incertidumbre del sistema** (usando el modelo del Artículo 1).
4. Evaluar un clasificador sencillo (por ejemplo, regresión logística o random forest sobre ε' y σ a varias frecuencias) con validación cruzada por muestra, no por medida, para evitar fugas de datos.

### 6.2 Variables a controlar

- Presión de contacto (célula de carga), temperatura de la muestra y tiempo desde la obtención.
- Varias localizaciones por pieza y varias piezas por tejido (la unidad estadística es la pieza).
- Volumen de medida: una prueba simple con capas de grosor conocido (grasa sobre músculo) permite estimarlo.

### 6.3 Producto

- **Dataset abierto** (Zenodo) con archivos .s1p en bruto, permitividades calculadas y metadatos.
- Revistas candidatas: *Physiological Measurement*, *Medical Engineering & Physics*, *IEEE Journal of Electromagnetics, RF and Microwaves in Medicine and Biology*.

---

## 7. Artículo 3: aplicación clínica (fase posterior)

Este artículo depende de los dos anteriores y de un colaborador clínico. No conviene concretarlo hasta tener los resultados del Artículo 2.

- **Casos de uso a explorar con el colaborador:** estado de hidratación o edema tisular (cambios en el contenido de agua, compatibles con la sensibilidad esperada) y, por cercanía con la cirugía cardíaca, la monitorización de fluidos en el postoperatorio.
- **Casos a evitar como objetivo principal:** glucosa no invasiva (efecto dieléctrico muy pequeño, campo con muchas afirmaciones y poca validación).
- **Requisitos:** aprobación del comité de ética, posible rediseño del sensor (sonda o resonador plano adaptado a la piel), protocolo clínico y un modelo predictivo informado según TRIPOD-AI.
- **Fortaleza propia:** la combinación de instrumentación y modelado clínico con ML.

---

## 8. Criterios de continuidad (go / no-go)

| Paso | Condición para continuar | Si no se cumple |
|---|---|---|
| Art. 1 → Art. 2 | Existe un rango de al menos ~1 década de frecuencia con error dentro del umbral fijado | Publicar el Art. 1 como caracterización de límites; revisar el diseño de la sonda |
| Art. 2 → Art. 3 | Al menos dos pares de tejidos con distinto contenido de agua se separan con significación más allá de la incertidumbre | Publicar el Art. 2 como evidencia de las limitaciones; reorientar el Art. 3 a contrastes mayores |

---

## 9. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| Sensibilidad insuficiente a baja frecuencia | Acotar el rango; valorar una sonda de mayor diámetro |
| Inestabilidad del cable | Cable corto, fijado, y cuantificar el efecto como factor |
| Errores de contacto en sólidos | Control de presión, varias repeticiones, criterio de rechazo definido a priori |
| Ausencia de VNA de banco | Validación con líquidos de referencia (suficiente para publicar); buscar una sesión puntual en un grupo de RF o antenas |
| Un solo NanoVNA | Declararlo como limitación; pedir unidades prestadas para estimar la variabilidad entre unidades |

---

## 10. Plan de trabajo orientativo

| Meses | Tarea |
|---|---|
| 1 | Búsqueda bibliográfica sistemática; fabricación de la sonda y el soporte; código de adquisición |
| 2 | Pruebas piloto: deriva, calentamiento y rango útil preliminar |
| 3–4 | Campaña completa del Artículo 1; análisis de incertidumbre |
| 5 | Redacción y envío del Artículo 1 (y preprint) |
| 6–8 | Campaña de tejidos ex vivo; dataset; redacción del Artículo 2 |
| En paralelo | Contacto con un colaborador clínico para definir el Artículo 3 |

---

## 11. Primeros pasos concretos

1. Hacer una búsqueda en Scopus/WoS con combinaciones de: *open-ended coaxial probe*, *low-cost VNA*, *NanoVNA*, *dielectric spectroscopy*, *biological tissue*, *uncertainty*. Guardar los trabajos más cercanos para delimitar la novedad.
2. Fabricar la primera sonda SMA y medir aire, cortocircuito y agua para comprobar que la cadena funciona.
3. Escribir el script de adquisición (Python) que guarde .s1p con metadatos automáticamente.
4. Hacer la prueba de deriva de 3 horas: es el primer resultado útil y condiciona todo el protocolo.
5. Fijar por escrito los umbrales de error y los criterios de rechazo **antes** de la campaña principal.

---

## 12. Referencias de partida

Datos bibliográficos comprobados en Crossref o en la propia fuente el 1 de octubre de 2026.

- Gabriel, C., Gabriel, S., Corthout, E. (1996). The dielectric properties of biological tissues: I. Literature survey. *Physics in Medicine and Biology*, 41(11), 2231–2249. doi:10.1088/0031-9155/41/11/001
- Gabriel, S., Lau, R. W., Gabriel, C. (1996). The dielectric properties of biological tissues: II. Measurements in the frequency range 10 Hz to 20 GHz. *Physics in Medicine and Biology*, 41(11), 2251–2269. doi:10.1088/0031-9155/41/11/002
- Gabriel, S., Lau, R. W., Gabriel, C. (1996). The dielectric properties of biological tissues: III. Parametric models for the dielectric spectrum of tissues. *Physics in Medicine and Biology*, 41(11), 2271–2293. doi:10.1088/0031-9155/41/11/003
- Gabriel, C., Peyman, A. (2006). Dielectric measurement: error analysis and assessment of uncertainty. *Physics in Medicine and Biology*, 51(23), 6033–6046. doi:10.1088/0031-9155/51/23/006
- Kaatze, U. (1989). Complex permittivity of water as a function of frequency and temperature. *Journal of Chemical & Engineering Data*, 34(4), 371–374. doi:10.1021/je00058a001
- Stuchly, M. A., Stuchly, S. S. (1980). Coaxial line reflection methods for measuring dielectric properties of biological substances at radio and microwave frequencies — a review. *IEEE Transactions on Instrumentation and Measurement*, 29(3), 176–183. doi:10.1109/tim.1980.4314902
- Marsland, T. P., Evans, S. (1987). Dielectric measurements with an open-ended coaxial probe. *IEE Proceedings H*, 134(4), 341–349. doi:10.1049/ip-h-2.1987.0068
- La Gioia, A., et al. (2018). Open-ended coaxial probe technique for dielectric measurement of biological tissues: challenges and common practices. *Diagnostics*, 8(2), 40. doi:10.3390/diagnostics8020040
- Farrugia, L., et al. (2024). The complex permittivity of biological tissues: a practical measurement guideline. *IEEE Access*, 12, 10296–10314. doi:10.1109/access.2024.3352728
- Peyman, A., Gabriel, C., Grant, E. H. (2007). Complex permittivity of sodium chloride solutions at microwave frequencies. *Bioelectromagnetics*, 28(4), 264–274. doi:10.1002/bem.20271
- Gregory, A. P., Clarke, R. N. (2012). *Tables of the complex permittivity of dielectric reference liquids at frequencies up to 5 GHz*. NPL Report MAT 23, enero de 2012 (sustituye al informe CETM 33 de 2001). https://eprintspublications.npl.co.uk/4347/
- JCGM 100:2008 (GUM) y JCGM 101:2008 (Monte Carlo).
- IT'IS Foundation. Tissue properties database.
- Linha, Z., et al. (2025). An inexpensive system for measuring the dielectric properties of biological tissues using an open-ended coaxial probe. *IEEE Transactions on Instrumentation and Measurement*, 74. doi:10.1109/tim.2025.3561426
- Małek, A., Piekarz, I., Sorocki, J. (2026). Low-cost system for broadband dielectric spectroscopy of residue-forming liquids using plug-and-measure planar microwave sensor. *IEEE Transactions on Microwave Theory and Techniques*, 74(5), 4458–4473. doi:10.1109/tmtt.2026.3664936
- González-Teruel, J. D., et al. (2022). Measurement of the broadband complex permittivity of soils in the frequency domain with a low-cost vector network analyzer and an open-ended coaxial probe. *Computers and Electronics in Agriculture*, 195, 106847. doi:10.1016/j.compag.2022.106847
- Schiavoni, R., et al. (2023). Microwave reflectometry sensing system for low-cost in-vivo skin cancer diagnostics. *IEEE Access*, 11, 13918–13928. doi:10.1109/access.2023.3243843
- Erkoreka, A., Martinez-Perdiguero, J. (2024). Development of a high-frequency dielectric spectrometer using a portable vector network analyzer. arXiv:2402.00498. NanoVNA V2 con condensador de placas paralelas, 10 MHz–1 GHz, cristal líquido.
