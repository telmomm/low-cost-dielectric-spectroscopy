# 2026-10-04 — Piloto del cortocircuito de la sonda v1

- **Objetivo:** elegir el patrón de cortocircuito de la sonda y ver cómo se comporta al aire.
- **Campaña:** `piloto_corto`, tanda `corto_20261004T101910Z` (48 barridos).
- **Equipo:** NanoVNA-F V2, firmware 0.5.0, calibración del firmware activa. Sonda v1 (adaptador SMA–N
  rebajado) enroscada al puerto 1, sin cable.
- **Procedimiento:** seis colocaciones de la lámina de cobre y seis del papel de aluminio, retirando el
  cortocircuito entre una y otra; dos barridos por colocación y la sonda al aire antes de cada una.

## Qué ha salido

**Contacto.** Una colocación cuenta si en todos los tramos de sus dos barridos queda lejos del aire.

| Material | Con contacto | Detalle |
|---|---|---|
| Lámina de cobre | 1 de 6 | Tres colocaciones sin contacto (se parecen al aire, con 13–20° más de desfase por encima de 100 MHz) y dos en las que el contacto se pierde durante la medida |
| Papel de aluminio | 5 de 5 | La primera colocación de la serie se hizo por error con el cobre rígido y no cuenta |

**Repetibilidad**, en % de la distancia entre aire y corto, por tramo (0,05–1, 1–10, 10–100, 100–1000 y
1000–1450 MHz):

| | | | | | |
|---|---|---|---|---|---|
| Ruido de un barrido (aire) | 0,02 | 0,02 | 0,02 | 0,06 | 0,14 |
| Aluminio, entre colocaciones (5) | 0,15 | 0,17 | 0,13 | 0,38 | 0,49 |
| Aluminio, mientras se sujeta | 0,05 | 0,24 | 0,10 | 0,19 | 0,40 |
| Cobre (la colocación buena) frente al aluminio | 1,23 | 0,43 | 0,30 | 2,39 | 3,58 |
| Aire, entre las 12 medidas | 0,32 | 0,19 | 0,27 | 1,53 | 3,17 |

- **El papel de aluminio da un cortocircuito repetible**: por debajo del 0,5 % en toda la banda, unas
  3–7 veces el ruido de un barrido.
- **La lámina de cobre rígida no sirve**: casi nunca hace contacto con el conductor central. La cara de
  la sonda es plana, según la inspección posterior, así que el problema estaría en la lámina (óxido en
  la superficie o falta de planitud), no en la sonda.
- **El aire cambió a mitad de sesión.** Las seis medidas de la serie del cobre coinciden entre sí
  (0,1–0,2 % por encima de 100 MHz) y las seis de la serie del aluminio están desplazadas un 3,6 % entre
  1 y 1,45 GHz y son más dispersas. Algo cambió al pasar al aluminio: restos en la cara, la posición de
  la mano o de algún objeto cerca de la apertura. Sin identificar.

**La sonda al aire frente al corto** (solo por encima de 100 MHz, donde vale la calibración del firmware):
el módulo del cociente es 0,99 y 0,98, y el desfase respecto a 180° es de 16° y 29° en los dos tramos
altos. Equivale a unos 0,7–0,8 pF, o a un retardo de 32–41 ps. Es bastante más de lo que cabe esperar de
una apertura de este tamaño al aire, así que parte tiene que venir de otra cosa: la inductancia del
cortocircuito (1 nH equivale a 0,4 pF) u otra causa sin identificar. El piloto del agua da una segunda
estimación de la capacidad de la apertura, sin cortocircuito, con la que contrastarlo.

## Qué cambia para la próxima sesión

- El cortocircuito de la sonda se hace con papel de aluminio y un respaldo blando.
- Medir las dimensiones de la cara de la sonda y fotografiarla (la planitud ya está comprobada).
- Para la medida al aire: limpiar la cara cada vez y mantener manos y objetos lejos de la apertura.
- Valorar la calibración sin cortocircuito (aire, agua y un tercer líquido), que evita depender de un
  corto que no es ideal.
