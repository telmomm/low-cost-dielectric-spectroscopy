# Búsqueda bibliográfica (fase 1)

Fecha de ejecución: 1 de octubre de 2026.

> **Limitación.** No se ha buscado en Scopus ni en Web of Science, que piden acceso institucional. Las
> cadenas se han ejecutado en índices abiertos (OpenAlex, PubMed y arXiv). Antes de escribir en el
> artículo que «no existe» un trabajo previo, hay que repetir Q1 y Q2 en Scopus y WoS y anotar aquí el
> resultado.

## Cadenas

| Id | Cadena (título y resumen) |
|---|---|
| Q1 | `("open-ended coaxial" OR "coaxial probe") AND ("low-cost" OR "low cost" OR NanoVNA OR "pocket VNA" OR "portable VNA" OR inexpensive) AND (permittivity OR dielectric)` |
| Q2 | Q1 `AND (uncertainty OR GUM OR "Monte Carlo")` |
| Q3 | `NanoVNA AND (permittivity OR dielectric)` |
| Q4 | `("open-ended coaxial" OR "coaxial probe") AND (permittivity OR dielectric) AND ("uncertainty budget" OR "Monte Carlo" OR GUM) AND (tissue OR biological)` |
| Q5 | `(NanoVNA OR "pocket VNA" OR pocketVNA OR "low-cost vector network analyzer" OR "low-cost VNA") AND (uncertainty OR metrological OR "Monte Carlo" OR traceability)` |

Respecto a la cadena del ROADMAP se ha añadido `inexpensive`, que es el término que usa el competidor
más cercano (Linha 2025).

## Resultados

| Cadena | OpenAlex | PubMed | arXiv |
|---|---|---|---|
| Q1 | 107 | 12 | 0 |
| Q2 | 6 | 2 | — |
| Q3 | 24 | 2 | 1 |
| Q4 | 3 | — | — |
| Q5 | 16 | — | — |

OpenAlex: `https://api.openalex.org/works?filter=title_and_abstract.search:<cadena>`. PubMed: E-utilities
`esearch`. arXiv: API de consulta, campo `all`. Los recuentos de OpenAlex incluyen duplicados
(preprint y versión publicada) y bastante ruido de antenas en Q1.

## Cribado

De los resultados de Q1, Q3 y Q5 se han retenido los que miden permitividad (o usan S11 para
caracterizar un material) con un VNA de bajo coste. Son 20 trabajos, recogidos en
[matriz_literatura.csv](matriz_literatura.csv). Diez se han leído a texto completo y diez solo por el
resumen, porque son de pago; la columna `leido` lo indica.

**Q2, Q4 y Q5, las cadenas de incertidumbre, no devuelven ningún trabajo con un presupuesto de
incertidumbre por fuentes para un VNA de bajo coste con sonda coaxial.** Lo que devuelven:

- Q2 (6): Aboyewa 2022 (circuito de RF propio, compara con la incertidumbre de una norma ASTM), La Gioia
  2018 (revisión), Haldes 2025 (modelo de mezclas agua-alcohol) y tres trabajos anteriores a 2009 sin
  relación con VNA de bajo coste.
- Q4 (3): Gabriel y Peyman 2006 (marco de incertidumbre, con equipo de laboratorio), McLaughlin 2009 y
  Naik 2021 (sondas, con VNA de banco).
- Q5 (16): solo tres pertinentes. Yang 2018 (VNA de bajo coste en resonadores cuasiesféricos, metrología
  de gases), Cataldo 2022 (VNA portátil para hidratación de la piel) y Freitas 2025 (VNA sobre SDR).

## Trabajos que la búsqueda añade a los informes de Consensus

| Trabajo | Por qué importa |
|---|---|
| Małek 2026, *IEEE TMTT* | NanoVNA V2.2 con sensor planar. Es lo más cercano a un análisis de incertidumbre de un equipo de esta clase, pero solo de tipo A y con dos componentes |
| Schiavoni 2023, *IEEE Access* | nanoVNA con sonda coaxial truncada **in vivo**, en 11 voluntarios con lesiones de piel |
| Cataldo 2022, *IEEE TIM* | VNA portátil de bajo coste para hidratación de la piel (mismo grupo) |
| Fita 2026, *Foods* | NanoVNA-H4 con sonda de 5 pines, 50–900 MHz, aceites |
| Merla 2018, MeMeA | Sistema portátil de bajo coste con sonda coaxial, líquidos |
| Carmo 2026, LACAP | Sonda coaxial de bajo coste frente a SPEAG DAK hasta 8,5 GHz |
| Repin 2026 | Sonda coaxial con nanoVNA en campo |
| Perrier 2025, *Sensors* | Sonda SMA de bajo coste en disoluciones conductoras hasta 9 GHz (VNA Keysight) |

## Segunda pasada sobre el enunciado de novedad (`/phd-skills:gaps`)

Búsqueda dirigida a encontrar un trabajo que ya publique un presupuesto de incertidumbre para un VNA de
bajo coste, o una caracterización metrológica del propio equipo. Tres búsquedas web y dos cadenas más
en OpenAlex:

- `("open-ended coaxial" OR "coaxial probe") AND (permittivity OR dielectric) AND ("Monte Carlo" OR "uncertainty budget" OR "uncertainty analysis" OR "uncertainty propagation")`: 22 resultados.
- `(NanoVNA OR LibreVNA OR LiteVNA OR pocketVNA OR miniVNA) AND (accuracy OR uncertainty OR drift OR stability) AND (evaluation OR assessment OR comparison OR characterization)`: 15 resultados.

**No aparece ningún trabajo que contradiga el enunciado.** Confianza media: varias formulaciones y tres
índices, pero sin Scopus ni WoS y sin literatura en chino o en ruso.

| Cobertura | Trabajos | Qué cubren | Qué falta |
|---|---|---|---|
| Incertidumbre de la sonda coaxial con VNA de banco | Gabriel y Peyman 2006; Bao 2021 (*IEEE TMTT*); Sharma y Dubey 2022; Wang 2009 (*PIER*) | Marco de errores aleatorios y sistemáticos; incertidumbre del líquido de calibración, deriva y posición de la sonda; presupuesto según IEEE 1528 | Equipos de bajo coste |
| Software abierto para la sonda coaxial | Yoon 2022, PyOECP (*Comput. Phys. Commun.*) | Modelos capacitivo y de antena, líquidos de referencia, ajuste de relajaciones por MCMC | El Monte Carlo es para el ajuste del modelo, no para propagar incertidumbre; VNA Agilent |
| Estabilidad de VNA de bolsillo | Carvajal 2024 (PocketVNA: efecto del calentamiento en S11 de antenas); Linha 2025 (calibración válida ~5 min) | Que el calentamiento y la deriva importan | Cuantificación propagada a permitividad |
| Calibración de VNA compactos | Liu 2026 (*IEEE Access*, LibreVNA, SOLT con patrones no ideales) | Mejora de la calibración con kits baratos | Efecto sobre la permitividad; incertidumbre |
| Incertidumbre con equipo de clase NanoVNA | Małek 2026 (*IEEE TMTT*) | Tipo A, dos componentes, sensor planar | Tipo B, Monte Carlo, sonda coaxial, materiales biológicos |
| **Presupuesto por fuentes, NanoVNA con sonda coaxial, materiales biológicos** | — | — | **Hueco** |

Trabajos que conviene citar y que no estaban en la matriz: Bao et al. 2021 (doi:10.1109/tmtt.2021.3093895),
que es el análisis de incertidumbre más parecido al previsto pero con equipo de banco; Yoon et al. 2022
(doi:10.1016/j.cpc.2022.108517); Carvajal et al. 2024 (doi:10.1109/lacap63752.2024.10876340) y Liu et al.
2026 (doi:10.1109/access.2026.3729596).
