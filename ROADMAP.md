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
2. **La banda útil esperable es más estrecha** de lo que sugiere el rango nominal: el antecedente con
   NanoVNA sitúa el límite fiable en 500–700 MHz.
3. **Dos factores nuevos en el diseño**: vida útil de la calibración (minutos) y modelo de inversión.
4. **La sesión con un VNA de banco pasa de opcional a muy recomendable**: es lo que hacen todos los
   competidores directos.

---

## Fase 0 — Arranque (1.ª semana de octubre)

- [x] Estructura del repositorio y paquete `lcds` con pruebas
- [x] Síntesis del SOTA inicial y matriz de literatura
- [x] `git init`
- [x] Primer commit
- [ ] Subir al remoto (https://github.com/telmomm/low-cost-dielectric-spectroscopy), decidiendo antes su visibilidad
- [ ] Inventario del equipo en `hardware/README.md`: número de serie, versión de firmware, kit SOL
- [ ] **Identificar el protocolo USB del NanoVNA-F V2.** El documento de la línea lo da como compatible
      con las herramientas del NanoVNA V2 (protocolo binario), pero el NanoVNA-F V2 puede usar la consola
      de texto de la familia NanoVNA-F. De esto depende el driver de adquisición; se comprueba
      conectando el equipo y probando NanoVNA-Saver
- [ ] Biblioteca de Zotero para la línea y exportación automática a `PAPER/art1_metrologia/v1/references.bib`

## Fase 1 — Delimitar la novedad (octubre)

- [ ] Búsqueda en Scopus y WoS, guardando cadena, fecha y número de resultados en `docs/SOTA/busqueda.md`.
      Cadena de partida:
      `("open-ended coaxial" OR "coaxial probe") AND ("low-cost" OR "low cost" OR NanoVNA OR "pocket VNA" OR "portable VNA") AND (permittivity OR dielectric)`
      y una segunda con `AND (uncertainty OR GUM OR "Monte Carlo")`
- [ ] Leer completos los 10 competidores directos y rellenar `docs/SOTA/matriz_literatura.csv`.
      Pregunta que hay que responder en cada uno: **¿reporta un presupuesto de incertidumbre por
      fuentes, o solo un error frente a una referencia?**
- [ ] Comprobar en la fuente primaria las cifras del SOTA que condicionan el diseño (banda del NanoVNA,
      vida de la calibración, sensibilidad a la presión)
- [ ] Resolver las referencias «(verificar)»: Peyman 2007, informe NPL MAT 23, arXiv:2402.00498
- [ ] Verificar los coeficientes de Kaatze (1989) de `src/lcds/reference.py` y añadir metanol, etanol y
      NaCl con sus fuentes
- [ ] Reescribir la sección de motivación del documento de la línea
- [ ] Pasar `/phd-skills:gaps` sobre el enunciado de novedad como segunda opinión

**G0 — ¿Hay novedad defendible?** Se continúa si ningún trabajo publica ya un presupuesto de
incertidumbre por fuentes (GUM o Monte Carlo) para un sistema NanoVNA + OECP en materiales biológicos.
Si existe, se reorienta el Artículo 1 hacia lo que ese trabajo deje sin cubrir (variabilidad entre
unidades, factores de uso real, estándar de metadatos) antes de fabricar nada más. La decisión se
anota en [docs/DECISIONES.md](docs/DECISIONES.md).

## Fase 2 — Cadena de medida mínima (octubre, en paralelo)

- [ ] Sonda v1 (SMA de panel o semirrígido de 0,141″), con dimensiones y fotos en `hardware/sonda/`
- [ ] Soporte con el cable fijado; lista de materiales en `hardware/README.md`
- [ ] Driver de adquisición `src/lcds/acquisition.py` y script `scripts/medir.py`, que guarden cada
      barrido con `lcds.metadata.guardar_medida`
- [ ] Termometría de la muestra (termopar o Pt100) leída por el mismo script
- [ ] Primera terna aire / cortocircuito / agua y un líquido de comprobación; notebook `00_cadena_minima`
- [ ] Decidir el patrón de cortocircuito (lámina, papel de aluminio presionado u otro) y medir su repetibilidad

**Salida:** un .s1p con metadatos se convierte en ε′ y σ con un solo comando y el resultado en un
líquido no usado para calibrar es físicamente razonable.

## Fase 3 — Pilotos (noviembre)

Cada piloto es un notebook y una entrada en `docs/cuaderno/`.

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

- [ ] `src/lcds/uncertainty.py`: propagación por Monte Carlo (JCGM 101) de Γ a ε*
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
