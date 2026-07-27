import csv
from pathlib import Path

def _resolve_root() -> Path:
    app_root = Path('/app')
    if (app_root / 'policy.md').exists() and (app_root / 'data' / 'records.csv').exists():
        return app_root
    return Path(__file__).resolve().parents[1] / 'environment'


ROOT = _resolve_root()
OUTPUT_PATH = ROOT / 'output' / 'violations.csv'
POLICY_PATH = ROOT / 'policy.md'
EXPECTED_PATH = Path('/tests/expected_violations.csv') if Path('/tests/expected_violations.csv').exists() else Path(__file__).resolve().parents[0] / 'expected_violations.csv'


def _load_policy():
    return POLICY_PATH.read_text(encoding='utf-8')


def _load_output():
    assert OUTPUT_PATH.exists(), 'missing /app/output/violations.csv'
    with OUTPUT_PATH.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def _load_expected():
    with EXPECTED_PATH.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def test_output_file_exists_and_is_csv():
    """instruction.md success criteria 1 and 2: output file must exist and contain the expected columns."""
    rows = _load_output()
    assert rows, 'violations.csv should contain at least one row'
    assert set(rows[0].keys()) == {'record_id', 'customer_id', 'category', 'region', 'created_date', 'retention_years', 'delete_after', 'reason'}


def test_reported_record_set_matches_policy():
    """instruction.md success criteria 3: only records overdue for deletion and not protected by an active hold are reported."""
    rows = _load_output()
    expected = _load_expected()
    assert len(rows) == len(expected)
    assert {row['record_id'] for row in rows} == {row['record_id'] for row in expected}


def test_reported_row_details_are_correct():
    """instruction.md success criteria 4: the reported row values and reason match the policy and input data."""
    rows = _load_output()
    expected = _load_expected()
    assert rows == expected


def test_policy_is_visible_to_agent():
    """The agent-visible policy file must be present and contain the required retention rules."""
    policy = _load_policy()
    assert 'retention' in policy.lower()
    assert 'legal hold' in policy.lower()
    assert 'consent withdrawal' in policy.lower()
