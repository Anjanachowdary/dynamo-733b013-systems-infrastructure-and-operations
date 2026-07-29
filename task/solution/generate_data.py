#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'environment'
DATA_DIR = ROOT / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

records = [
    {'record_id': '1', 'customer_id': 'C001', 'category': 'customer_records', 'region': 'EU', 'created_date': '2020-01-15'},
    {'record_id': '2', 'customer_id': 'C002', 'category': 'customer_records', 'region': 'US', 'created_date': '2021-02-20'},
    {'record_id': '3', 'customer_id': 'C003', 'category': 'financial', 'region': 'APAC', 'created_date': '2019-03-10'},
    {'record_id': '4', 'customer_id': 'C004', 'category': 'healthcare', 'region': 'US', 'created_date': '2015-05-05'},
    {'record_id': '5', 'customer_id': 'C005', 'category': 'healthcare', 'region': 'APAC', 'created_date': '2014-07-20'},
    {'record_id': '6', 'customer_id': 'C006', 'category': 'customer_records', 'region': 'EU', 'created_date': '2018-11-30'},
    {'record_id': '7', 'customer_id': 'C007', 'category': 'financial', 'region': 'US', 'created_date': '2017-09-01'},
    {'record_id': '8', 'customer_id': 'C008', 'category': 'customer_records', 'region': 'APAC', 'created_date': '2022-08-02'},
    {'record_id': '9', 'customer_id': 'C009', 'category': 'financial', 'region': 'EU', 'created_date': '2021-10-10'},
    {'record_id': '10', 'customer_id': 'C010', 'category': 'healthcare', 'region': 'EU', 'created_date': '2017-12-12'},
]

holds = [
    {'hold_id': 'H1', 'record_id': '4', 'start_date': '2025-01-01', 'end_date': '2026-12-31', 'reason': 'litigation'},
    {'hold_id': 'H2', 'record_id': '6', 'start_date': '2024-01-01', 'end_date': '2026-06-30', 'reason': 'investigation'},
    {'hold_id': 'H3', 'record_id': '9', 'start_date': '2023-01-01', 'end_date': '2026-06-01', 'reason': 'regulatory_review'},
]

withdrawals = [
    {'customer_id': 'C002', 'withdrawal_date': '2026-06-20'},
    {'customer_id': 'C004', 'withdrawal_date': '2026-06-15'},
    {'customer_id': 'C008', 'withdrawal_date': '2026-06-25'},
]

policy = {
    'audit_date': '2026-07-01',
    'default_retention_periods': {
        'customer_records': {'EU': 5, 'US': 7, 'APAC': 3},
        'financial': {'EU': 4, 'US': 6, 'APAC': 5},
        'healthcare': {'EU': 6, 'US': 8, 'APAC': 4},
    },
    'statutory_minimums': {
        'customer_records': {'EU': 7, 'US': 5, 'APAC': 4},
        'financial': {'EU': 5, 'US': 7, 'APAC': 6},
        'healthcare': {'EU': 8, 'US': 10, 'APAC': 5},
    },
    'consent_withdrawal_acceleration_days': 30,
    'legal_hold_override': True,
}

with (DATA_DIR / 'records.csv').open('w', newline='', encoding='utf-8') as handle:
    writer = csv.DictWriter(handle, fieldnames=['record_id', 'customer_id', 'category', 'region', 'created_date'])
    writer.writeheader()
    writer.writerows(records)

with (DATA_DIR / 'legal_holds.csv').open('w', newline='', encoding='utf-8') as handle:
    writer = csv.DictWriter(handle, fieldnames=['hold_id', 'record_id', 'start_date', 'end_date', 'reason'])
    writer.writeheader()
    writer.writerows(holds)

with (DATA_DIR / 'consent_withdrawals.csv').open('w', newline='', encoding='utf-8') as handle:
    writer = csv.DictWriter(handle, fieldnames=['customer_id', 'withdrawal_date'])
    writer.writeheader()
    writer.writerows(withdrawals)

(ROOT / 'policy.json').write_text(json.dumps(policy, indent=2), encoding='utf-8')
