# Hardware

Todo lo que aparece aquí forma parte del método y se publicará como hardware abierto con el Artículo 1.

## Equipo

| Elemento | Identificación | Notas |
|---|---|---|
| VNA | NanoVNA-F V2 — n.º de serie: (comando `SN`) · firmware: 0.5.0, compilado el 24 de junio de 2022 | Consola de texto por USB (pynanovna). 101 puntos por barrido como máximo; sin control de ancho de banda de FI por USB. Ranuras de calibración guardadas: 0 (50 kHz–3 GHz), 1–3 (100 MHz–1,5 GHz), 4 (1–100 MHz), 5 (100 kHz–1,5 GHz) |
| Kit SOL | | ¿Del fabricante o caracterizado? |
| Cables | Ninguno en la configuración de partida: la sonda v1 se enrosca al puerto | Los latiguillos que se prueben después se anotan aquí con tipo, longitud y conectores |
| Termómetro | | Resolución e incertidumbre |
| Conductímetro | | |
| Balanza | | Para las disoluciones por pesada |

## Sondas (`sonda/`)

Una carpeta por sonda (`sonda/v1/`…) con fotos, dimensiones medidas y fecha de fabricación.

| Id | Tipo | Ø conductor interior | Ø interior del exterior | Dieléctrico | Estado |
|---|---|---|---|---|---|
| [v1](sonda/v1/README.md) | Adaptador rígido SMA macho–N macho, con el lado N rebajado | por medir | por medir (≈ 7 mm) | PTFE | por comprar; para líquidos y la parte baja de la banda |
| v2 | Semirrígido de 0,141″ o SMA de panel | | | PTFE | prevista; para la parte alta de la banda y para tejido |

## Soporte (`soporte/`)

Planos o archivos de impresión, y la forma de fijar el cable y la sonda. Para el Artículo 2 se añade
la célula de carga (HX711 + galga).

## Lista de materiales

| Elemento | Referencia | Proveedor | Coste |
|---|---|---|---|
| Adaptador rígido SMA macho–N macho, 2 unidades (sonda v1) | TUOLNK, B0BGSB1PQH | Amazon | por anotar |
| Latiguillos SMA macho–hembra de varios tipos y longitudes (factor cable) | por elegir | | |
