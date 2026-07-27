#!/usr/bin/env python3
import csv
from datetime import date, datetime
from pathlib import Path

def _resolve_root() -> Path:
    app_root = Path('/app')
    if (app_root / 'policy.md').exists() and (app_root / 'data' / 'records.csv').exists():
        return app_root
    return Path(__file__).resolve().parents[1] / 'environment'


ROOT = _resolve_root()
DATA_DIR = ROOT / 'data'
OUTPUT_DIR = ROOT / 'output'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AUDIT_DATE = date(2026, 1, 1)


def parse_date(value: str) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, '%Y-%m-%d').date()


def load_records() -> list[dict]:
    with (DATA_DIR / 'records.csv').open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def load_holds() -> dict[str, tuple[date, date]]:
    holds: dict[str, tuple[date, date]] = {}
    with (DATA_DIR / 'legal_holds.csv').open(newline='', encoding='utf-8') as handle:
        for row in csv.DictReader(handle):
            holds[row['record_id']] = (parse_date(row['hold_start_date']), parse_date(row['hold_end_date']))
    return holds


def load_policy() -> dict[tuple[str, str], int]:
    policy: dict[tuple[str, str], int] = {}
    for line in (ROOT / 'policy.md').read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line.startswith('- '):
            continue
        item = line[2:]
        if '/' not in item or ':' not in item:
            continue
        category, region_years = item.split('/', 1)
        region, years = region_years.split(':', 1)
        policy[(category.strip(), region.strip())] = int(years.strip().split()[0])
    return policy


def is_active_hold(hold_range: tuple[date | None, date | None]) -> bool:
    start, end = hold_range
    if start is None or end is None:
        return False
    return start <= AUDIT_DATE <= end


def main() -> None:
    records = load_records()
    holds = load_holds()
    policy = load_policy()
    violations = []

    for row in records:
        record_id = row['record_id']
        created_date = parse_date(row['created_date'])
        consent_withdrawal_date = parse_date(row['consent_withdrawal_date'])
        if consent_withdrawal_date and consent_withdrawal_date >= created_date:
            continue

        if record_id in holds and is_active_hold(holds[record_id]):
            continue

        category = row['category']
        region = row['region']
        retention_years = policy.get((category, region))
        if retention_years is None:
            continue

        if created_date is None:
            continue

        delete_after = created_date.replace(year=created_date.year + retention_years)
        if delete_after < AUDIT_DATE:
            violations.append({
                'record_id': record_id,
                'customer_id': row['customer_id'],
                'category': category,
                'region': region,
                'created_date': row['created_date'],
                'retention_years': str(retention_years),
                'delete_after': delete_after.strftime('%Y-%m-%d'),
                'reason': 'retention_period_expired',
            })

    violations.sort(key=lambda item: int(item['record_id']))
    with (OUTPUT_DIR / 'violations.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['record_id', 'customer_id', 'category', 'region', 'created_date', 'retention_years', 'delete_after', 'reason'])
        writer.writeheader()
        writer.writerows(violations)


if __name__ == '__main__':
    main()
