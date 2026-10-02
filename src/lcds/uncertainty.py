"""Incertidumbre de la permitividad con el motor de rfmeasurement (GUM y Monte Carlo).

El motor de rfmeasurement propaga una magnitud real escalar, así que hay un modelo por magnitud
(eps' o sigma) y por frecuencia. Las fuentes son las partes real e imaginaria de los cuatro
coeficientes de reflexión que entran en la conversión bilineal y la temperatura del agua de
calibración. Las demás fuentes del presupuesto (deriva, cable, modelo de inversión) se añaden
aquí a medida que los pilotos las cuantifiquen.
"""

from dataclasses import dataclass, replace

import numpy as np
from rfmeasurement.domain import (
    AnalysisResult,
    Distribution,
    Measurand,
    UncertaintyModel,
    UncertaintySource,
    UncertaintyBudget,
    UncertaintyType,
)
from rfmeasurement.reporting import build_metadata, generate_report
from rfmeasurement.uncertainty import (
    LinearPropagationResult,
    MonteCarloResult,
    build_budget,
    coverage_interval_from_samples,
    propagate_linear,
    propagate_monte_carlo,
)

from .probe import epsilon_bilinear
from .provenance import registrar
from .reference import conductivity, water
from .sol import corregir, terminos_error

GAMMAS = ("muestra", "corto", "aire", "agua")
MAGNITUDES = {
    "eps_real": ("eps'", "Parte real de la permitividad relativa", "1"),
    "sigma": ("sigma", "Conductividad equivalente, w·eps0·eps''", "S/m"),
}


def modelo(f_hz, gammas, u_gammas, temp_agua_c, u_temp_agua_c, magnitud="eps_real"):
    """Modelo de medida de eps' o sigma a una frecuencia.

    gammas, u_gammas  dicts con las claves de GAMMAS: valor complejo y su incertidumbre típica
                      (compleja: parte real e imaginaria por separado, como da lcds.sol.promediar).
    temp_agua_c       temperatura del agua de calibración y su incertidumbre típica.
    """
    nombre, definicion, unidad = MAGNITUDES[magnitud]

    fuentes = []
    for clave in GAMMAS:
        for parte, valor, u in (
            ("re", gammas[clave].real, u_gammas[clave].real),
            ("im", gammas[clave].imag, u_gammas[clave].imag),
        ):
            fuentes.append(
                UncertaintySource(
                    name=f"gamma_{clave}_{parte}",
                    description=f"Parte {parte} del coeficiente de reflexión con {clave}",
                    uncertainty_type=UncertaintyType.TYPE_A,
                    distribution=Distribution.NORMAL,
                    standard_uncertainty=float(u),
                    unit="1",
                    nominal_value=float(valor),
                    assumptions="Repetibilidad de barridos; partes real e imaginaria independientes",
                )
            )
    fuentes.append(
        UncertaintySource(
            name="temp_agua",
            description="Temperatura del agua de calibración",
            uncertainty_type=UncertaintyType.TYPE_B,
            distribution=Distribution.NORMAL,
            standard_uncertainty=float(u_temp_agua_c),
            unit="°C",
            nominal_value=float(temp_agua_c),
            source_reference="Termómetro de la muestra",
        )
    )

    def funcion(v):
        g = {clave: complex(v[f"gamma_{clave}_re"], v[f"gamma_{clave}_im"]) for clave in GAMMAS}
        eps = epsilon_bilinear(
            g["muestra"], g["corto"], g["aire"], g["agua"], water(f_hz, v["temp_agua"])
        )
        return float(eps.real) if magnitud == "eps_real" else float(conductivity(f_hz, eps))

    return UncertaintyModel(
        measurand=Measurand(name=nombre, definition=definicion, unit=unidad, frequency_hz=float(f_hz)),
        function=funcion,
        sources=tuple(fuentes),
        assumptions=(
            "Modelo capacitivo de la sonda (conversión bilineal con corto, aire y agua); agua según "
            "Kaatze (1989); fuentes independientes; sin deriva, cable ni error de modelo."
        ),
    )


GAMMAS_SOL = ("abierto", "corto", "carga", "medida")


def modelo_sol(gammas, u_gammas, parte="re", f_hz=None):
    """Modelo de medida de la parte real o imaginaria de un Gamma corregido por SOL, a una frecuencia.

    gammas, u_gammas  dicts con las claves de GAMMAS_SOL: los tres patrones medidos y la medida a
                      corregir, con su incertidumbre típica compleja (real e imaginaria por
                      separado). Para un patrón promediado, la de la media.
    """
    fuentes = tuple(
        UncertaintySource(
            name=f"gamma_{clave}_{p}",
            description=f"Parte {p} del coeficiente de reflexión medido: {clave}",
            uncertainty_type=UncertaintyType.TYPE_A,
            distribution=Distribution.NORMAL,
            standard_uncertainty=float(getattr(u_gammas[clave], atributo)),
            unit="1",
            nominal_value=float(getattr(gammas[clave], atributo)),
            assumptions="Repetibilidad de barridos; partes real e imaginaria independientes",
        )
        for clave in GAMMAS_SOL
        for p, atributo in (("re", "real"), ("im", "imag"))
    )

    def funcion(v):
        g = {c: np.array([complex(v[f"gamma_{c}_re"], v[f"gamma_{c}_im"])]) for c in GAMMAS_SOL}
        corregido = corregir(g["medida"], *terminos_error(g["abierto"], g["corto"], g["carga"]))[0]
        return float(corregido.real if parte == "re" else corregido.imag)

    return UncertaintyModel(
        measurand=Measurand(
            name=f"{'Re' if parte == 're' else 'Im'}(Gamma corregido)",
            definition="Coeficiente de reflexión tras la corrección SOL de un puerto",
            unit="1",
            frequency_hz=None if f_hz is None else float(f_hz),
        ),
        function=funcion,
        sources=fuentes,
        assumptions=(
            "Patrones SOL ideales (su definición no se incluye como fuente); fuentes independientes; "
            "solo repetibilidad: sin deriva ni reconexión entre los patrones y la medida."
        ),
    )


@dataclass
class Evaluacion:
    """Todo lo que produce `evaluar`, para reportarlo o empaquetarlo sin recalcular."""

    modelo: UncertaintyModel
    resultado: AnalysisResult
    presupuesto: UncertaintyBudget
    monte_carlo: MonteCarloResult
    lineal: LinearPropagationResult


def evaluar(modelo_u, n_muestras=10_000, semilla=42, cobertura=0.95, entradas=()):
    """Propaga por Monte Carlo y construye el presupuesto. Devuelve una Evaluacion.

    El valor, la incertidumbre típica y el intervalo de cobertura salen de Monte Carlo (JCGM 101),
    porque la conversión no es lineal. El presupuesto por fuentes usa los coeficientes de
    sensibilidad de la propagación lineal (JCGM 100). `entradas` son los record_id de los datos
    de partida, para la trazabilidad del resultado.
    """
    mc = propagate_monte_carlo(modelo_u, n_samples=n_muestras, rng=np.random.default_rng(semilla))
    lineal = propagate_linear(modelo_u)
    presupuesto = build_budget(
        modelo_u.measurand, modelo_u.sources, lineal.sensitivity_coefficients, lineal.standard_uncertainty
    )
    intervalo = coverage_interval_from_samples(mc.samples, cobertura)
    resultado = AnalysisResult(
        measurand=modelo_u.measurand,
        value=mc.value,
        unit=modelo_u.measurand.unit,
        provenance=(
            registrar(
                "propagar_incertidumbre",
                entradas=entradas,
                parametros={
                    "metodo": "monte_carlo",
                    "n_muestras": n_muestras,
                    "semilla": semilla,
                    "cobertura": cobertura,
                    "u_lineal": lineal.standard_uncertainty,
                },
            ),
        ),
        standard_uncertainty=mc.standard_uncertainty,
        expanded_uncertainty=(intervalo[1] - intervalo[0]) / 2,
        coverage_probability=cobertura,
        coverage_interval=intervalo,
        contributing_sources=modelo_u.sources,
    )
    return Evaluacion(modelo_u, resultado, presupuesto, mc, lineal)


def _con_historia(medicion, ev, registros):
    """La medida de la muestra con toda la cadena: adquisición, pasos intermedios y propagación."""
    return replace(medicion, provenance=[*medicion.provenance, *registros, *ev.resultado.provenance])


def metadatos(medicion, ev, registros=()):
    """Paquete JSON de un resultado con rfmeasurement.reporting, más el presupuesto por fuentes.

    medicion   Measurement de la muestra, tal como lo devuelve lcds.acquisition.medir.
    registros  registros intermedios (calibración de la sonda, conversión a permitividad…).
    """
    paquete = build_metadata(
        _con_historia(medicion, ev, registros), ev.resultado, model=ev.modelo, monte_carlo=ev.monte_carlo
    )
    paquete["presupuesto"] = [
        {
            "fuente": c.source.name,
            "tipo": c.source.uncertainty_type.value,
            "u_fuente": c.source.standard_uncertainty,
            "unidad_fuente": c.source.unit,
            "coeficiente_sensibilidad": c.sensitivity_coefficient,
            "contribucion": c.contribution,
            "porcentaje_varianza": c.percentage_of_variance,
        }
        for c in ev.presupuesto.ranked
    ]
    paquete["u_lineal"] = ev.lineal.standard_uncertainty
    return paquete


def informe(medicion, ev, registros=()):
    """Informe en Markdown del resultado, generado por rfmeasurement.reporting."""
    return generate_report(
        _con_historia(medicion, ev, registros), ev.resultado, model=ev.modelo, monte_carlo=ev.monte_carlo
    )
