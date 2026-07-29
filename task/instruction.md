There is a synthetic corporate records compliance dataset at /app/data/, and a normative policy at /app/policy.json. Analyze the records, legal-hold windows, and consent withdrawal dates against the policy using the fixed audit date 2026-07-01.

Resolve the rules in the following precedence order: Litigation Hold > Statutory Minimum Floor > Consent Withdrawal Acceleration > Default Retention Period. A record is overdue for deletion when its effective deletion date is on or before the audit date.

Write the result as a CSV file at /app/output/violations.csv with exactly these columns, in this order: record_id,customer_id,category,region,created_date,effective_retention_years,delete_after,violation_reason.

The output must be sorted by record_id in ascending order. The violation_reason field must be one of the following values: retention_period_expired, consent_withdrawal_accelerated, legal_hold_override, statutory_floor_applied.

Use the policy and the provided data files directly; do not hardcode the expected rows.
