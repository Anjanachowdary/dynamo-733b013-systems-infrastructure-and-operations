import csv
import json
from pathlib import Path


def _resolve_root() -> Path:
    app_root = Path('/app')
    if (app_root / 'policy.json').exists() and (app_root / 'data' / 'records.csv').exists():
        return app_root
    return Path(__file__).resolve().parents[1] / 'environment'


ROOT = _resolve_root()
OUTPUT_PATH = ROOT / 'output' / 'violations.csv'
POLICY_PATH = ROOT / 'policy.json'
EXPECTED_PATH = Path('/tests/expected_violations.csv') if Path('/tests/expected_violations.csv').exists() else Path(__file__).resolve().parents[0] / 'expected_violations.csv'


def _load_policy():
    return json.loads(POLICY_PATH.read_text(encoding='utf-8'))


def _load_output():
    assert OUTPUT_PATH.exists(), 'missing /app/output/violations.csv'
    with OUTPUT_PATH.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def _load_expected():
    with EXPECTED_PATH.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def test_output_file_exists_and_is_csv():
    """The output file must exist and have the exact schema required by the instruction."""
    rows = _load_output()
    assert rows, 'violations.csv should contain at least one row'
    assert set(rows[0].keys()) == {'record_id', 'customer_id', 'category', 'region', 'created_date', 'effective_retention_years', 'delete_after', 'violation_reason'}


def test_reported_rows_match_oracle_exactly():
    """The verifier must match the hidden oracle rows exactly, including dates and violation reasons."""
    rows = _load_output()
    expected = _load_expected()
    assert rows == expected


def test_policy_is_visible_to_agent():
    """The agent-visible policy file must be present and contain the required retention rules."""
    policy = _load_policy()
    assert 'default_retention_periods' in policy
    assert 'statutory_minimums' in policy
    assert 'consent_withdrawal_acceleration_days' in policy
    assert policy.get('hold_tolling_behavior') == 'extend_deadline_to_hold_end'
