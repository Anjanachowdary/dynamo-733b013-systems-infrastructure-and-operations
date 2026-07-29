#!/usr/bin/env python3
import csv
import json
from datetime import date, datetime, timedelta
from pathlib import Path


def _resolve_root() -> Path:
    app_root = Path('/app')
    if (app_root / 'policy.json').exists() and (app_root / 'data' / 'records.csv').exists():
        return app_root
    return Path(__file__).resolve().parents[1] / 'environment'


ROOT = _resolve_root()
DATA_DIR = ROOT / 'data'
OUTPUT_DIR = ROOT / 'output'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AUDIT_DATE = date(2026, 7, 1)


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, '%Y-%m-%d').date()


def load_records() -> list[dict]:
    with (DATA_DIR / 'records.csv').open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def load_holds() -> list[dict]:
    with (DATA_DIR / 'legal_holds.csv').open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def load_withdrawals() -> dict[str, date]:
    withdrawals: dict[str, date] = {}
    with (DATA_DIR / 'consent_withdrawals.csv').open(newline='', encoding='utf-8') as handle:
        for row in csv.DictReader(handle):
            withdrawals[row['customer_id']] = parse_date(row['withdrawal_date'])
    return withdrawals


def load_policy() -> dict:
    with (ROOT / 'policy.json').open(encoding='utf-8') as handle:
        return json.load(handle)


def is_active_hold(hold: dict, created_date: date) -> bool:
    start_date = parse_date(hold.get('start_date'))
    end_date = parse_date(hold.get('end_date'))
    if start_date is None:
        return False
    if end_date is None:
        return start_date <= AUDIT_DATE
    return start_date <= AUDIT_DATE <= end_date


def add_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value + timedelta(days=365 * years)


def resolve_retention(record: dict, policy: dict, hold: dict | None, withdrawal_date: date | None) -> tuple[int, date, str | None]:
    category = record['category']
    region = record['region']
    created_date = parse_date(record['created_date'])
    if created_date is None:
        raise ValueError(f"Missing created_date for {record['record_id']}")

    default_period = policy['default_retention_periods'][category][region]
    statutory_floor = policy['statutory_minimums'][category][region]
    consent_acceleration = policy['consent_withdrawal_acceleration_days']

    if hold is not None and is_active_hold(hold, created_date):
        return max(default_period, statutory_floor), add_years(created_date, max(default_period, statutory_floor)), 'legal_hold_override'

    retention_years = default_period
    reason = None

    if statutory_floor > retention_years:
        retention_years = statutory_floor
        reason = 'statutory_floor_applied'

    if withdrawal_date is not None and withdrawal_date >= created_date:
        accelerated_date = withdrawal_date + timedelta(days=consent_acceleration)
        if accelerated_date <= AUDIT_DATE:
            return retention_years, accelerated_date, 'consent_withdrawal_accelerated'

    delete_after = add_years(created_date, retention_years)
    return retention_years, delete_after, reason or 'retention_period_expired'


def main() -> None:
    records = load_records()
    holds = load_holds()
    withdrawals = load_withdrawals()
    policy = load_policy()

    hold_lookup = {item['record_id']: item for item in holds}
    violations = []

    for record in records:
        record_id = record['record_id']
        created_date = parse_date(record['created_date'])
        if created_date is None:
            continue

        hold = hold_lookup.get(record_id)
        withdrawal_date = withdrawals.get(record['customer_id'])
        retention_years, delete_after, violation_reason = resolve_retention(record, policy, hold, withdrawal_date)

        if violation_reason == 'legal_hold_override':
            continue

        if delete_after <= AUDIT_DATE:
            violations.append({
                'record_id': record_id,
                'customer_id': record['customer_id'],
                'category': record['category'],
                'region': record['region'],
                'created_date': record['created_date'],
                'effective_retention_years': str(retention_years),
                'delete_after': delete_after.strftime('%Y-%m-%d'),
                'violation_reason': violation_reason,
            })

    violations.sort(key=lambda item: int(item['record_id']))
    with (OUTPUT_DIR / 'violations.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['record_id', 'customer_id', 'category', 'region', 'created_date', 'effective_retention_years', 'delete_after', 'violation_reason'])
        writer.writeheader()
        writer.writerows(violations)


if __name__ == '__main__':
    main()
