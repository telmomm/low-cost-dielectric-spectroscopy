# Roadmap

Plan de la línea descrita en [linea_investigacion_nanovna_biomedico.md](linea_investigacion_nanovna_biomedico.md),
ajustado con el estado del arte inicial ([docs/SOTA/README.md](docs/SOTA/README.md)).
Mes 1 = octubre de 2026. Las fechas son orientativas; las puertas (G0–G3) no lo son.

## Vista general

| Fase | Cuándo | Qué | Puerta de salida |
|---|---|---|---|
| 0. Arranque | 1.ª semana de octubre | Repositorio, entorno, inventario del equipo | — |
| 1. Novedad | Octubre | Búsqueda sistemática, lectura de competidores, enunciado de novedad | **G0** |
| 2. Cadena mínima | Octubre (en paralelo) | Sonda v1, soporte, adquisición, primera terna aire/corto/agua | Cadena funcionando de extremo a extremo |
| 3. Pilotos | Noviembre | Deriva, vida de la calibración, rango útil, ruido, cable | **G1**: protocolo congelado |
| 4. Campaña Art. 1 | Diciembre – enero | Diseño experimental completo en líquidos | Datos completos y auditados |
| 5. Incertidumbre | Enero – febrero | Presupuesto GUM, Monte Carlo, comparación de modelos | Figura clave del artículo |
| 6. Artículo 1 | Febrero | Redacción, preprint, Zenodo, envío | **G2**: go/no-go hacia tejidos |
| 7. Artículo 2 | Marzo – mayo de 2027 | Tejido ex vivo, dataset, discriminación | **G3**: go/no-go hacia clínica |
| 8. Artículo 3 | En paralelo desde octubre | Colaborador clínico, caso de uso, ética | Se concreta tras G3 |

## Qué cambia respecto al plan inicial

El SOTA no invalida la línea, pero mueve el foco (detalle en `docs/SOTA/README.md`, sección 3):

1. **La validación de un VNA barato con sonda coaxial ya está publicada**, incluso en tejido y en
   *IEEE TIM* (Linha 2025). El Artículo 1 tiene que venderse por el presupuesto de incertidumbre por
   fuentes y el protocolo, no por «funciona». De ahí la puerta G0, que antes no existía.
2. **La banda útil no se puede anticipar con la literatura.** El límite de 500–700 MHz que citan los
   informes es de un nanoVNA-H, que mide con armónicos por encima de 300 MHz; el NanoVNA-F V2 es otro
   diseño y su banda útil hay que medirla (piloto de rango útil).
3. **Dos factores nuevos en el diseño**: vida útil de la calibración (minutos) y modelo de inversión.
4. **La sesión con un VNA de banco pasa de opcional a muy recomendable**: es lo que hacen todos los
   competidores directos.

---

## Fase 0 — Arranque (1.ª semana de octubre)

- [x] Estructura del repositorio y paquete `lcds` con pruebas
- [x] Síntesis del SOTA inicial y matriz de literatura
- [x] `git init`
- [x] Primer commit
- [x] Subir al remoto (https://github.com/telmomm/low-cost-dielectric-spectroscopy), decidiendo antes su visibilidad
- [ ] Inventario del equipo en `hardware/README.md`: número de serie, versión de firmware, kit SOL
- [x] Adquisición en `src/lcds/acquisition.py`: pynanovna para el USB y rfmeasurement para contexto y
      validación, como en `nanovna-calibration`. pynanovna trata el NanoVNA-F V2 con la consola de
      texto de la familia NanoVNA-F, no con el protocolo binario del NanoVNA V2
- [x] Aclarado: el S11 que llega por USB ya viene corregido por la calibración cargada en el firmware
- [x] **Primera prueba con el equipo conectado** (2 de octubre): detectado como NanoVNA-F_V2, firmware
      0.5.0; barrido por tramos, validación y guardado funcionan (501 puntos en unos 24 s)
- [x] Banda de trabajo fijada en 50 kHz–1,45 GHz, la misma que en `nanovna-calibration`. Por encima de
      1,5 GHz el equipo devuelve ceros exactos; queda fuera del alcance
- [x] Calibración por tramos: la SOL se hace por software sobre los mismos tramos, encima de la del
      firmware, que fuera de su intervalo da valores sin sentido
- [x] `scripts/prueba_sol.py` ejecutado con los patrones del kit (2 de octubre): la SOL por software
      funciona en toda la banda; resultado en `docs/cuaderno/2026-10-02_prueba_sol.md`
- [x] Prueba de saltos: pausar el barrido no los quita; son saltos de fase ligados a la posición
      dentro del tramo (`docs/cuaderno/2026-10-02_saltos_y_deriva.md`)
- [x] Saltos con 51 puntos por tramo: van con la posición relativa dentro del tramo (20–35 % de su
      recorrido), no con el número de punto ni con una frecuencia fija
- [x] Saltos con dos juegos de tramos desplazados: la combinación los reduce a la mitad y elimina las
      frecuencias peores, sobre todo por encima de 100 MHz
- [ ] Llevar los dos juegos de tramos y la mediana de repeticiones a la adquisición
- [x] rfmeasurement 0.2.0 desde PyPI (trazabilidad e informes reproducibles)
- [ ] En rfmeasurement: corregir la regla de pasividad para redes de un puerto (ver `docs/DECISIONES.md`)
- [ ] Biblioteca de Zotero para la línea y exportación automática a `PAPER/art1_metrologia/v1/references.bib`

## Fase 1 — Delimitar la novedad (octubre)

Ejecutada el 1 de octubre de 2026; resultado en `docs/SOTA/README.md`, sección 0.

- [x] Búsqueda con las cadenas previstas en OpenAlex, PubMed y arXiv (`docs/SOTA/busqueda.md`)
- [ ] Repetir las cadenas Q1 y Q2 en Scopus y WoS, que piden acceso institucional
- [x] Extraer a `docs/SOTA/matriz_literatura.csv` los 20 trabajos con VNA de bajo coste: 10 a texto
      completo y 10 por el resumen. Ninguno reporta un presupuesto de incertidumbre por fuentes
- [ ] Conseguir y leer los 10 trabajos de pago (sobre todo Rangel 2025, Joof 2024 y Moreno-Merín 2026)
- [x] Comprobar en la fuente primaria las cifras que condicionan el diseño: presión y deshidratación,
      correctas; vida de la calibración, correcta pero sin cuantificar; banda del NanoVNA, no trasladable
      a nuestro equipo
- [x] Resolver las referencias «(verificar)»: Peyman 2007, informe NPL MAT 23 (2012) y arXiv:2402.00498
- [x] Coeficientes de Kaatze (1989) cotejados con una fuente secundaria; metanol y etanol añadidos desde
      el informe NPL, con prueba contra sus tablas
- [ ] Modelo de las disoluciones de NaCl: falta conseguir Peyman et al. (2007)
- [ ] Cotejar los coeficientes del agua con el artículo original de Kaatze
- [x] Reescribir la sección de motivación del documento de la línea
- [x] Segunda pasada con `/phd-skills:gaps` sobre el enunciado de novedad: no aparece ningún trabajo
      que lo contradiga (confianza media)

**G0 — ¿Hay novedad defendible?** Se continúa si ningún trabajo publica ya un presupuesto de
incertidumbre por fuentes (GUM o Monte Carlo) para un sistema NanoVNA + OECP en materiales biológicos.
Si existe, se reorienta el Artículo 1 hacia lo que ese trabajo deje sin cubrir (variabilidad entre
unidades, factores de uso real, estándar de metadatos) antes de fabricar nada más. La decisión se
anota en [docs/DECISIONES.md](docs/DECISIONES.md).

**Estado: superada de forma provisional.** Se confirma al repetir la búsqueda en Scopus y WoS y leer
los trabajos de pago.

## Fase 2 — Cadena de medida mínima (octubre, en paralelo)

- [ ] Sonda v1 (lado N de un adaptador rígido SMA macho–N macho): comprar, rebajar la cara, medir
      dimensiones y hacer fotos (`hardware/sonda/v1/README.md`)
- [ ] Soporte con el cable fijado; lista de materiales en `hardware/README.md`
- [x] Script `scripts/medir_sonda.py`: terna de la sonda y líquidos, de los .s1p a ε′ y σ con su
      incertidumbre y comparación con la referencia. Probado solo en simulado, a falta de la sonda
- [x] SOL por software (`src/lcds/sol.py`), con la formulación de `nanovna-calibration`; queda como
      herramienta auxiliar, porque la SOL de la cadena es la del firmware
- [x] Trazabilidad (`src/lcds/provenance.py`): cada barrido guarda su registro y los resultados
      derivados enlazan con él
- [ ] Decidir el papel de la SOL en el presupuesto: con el modelo capacitivo, la calibración de la sonda
      absorbe la SOL del firmware siempre que no cambie entre la terna y las muestras (ver
      `docs/DECISIONES.md`)
- [ ] Decidir los tramos del barrido: pynanovna da 101 puntos por barrido en este equipo, así que la
      banda se cubre por tramos (ahora, cinco tramos por décadas)
- [ ] Termometría de la muestra (termopar o Pt100) leída por el mismo script
- [ ] Primera terna aire / cortocircuito / agua y un líquido de comprobación; notebook `00_cadena_minima`
- [ ] Decidir el patrón de cortocircuito con `scripts/piloto_corto.py`: lámina de cobre frente a papel de
      aluminio, repetibilidad al recolocarlo y sonda al aire (no necesita líquidos)

**Salida:** un .s1p con metadatos se convierte en ε′ y σ con un solo comando y el resultado en un
líquido no usado para calibrar es físicamente razonable.

## Fase 3 — Pilotos (noviembre)

Cada piloto es un notebook y una entrada en `docs/cuaderno/`.

- [x] **Deriva sin sonda** (`scripts/piloto_deriva.py`), con el equipo ya caliente: sin deriva apreciable
      en una hora por encima de 10 MHz; deriva lenta por debajo (de −60 a −53 dB)
- [ ] **Deriva tras el encendido** (3 h, barridos cada 10–15 min) → tiempo de calentamiento. `01_piloto_deriva`
- [ ] **Vida útil de la calibración** (barridos cada 30–60 s durante 30 min tras calibrar) → cuántas
      medidas caben entre recalibraciones. `02_piloto_vida_calibracion`
- [ ] **Rango útil preliminar** (error frente a frecuencia en un líquido de validación) y margen
      dinámico medido. `03_piloto_rango_util`
- [ ] **Ruido frente a promediado y número de puntos** → configuración del barrido
- [ ] **Cable** fijo frente a flexionado
- [ ] Contactar con un grupo de RF para una sesión con VNA de banco
- [ ] Comprobar con el comité de ética si el tejido de origen alimentario necesita trámite (para la fase 7)

**G1 — Protocolo congelado.** Antes de la campaña quedan escritos en [PROTOCOLO.md](PROTOCOLO.md):
umbrales de error, banda mínima útil, criterios de rechazo, cadencia de recalibración, tamaño de
muestra por factor y orden aleatorizado. A partir de aquí, cualquier cambio se anota como desviación.

## Fase 4 — Campaña del Artículo 1 (diciembre – enero)

- [ ] Preparar las disoluciones de NaCl por pesada y verificarlas con el conductímetro
- [ ] Repetibilidad de la medida (≥ 10 sin recalibrar) y de la calibración (≥ 5 recalibraciones completas)
- [ ] Temperatura: 20, 25, 30 y 37 °C
- [ ] Cable, promediado y resto de factores del protocolo
- [ ] Sesión con el VNA de banco y, si se consiguen, 2–3 unidades de NanoVNA
- [ ] Auditoría de datos: todos los .s1p con metadatos completos, ninguna medida rechazada sin motivo anotado

## Fase 5 — Análisis de incertidumbre (enero – febrero)

- [x] Motor de incertidumbre (`src/lcds/uncertainty.py`) sobre `rfmeasurement.uncertainty`: modelo de
      ε′ y σ por frecuencia, Monte Carlo (JCGM 101) y presupuesto por fuentes. Por ahora con las
      fuentes de repetibilidad de Γ y la temperatura del agua
- [ ] Añadir al modelo las fuentes que cuantifiquen los pilotos: deriva, cable, cortocircuito, modelo
      de inversión y correlación entre parte real e imaginaria de Γ
- [ ] Presupuesto de incertidumbre por fuentes, separando la calibración SOL de la calibración de la sonda
- [ ] `src/lcds/probe.py`: añadir los modelos de radiación y de línea virtual y compararlos sobre los mismos datos
- [ ] Figura clave: error ± incertidumbre expandida (k = 2) frente a frecuencia, con el rango útil sombreado
- [ ] Pasar `/phd-skills:paper-verification` cuando haya cifras en el manuscrito

## Fase 6 — Artículo 1 (febrero)

- [ ] Elegir revista (ver `PAPER/art1_metrologia/Planning.md`) y montar `v1/` con su plantilla
- [ ] Redacción; `/phd-skills:reviewer-defense` antes de enviar
- [ ] Publicar en Zenodo datos, código y diseño de la sonda; preprint
- [ ] Envío

**G2 — Go/no-go hacia tejidos.** Se continúa si existe una banda de al menos una década de frecuencia
con el error dentro del umbral fijado en G1. Si no, el Artículo 1 se publica como caracterización de
límites y se revisa el diseño de la sonda antes de medir tejido.

## Fase 7 — Artículo 2: tejido ex vivo (marzo – mayo de 2027)

- [ ] Soporte con célula de carga (HX711) y registro de la fuerza en los metadatos
- [ ] Piloto de presión, deshidratación y volumen sensible (capas de grosor conocido), dimensionado con
      las cifras del SOTA
- [ ] Protocolo propio del Artículo 2 (`PAPER/art2_tejidos/`), congelado antes de la campaña
- [ ] Campaña: músculo, grasa, hígado, piel y miocardio; varias piezas por tejido y varias
      localizaciones por pieza
- [ ] Comparación con Gabriel (1996) e IT'IS; discriminación con las barras de error del Artículo 1;
      clasificador con validación cruzada por pieza
- [ ] Dataset en Zenodo y envío

**G3 — Go/no-go hacia clínica.** Se continúa si al menos dos pares de tejidos con distinto contenido de
agua se separan más allá de la incertidumbre del sistema.

## Fase 8 — Artículo 3 (en paralelo, sin fecha)

- [ ] Identificar y contactar con un colaborador clínico
- [ ] Acotar el caso de uso con los contrastes que el Artículo 2 demuestre detectables
- [ ] Comité de ética, rediseño del sensor para piel y protocolo según TRIPOD+AI

---

## Riesgos que el SOTA añade

| Riesgo | Señal temprana | Respuesta |
|---|---|---|
| Otro grupo publica el presupuesto de incertidumbre antes | Fase 1; alerta de citas a Linha 2025 y Arias-Rodríguez 2025 | Preprint en cuanto esté la figura clave; reforzar con variabilidad entre unidades |
| La banda útil queda por debajo de una década | Piloto de rango útil | Sonda de mayor diámetro; reformular como caracterización de límites |
| La calibración dura menos de lo que tarda una serie de medidas | Piloto de vida de calibración | Recalibración intercalada; patrón de comprobación entre muestras |
| El modelo capacitivo domina el error | Fase 5, o antes con el líquido de comprobación | Modelo de radiación; restringir la banda |
