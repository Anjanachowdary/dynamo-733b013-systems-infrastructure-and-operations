import json
from collections import Counter
from pathlib import Path

REPORT_PATH = Path("/app/report.json")
LOG_PATH = Path("/app/access.log")


def _expected():
    """Independently recompute the expected stats straight from the log file so the verifier never trusts the agent's own numbers."""
    total = 0
    ips = set()
    paths = Counter()
    with open(LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total += 1
            ips.add(line.split()[0])
            quoted = line.split('"')[1]
            parts = quoted.split()
            if len(parts) >= 2:
                paths[parts[1]] += 1
    return total, len(ips), paths.most_common(1)[0][0]


def _load_report():
    """Load the agent's JSON report and fail with a clear message if it is missing or malformed."""
    assert REPORT_PATH.exists(), "no report.json found at /app/report.json"
    return json.loads(REPORT_PATH.read_text())


def test_report_contains_exactly_the_required_fields():
    """instruction.md success criteria 1 and 2: /app/report.json must contain exactly the required schema."""
    data = _load_report()
    assert set(data.keys()) == {"total_requests", "unique_ips", "top_path"}


def test_total_requests_matches_log():
    """instruction.md success criterion 2: total_requests equals the number of requests in /app/access.log."""
    data = _load_report()
    expected_total, _, _ = _expected()
    assert data.get("total_requests") == expected_total, (
        f"expected total_requests={expected_total}, got {data.get('total_requests')}"
    )


def test_unique_ips_matches_log():
    """instruction.md success criterion 3: unique_ips equals the number of distinct client IPs in /app/access.log."""
    data = _load_report()
    _, expected_ips, _ = _expected()
    assert data.get("unique_ips") == expected_ips, (
        f"expected unique_ips={expected_ips}, got {data.get('unique_ips')}"
    )


def test_top_path_matches_log():
    """instruction.md success criterion 4: top_path equals the most frequently requested path in /app/access.log."""
    data = _load_report()
    _, _, expected_top = _expected()
    assert data.get("top_path") == expected_top, (
        f"expected top_path={expected_top!r}, got {data.get('top_path')!r}"
    )
