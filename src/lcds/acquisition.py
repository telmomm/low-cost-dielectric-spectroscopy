"""Adquisición con el NanoVNA-F V2.

Reparto de papeles, el mismo que en el proyecto nanovna-calibration:

- pynanovna habla con el equipo por USB (rfmeasurement deja los drivers fuera de su alcance);
- rfmeasurement aporta el contexto de la medida, el informe de validación y el registro de
  trazabilidad de la adquisición;
- lcds.metadata guarda el barrido en bruto con sus metadatos.

El S11 que el equipo entrega por USB ya viene corregido por la calibración SOL que esté cargada
en el firmware. Eso es lo que se guarda, sin más corrección por software, y `cal_sol_id`
identifica qué calibración del firmware estaba cargada. Esa calibración no debe cambiar entre
la terna de la sonda (corto, aire, agua) y las muestras que se convierten con ella.
"""

from datetime import datetime, timezone

import numpy as np
import skrf as rf
from rfmeasurement.domain import Measurement, MeasurementContext, MetadataConfidence
from rfmeasurement.domain import ValidationResult, ValidationStatus
from rfmeasurement.validation import DEFAULT_RULES, PassivityRule, ValidationRule, validate

from .metadata import guardar_medida
from .paths import RAW
from .provenance import a_dict, registrar

INSTRUMENTO = "NanoVNA-F V2"

# pynanovna limita este equipo a 101 puntos por barrido, así que la banda completa se cubre por
# tramos. Provisional: la configuración definitiva se fija en la puerta G1 del ROADMAP.
SEGMENTOS = ((50e3, 1e6), (1e6, 10e6), (10e6, 100e6), (100e6, 1e9), (1e9, 3e9))
PUNTOS_POR_SEGMENTO = 101


class PasividadUnPuerto(ValidationRule):
    """Pasividad de una red de un puerto: |S11| <= 1.

    Sustituye a PassivityRule de rfmeasurement 0.1.0, que da FAIL en cualquier red de un puerto
    porque Network.passivity de scikit-rf no está definida para ellas. Retirar cuando se
    corrija en rfmeasurement.
    """

    identifier = PassivityRule.identifier
    description = "El módulo de S11 no supera la unidad a ninguna frecuencia."

    def __init__(self, tol=1e-6):
        self.tol = tol

    def is_applicable(self, measurement):
        return measurement.data.nports == 1

    def _evaluate(self, measurement):
        maximo = float(np.max(np.abs(measurement.data.s)))
        pasiva = maximo <= 1 + self.tol
        return ValidationResult(
            rule_id=self.identifier,
            status=ValidationStatus.PASS if pasiva else ValidationStatus.FAIL,
            description=self.description,
            evidence={"max_abs_s11": maximo, "tolerance": self.tol},
            explanation=None if pasiva else "|S11| supera la unidad en alguna frecuencia.",
        )


REGLAS = tuple(
    PasividadUnPuerto() if isinstance(regla, PassivityRule) else regla for regla in DEFAULT_RULES
)


def conectar(puerto=None):
    """Abre el NanoVNA. Con varios equipos conectados, `puerto` elige cuál (p. ej. '/dev/cu.usbmodem…')."""
    import pynanovna  # dependencia opcional: solo hace falta con el equipo delante
    from pynanovna.hardware import Hardware as hw

    interfaces = hw.get_interfaces()
    if not interfaces:
        raise RuntimeError("No se detectó ningún NanoVNA. Comprueba USB y alimentación.")
    indice = 0
    if puerto is not None:
        puertos = [interfaz.port for interfaz in interfaces]
        if puerto not in puertos:
            raise ValueError(f"Puerto no encontrado: {puerto}. Disponibles: {puertos}")
        indice = puertos.index(puerto)

    vna = pynanovna.VNA(vna_index=indice, logging_level="critical")
    if not getattr(vna, "connected", False) or getattr(vna, "vna", None) is None:
        desconectar(vna)
        raise RuntimeError(
            "pynanovna encontró el puerto pero no pudo inicializar el equipo. "
            "Cierra otros programas que lo estén usando y vuelve a intentarlo."
        )
    return vna


def desconectar(vna):
    """Cierra el puerto serie, igual que en nanovna-calibration (vale también tras una conexión a medias)."""
    interfaz = getattr(vna, "iface", None)
    if interfaz is not None:
        try:
            interfaz.close()
        except Exception:
            pass


def barrer(vna, segmentos=SEGMENTOS, n_puntos=PUNTOS_POR_SEGMENTO):
    """Barre los tramos y devuelve (f_hz, s11) sobre una malla creciente y sin puntos repetidos."""
    f, s11 = [], []
    for inicio, fin in segmentos:
        vna.set_sweep(int(inicio), int(fin), n_puntos)
        s11_tramo, _, f_tramo = vna.sweep()
        f.append(np.asarray(f_tramo, dtype=float))
        s11.append(np.asarray(s11_tramo, dtype=complex))
    f, s11 = np.concatenate(f), np.concatenate(s11)
    f, unicos = np.unique(f, return_index=True)  # los extremos de tramos contiguos coinciden
    return f, s11[unicos]


def a_measurement(f_hz, s11, medida):
    """Envuelve el barrido en un Measurement de rfmeasurement, con el contexto de `medida`."""
    f_hz = np.asarray(f_hz, dtype=float)
    red = rf.Network(
        frequency=rf.Frequency.from_f(f_hz, unit="hz"),
        s=np.asarray(s11, dtype=complex).reshape(-1, 1, 1),
        z0=50,
        name=f"{medida.muestra}_r{medida.repeticion:02d}",
    )
    confianza = {
        "frequency_range_hz": MetadataConfidence.MEASURED,
        "instrument": MetadataConfidence.SPECIFIED,
        "calibration": MetadataConfidence.SPECIFIED,  # la declara el operador con cal_sol_id
    }
    if medida.temp_muestra_c is not None:
        confianza["temperature_c"] = MetadataConfidence.MEASURED
    contexto = MeasurementContext(
        dut=medida.muestra,
        operator=medida.operador,
        instrument=INSTRUMENTO,
        calibration=f"SOL del firmware ({medida.cal_sol_id or 'sin identificar'})",
        fixture=medida.sonda_id,
        temperature_c=medida.temp_muestra_c,
        averaging=medida.promediado,
        frequency_range_hz=(float(f_hz[0]), float(f_hz[-1])),
        timestamp=datetime.strptime(medida.timestamp_utc, "%Y%m%dT%H%M%SZ").replace(
            tzinfo=timezone.utc
        ),
        confidence=confianza,
    )
    return Measurement(data=red, context=contexto)


def medir(vna, medida, segmentos=SEGMENTOS, n_puntos=PUNTOS_POR_SEGMENTO, raiz=RAW):
    """Barre, valida y guarda. Devuelve (ruta del .s1p, Measurement de rfmeasurement).

    El Measurement lleva el informe de validación y el registro de trazabilidad de la
    adquisición, cuyo record_id queda también en el .json para enlazar los resultados derivados.

    Un fallo de integridad (valores no finitos, malla de frecuencias rota) es un barrido
    defectuoso y no se guarda. Los fallos de las reglas físicas y los avisos de calidad sí se
    guardan, anotados en los metadatos: son evidencia experimental, no motivo de descarte.
    """
    if medida.vna_serie is None or medida.vna_firmware is None:
        info = vna.info()
        medida.vna_serie = medida.vna_serie or str(info.get("Serial Number"))
        medida.vna_firmware = medida.vna_firmware or str(info.get("Version"))

    f_hz, s11 = barrer(vna, segmentos, n_puntos)
    medicion = a_measurement(f_hz, s11, medida)
    medicion.validation = validate(medicion, rules=REGLAS)

    resumen = {r.rule_id: r.status.value for r in medicion.validation.results}
    rotas = [r for r, estado in resumen.items() if r.startswith("integrity.") and estado == "fail"]
    if rotas:
        raise RuntimeError(f"Barrido defectuoso, no se guarda: {rotas}")

    registro = registrar(
        "adquirir_barrido",
        parametros={
            "instrumento": INSTRUMENTO,
            "vna_serie": medida.vna_serie,
            "vna_firmware": medida.vna_firmware,
            "segmentos_hz": [list(tramo) for tramo in segmentos],
            "puntos_por_segmento": n_puntos,
            "cal_sol_id": medida.cal_sol_id,
        },
        notas="S11 corregido por la calibración SOL cargada en el firmware; sin corrección por software",
    )
    medicion.provenance.append(registro)

    ruta = guardar_medida(
        f_hz, s11, medida, raiz=raiz, extra={"validacion": resumen, "procedencia": a_dict(registro)}
    )
    return ruta, medicion
