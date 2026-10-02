<!-- Borrador de issue para https://github.com/telmomm/rfmeasurement (plantilla "Feature request").
     El título va en la primera línea; el resto, en los campos de la plantilla. -->

**Title:** Support degrees of freedom (Student-t coverage factors, Welch–Satterthwaite) for Type A sources

## Motivation

`rfmeasurement.uncertainty.coverage_factor` and `expand` always use the Gaussian factor
(k = 1.96 for 95 %). That is only correct when every standard uncertainty is known exactly.
When a Type A source is estimated from a small number of repeated readings, its standard
uncertainty is itself uncertain, and the Gaussian factor produces intervals that are too narrow.

This is the situation in most VNA work: a standard or a DUT is swept 3–10 times and the standard
deviation of those sweeps becomes the `standard_uncertainty` of a `TYPE_A` source. The library
currently has no way to record how many readings that estimate came from, so it cannot correct
for it.

**Reproducer** (rfmeasurement 0.2.0, numpy only): `y = x`, where `x` is the mean of `n` normal
readings and its uncertainty is the experimental standard deviation of the mean. The script
counts how often the 95 % interval from `expand` contains the true value over 20 000 trials.

```python
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
```

| n readings | ν = n − 1 | Coverage obtained | Coverage expected from Student-t with k = 1.96 | k needed for 95 % |
|---|---|---|---|---|
| 3 | 2 | 81.2 % | 81.1 % | 4.30 |
| 5 | 4 | 88.2 % | 87.8 % | 2.78 |
| 10 | 9 | 92.0 % | 91.8 % | 2.26 |
| 30 | 29 | 94.1 % | 94.0 % | 2.05 |
| 100 | 99 | 94.6 % | 94.7 % | 1.98 |

With five sweeps, an interval reported as 95 % covers the true value 88 % of the time.

`docs/uncertainty.md` says the implementation "must avoid presenting a numerical interval as a
generic confidence interval unless its statistical interpretation is actually justified". For
Type A sources with few readings, the current `coverage_probability` stored in `AnalysisResult`
is not justified.

The same applies to `propagate_monte_carlo`: a `NORMAL` source is sampled with its estimated
standard deviation as if it were exact, so `coverage_interval_from_samples` under-covers in the
same way.

Found while using the library in a downstream project (one-port SOL calibration of a NanoVNA,
5 sweeps per standard), where the residual of a held-out sweep fell inside the propagated 95 %
uncertainty at 86–88 % of the frequency points on purely synthetic noise.

## Proposed solution

Follow JCGM 100:2008 Annex G for linear propagation and JCGM 101:2008 clause 6.4.9 for Monte Carlo.

1. **Record the degrees of freedom of a source.** Add `degrees_of_freedom: float | None = None`
   to `UncertaintySource`. `None` means "treated as exactly known" (current behaviour, and the
   usual convention for Type B sources), so existing code keeps working.
2. **Effective degrees of freedom in linear propagation.** Add `effective_degrees_of_freedom`
   to `LinearPropagationResult`, computed with the Welch–Satterthwaite formula (GUM eq. G.2b):
   `ν_eff = u_c⁴ / Σ [(c_i·u_i)⁴ / ν_i]`, with sources whose `degrees_of_freedom` is `None`
   contributing zero to the sum. The formula assumes uncorrelated inputs; when correlated
   sources carry finite degrees of freedom the function should say so rather than return a
   number silently.
3. **Student-t coverage factor.** `coverage_factor(coverage_probability, degrees_of_freedom=None)`
   and `expand(value, standard_uncertainty, coverage_probability, degrees_of_freedom=None)`
   return the t-quantile when degrees of freedom are given and the current Gaussian factor
   otherwise (GUM G.3, Table G.2).
4. **Monte Carlo.** Sample a Type A source with finite degrees of freedom from a scaled and
   shifted t-distribution (JCGM 101, 6.4.9.2) instead of a normal. This could be a new
   `Distribution.STUDENT_T`, or automatic for `NORMAL` sources that declare
   `degrees_of_freedom`.
5. **Reporting.** Store the coverage factor and the effective degrees of freedom in
   `AnalysisResult`, and include them in `build_metadata` and `generate_report`, so a reader can
   tell a k = 1.96 interval from a k = 2.78 one.
6. **Scientific tests.** `tests/scientific/` could check the reproducer above (coverage within
   Monte Carlo error of the nominal probability for small n) and the worked example GUM H.1,
   which reports effective degrees of freedom.

Design question to settle: the t-quantile is not in the Python standard library
(`statistics.NormalDist` has no t counterpart). SciPy provides it and is already installed as a
dependency of scikit-rf, but it would become a direct dependency of rfmeasurement.

## Alternatives considered

- **Leave it to the caller.** Users can compute the t-factor themselves and multiply, which is
  what the downstream project does today. But then `AnalysisResult.coverage_probability` and the
  generated report describe an interval the library did not actually compute, which defeats the
  reproducibility package.
- **Only document the limitation.** A note in `docs/uncertainty.md` and in the `expand`
  docstring saying the Gaussian factor assumes large samples. Cheap, and worth doing regardless,
  but it leaves the common small-n VNA case without a correct answer.
- **A Bayesian treatment** of Type A uncertainty (multiply the standard uncertainty by
  `sqrt((n − 1)/(n − 3))`, as in JCGM 101). Consistent with the Monte Carlo path, but it is
  undefined for n ≤ 3 and departs from the GUM procedure most RF laboratories follow.

## Scope

- [x] I have checked docs/scope.md and believe this is in scope for the core package.
  ("Uncertainty: standard uncertainty; probability distributions; … coverage intervals or
  regions", compatible with the GUM family.)
