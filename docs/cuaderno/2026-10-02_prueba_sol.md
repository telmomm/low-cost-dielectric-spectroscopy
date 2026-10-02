# 2026-10-02 — Primera prueba con el equipo y calibración SOL por software

- **Objetivo:** comprobar la cadena de adquisición con el NanoVNA real y la corrección SOL por software.
- **Campaña:** `prueba_sol` (`data/raw/prueba_sol/20261002/`), identificador `sol_20261002T080408Z`.
- **Equipo:** NanoVNA-F V2, firmware 0.5.0. Patrones SOL conectados directamente al puerto, sin cable ni sonda.
- **Calibración del firmware:** activa («load open short cal'ed»); por los datos, hecha entre 100 MHz y 1,5 GHz.
- **Barrido:** 50 kHz–1,45 GHz en cinco tramos de 101 puntos (501 puntos, unos 24 s por barrido).

## Medidas

| Hora (UTC) | Patrón | Repeticiones | Incidencias |
|---|---|---|---|
| 08:04–08:06 | abierto | 5 | — |
| 08:12–08:14 | corto | 5 | — |
| 08:14–08:16 | carga | 5 | — |

Una tanda anterior (07:24 UTC) se descartó: en corto y carga las repeticiones no coincidían entre sí
porque el patrón se cambió con la medida en marcha. Sus barridos no se conservan.

## Qué ha salido

Tramos: 0,05–1, 1–10, 10–100, 100–1000 y 1000–1450 MHz.

| | 0,05–1 | 1–10 | 10–100 | 100–1000 | 1000–1450 |
|---|---|---|---|---|---|
| Repetibilidad de abierto y corto (dB) | −62 | −60 | −59 | −54 | −46 |
| Repetibilidad de la carga (dB) | −64 | −63 | −61 | −68 | −65 |
| Residuo mediano tras corregir, abierto (dB) | −62 | −64 | −65 | −55 | −46 |
| Residuo mediano tras corregir, carga (dB) | −64 | −65 | −65 | −68 | −65 |
| \|S11\| del abierto tal como lo entrega el firmware | 1,12 | 1,29 | 1,86 | 1,006 | 1,004 |

- **La SOL por software funciona en toda la banda**, también por debajo de 100 MHz, donde la
  calibración del firmware da valores sin sentido. Dejando fuera una repetición, el residuo mediano
  queda entre −58 y −66 dB, y no depende de qué repetición se deje fuera.
- **El residuo es compatible con la repetibilidad.** Cae dentro de la incertidumbre propagada al 95 %
  en el 87–88 % de los puntos; con cuatro repeticiones lo esperable solo por ruido es un 86 %. No hay
  indicios de deriva dentro de los dos minutos de cada serie.
- **El ruido es proporcional a la señal.** Con abierto y corto la repetibilidad empeora de −62 a −46 dB
  al subir la frecuencia; con la carga se queda en torno a −65 dB. Con la sonda, que refleja casi todo,
  mandará el caso desfavorable: en torno al 0,5 % de Γ entre 1 y 1,45 GHz.
- **Hay saltos esporádicos.** En un 7–9 % de los puntos de abierto y corto, una o dos repeticiones se
  apartan de las demás en torno a 0,1, en bloques de frecuencias contiguas (por ejemplo 0,78–0,85 MHz
  o cerca de 29 MHz). Explican los picos de hasta −23 dB del residuo. Con la carga casi no aparecen.

Lo que esta prueba no dice: la exactitud. Los patrones se suponen ideales y no se reconectaron entre
repeticiones, así que solo mide repetibilidad a corto plazo.

## Qué cambia para la próxima sesión

- Investigar los saltos: probar a pausar el barrido continuo del equipo antes de leer, y comparar media
  y mediana de las repeticiones.
- Repetir reconectando el patrón entre repeticiones, para separar la repetibilidad de la conexión.
- Dejar pasar tiempo entre los patrones y la medida para ver la deriva (piloto de vida de la calibración).
