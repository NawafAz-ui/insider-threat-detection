"""Simple reference methods (itd/rules.py): definitions, validation-only thresholds, no-skill values, and storage by the engine."""
import json
import os
import subprocess
import sys

os.environ.setdefault("MONGO_URI", "mock")
import numpy as np
import pandas as pd
import pytest

from itd import rules
from itd.features import DEV_FEATURES
from itd.risk import best_f1

ROOT = os.path.dirname(os.path.dirname(__file__))


def _frame(n=40, seed=3):
    rng = np.random.default_rng(seed)
    f = pd.DataFrame({"is_after_hours": rng.integers(0, 2, n), "n_device_connect": rng.integers(0, 3, n),
                      "n_http_leak": rng.integers(0, 2, n)})
    for c in DEV_FEATURES:
        f[c] = rng.normal(0, 1, n)
    return f


def test_scores_follow_their_definitions():
    f = pd.DataFrame({"is_after_hours": [0, 1, 1, 1], "n_device_connect": [2, 0, 1, 0], "n_http_leak": [0, 0, 0, 3]})
    for i, c in enumerate(DEV_FEATURES):
        f[c] = [0.0, float(i), -1.0, 2.5]
    s = rules.rule_scores(f)
    assert s["rule_after_hours"].tolist() == [0, 1, 1, 1]
    assert s["rule_hand_written"].tolist() == [0, 0, 1, 1]           # after hours AND (device OR leak site)
    assert s["rule_deviation"].tolist() == [0.0, 9.0, -1.0, 2.5]     # the largest of the 10 deviations


def test_threshold_is_chosen_on_validation_data_only():
    f = _frame(60)
    y = np.zeros(60, int)
    y[[20, 25, 30, 35, 52, 57]] = 1
    va, te = np.arange(18, 38), np.arange(38, 60)
    m = rules.reference_metrics(f, y, va, te)
    s = rules.rule_scores(f)
    for key in s:
        assert m[key]["threshold"] == pytest.approx(best_f1(y[va], s[key][va])[1])      # not looked at test labels
    changed = y.copy()
    changed[te] = 1 - changed[te]                                     # new test labels must not move any threshold
    again = rules.reference_metrics(f, changed, va, te)
    assert all(again[k]["threshold"] == m[k]["threshold"] for k in s)


def test_no_skill_is_the_flag_everything_reference():
    f = _frame(60)
    y = np.zeros(60, int)
    y[[20, 30, 50, 57]] = 1
    m = rules.reference_metrics(f, y, np.arange(18, 38), np.arange(38, 60))["no_skill"]
    p = 2 / 22
    assert m["precision"] == pytest.approx(p) and m["pr_auc"] == pytest.approx(p) and m["recall"] == 1.0
    assert m["f1"] == pytest.approx(2 * p / (1 + p)) and m["flagged"] == 22 and m["positives"] == 2


def test_metrics_can_be_stored_and_have_the_expected_keys():
    f = _frame(60)
    y = np.zeros(60, int)
    y[[20, 25, 30, 52, 57]] = 1
    m = rules.reference_metrics(f, y, np.arange(18, 38), np.arange(38, 60))
    assert set(m) == set(rules.RULE_NAMES)
    json.dumps(m)                                                    # plain numbers only: MongoDB and the API can hold them
    for v in m.values():
        assert {"precision", "recall", "f1", "pr_auc", "flagged", "positives"} <= set(v)
        assert 0 <= v["precision"] <= 1 and 0 <= v["recall"] <= 1 and v["flagged"] >= 0


def test_engine_stores_the_reference_metrics_with_a_training_run(tmp_path):
    from itd import engine
    from itd.db import get_db
    subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts/generate_synthetic_cert.py"), str(tmp_path / "d"),
                           "--users", "60", "--days", "80", "--insiders", "8"])
    engine.run(str(tmp_path / "d"), retrain=True, report_dir=str(tmp_path / "rep"))
    test = get_db().runs.find_one(sort=[("at", -1)])["metrics"]["test"]
    assert set(rules.RULE_NAMES) <= set(test) and "risk_engine" in test
    assert test["no_skill"]["recall"] == 1.0
    assert test["risk_engine"]["pr_auc"] > test["no_skill"]["pr_auc"]       # the models must beat the floor
    metrics_json = json.load(open(tmp_path / "rep" / "metrics.json"))
    assert "rule_deviation" in metrics_json["test"]
