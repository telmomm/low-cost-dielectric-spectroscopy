"""Empirical coverage of rfmeasurement's 95 % expanded uncertainty when the
standard uncertainty of a Type A source is estimated from n repeated readings."""
import numpy as np
from rfmeasurement.domain import Distribution, Measurand, UncertaintyModel, UncertaintySource, UncertaintyType
from rfmeasurement.uncertainty import expand, propagate_linear

rng = np.random.default_rng(0)
TRUE_VALUE, SIGMA, TRIALS, P = 1.0, 0.1, 20_000, 0.95
measurand = Measurand(name="y", definition="y = x", unit="1")

for n in (3, 5, 10, 30, 100):
    hits = 0
    for _ in range(TRIALS):
        readings = rng.normal(TRUE_VALUE, SIGMA, n)
        source = UncertaintySource(
            name="x", description="mean of n repeated readings",
            uncertainty_type=UncertaintyType.TYPE_A, distribution=Distribution.NORMAL,
            standard_uncertainty=readings.std(ddof=1) / np.sqrt(n), unit="1",
            nominal_value=readings.mean(),
        )
        model = UncertaintyModel(measurand=measurand, function=lambda v: v["x"],
                                 sources=(source,), assumptions="y = x")
        result = propagate_linear(model)
        _, (low, high) = expand(result.value, result.standard_uncertainty, P)
        hits += low <= TRUE_VALUE <= high
    print(f"n = {n:3d}  (nu = {n - 1:2d}):  empirical coverage = {hits / TRIALS:.1%}")
