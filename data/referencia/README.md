# Permitividades de referencia

| Archivo | Líquido | Modelo | Fuente | Comprobado |
|---|---|---|---|---|
| `npl_mat23_metanol.csv` | Metanol, 10–50 °C | Debye simple | Gregory y Clarke, *NPL Report MAT 23* (2012), sección 7 | Transcrito del informe; `tests/test_reference.py` reproduce su tabla de valores a 25 °C |
| `npl_mat23_etanol.csv` | Etanol, 10–50 °C, hasta 5 GHz | Debye-Γ | Ídem | Ídem, a 20 °C |
| (en `src/lcds/reference.py`) | Agua, −4,1 a 60 °C | Debye simple | Kaatze (1989), *J. Chem. Eng. Data* 34(4), 371–374 | Ecuaciones cotejadas con una fuente secundaria que las reproduce (Gezehegn et al., 2021); falta el artículo original |

Informe NPL: <https://eprintspublications.npl.co.uk/4347/>. Sus incertidumbres son expandidas (k = 2) y no
incluyen la de la temperatura (±0,1 °C hasta 35 °C y ±0,2 °C por encima). Entre temperaturas tabuladas
se interpola linealmente, como admite la nota 5 del informe.

Pendiente: disoluciones de NaCl. El modelo previsto es el de Peyman, Gabriel y Grant (2007),
*Bioelectromagnetics* 28(4), 264–274, doi:10.1002/bem.20271; el artículo es de pago y sus
coeficientes no se han podido consultar, así que no se ha implementado nada.
