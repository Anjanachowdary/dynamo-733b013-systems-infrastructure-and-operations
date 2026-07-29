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


def active_hold_window(hold: dict) -> tuple[date, date] | None:
    start_date = parse_date(hold.get('start_date'))
    end_date = parse_date(hold.get('end_date'))
    if start_date is None or end_date is None:
        return None
    if end_date < start_date:
        return None
    return start_date, end_date


def is_active_hold(hold: dict) -> bool:
    window = active_hold_window(hold)
    if window is None:
        return False
    start_date, end_date = window
    return start_date <= AUDIT_DATE <= end_date


def add_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value + timedelta(days=365 * years)


def resolve_retention(record: dict, policy: dict, holds: list[dict], withdrawal_date: date | None) -> tuple[int, date, str | None]:
    category = record['category']
    region = record['region']
    created_date = parse_date(record['created_date'])
    if created_date is None:
        raise ValueError(f"Missing created_date for {record['record_id']}")

    default_period = policy['default_retention_periods'][category][region]
    statutory_floor = policy['statutory_minimums'][category][region]
    consent_acceleration = policy['consent_withdrawal_acceleration_days']

    retention_years = max(default_period, statutory_floor)
    base_delete_after = add_years(created_date, retention_years)
    effective_delete_after = base_delete_after
    reason = 'retention_period_expired'

    if statutory_floor > default_period:
        reason = 'statutory_floor_applied'

    active_hold_end_dates = []
    for hold in holds:
        window = active_hold_window(hold)
        if window is not None:
            start_date, end_date = window
            if start_date <= AUDIT_DATE <= end_date:
                active_hold_end_dates.append(end_date)

    if active_hold_end_dates:
        effective_delete_after = max(base_delete_after, max(active_hold_end_dates))
        reason = 'hold_tolling_applied'
    elif withdrawal_date is not None and created_date <= withdrawal_date < base_delete_after:
        accelerated_date = withdrawal_date + timedelta(days=consent_acceleration)
        if accelerated_date <= AUDIT_DATE:
            effective_delete_after = accelerated_date
            reason = 'consent_withdrawal_accelerated'

    if effective_delete_after <= AUDIT_DATE:
        return retention_years, effective_delete_after, reason

    return retention_years, effective_delete_after, None


def main() -> None:
    records = load_records()
    holds = load_holds()
    withdrawals = load_withdrawals()
    policy = load_policy()

    hold_lookup = {}
    for hold in holds:
        hold_lookup.setdefault(hold['record_id'], []).append(hold)
    violations = []

    for record in records:
        record_id = record['record_id']
        created_date = parse_date(record['created_date'])
        if created_date is None:
            continue

        hold_records = hold_lookup.get(record_id, [])
        withdrawal_date = withdrawals.get(record['customer_id'])
        retention_years, delete_after, violation_reason = resolve_retention(record, policy, hold_records, withdrawal_date)

        if violation_reason is None:
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
