import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simulator import validate_distribution, simulate_one_run, run_monte_carlo


VALID = pd.DataFrame({
    "demand": [0, 2, 4],
    "probability": [0.2, 0.3, 0.5],
})


def test_valid_distribution():
    result = validate_distribution(VALID)
    assert result["probability"].sum() == pytest.approx(1.0)


def test_invalid_probability_total():
    bad = pd.DataFrame({"demand": [1, 2], "probability": [0.2, 0.2]})
    with pytest.raises(ValueError):
        validate_distribution(bad)


def test_simulation_has_expected_number_of_days():
    result = simulate_one_run(VALID, days=12, seed=7)
    assert len(result) == 12
    assert (result["ending_stock"] >= 0).all()


def test_reproducible_monte_carlo():
    summary_a, results_a = run_monte_carlo(VALID, days=5, replications=10, seed=99)
    summary_b, results_b = run_monte_carlo(VALID, days=5, replications=10, seed=99)
    assert summary_a == summary_b
    pd.testing.assert_frame_equal(results_a, results_b)
