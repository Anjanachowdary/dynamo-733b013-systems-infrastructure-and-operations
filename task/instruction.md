There is a synthetic corporate records compliance dataset at /app/data/, and a normative policy at /app/policy.json. Analyze the records, legal-hold windows, and consent withdrawal dates against the policy using the fixed audit date 2026-07-01.

Resolve the rules in the following precedence order: Litigation Hold > Statutory Minimum Floor > Consent Withdrawal Acceleration > Default Retention Period. A record is overdue for deletion when its effective deletion date is on or before the audit date.

Write the result as a CSV file at /app/output/violations.csv with exactly these columns, in this order: record_id,customer_id,category,region,created_date,effective_retention_years,delete_after,violation_reason.

The output must be sorted by record_id in ascending order. The violation_reason field must be one of the following values: retention_period_expired, consent_withdrawal_accelerated, legal_hold_override, statutory_floor_applied, hold_tolling_applied.

Interpret the policy precisely:
- A legal hold is only active for the date window stated in the hold record. A hold that ends before the audit date does not protect the record at audit time.
- A record can have multiple hold windows. The solver must reconcile all active hold windows and use the latest active hold end date as the deadline extension point.
- If a record is under an active hold, the retention clock is suspended while the hold is active; the deletion deadline is extended to the latest active hold end date, not the original retention anniversary.
- If a consent withdrawal occurs after the record's creation date and before the effective deletion date, the deletion deadline is accelerated by the policy-defined number of days.
- If both a hold and a consent withdrawal apply, the hold dominates because it pauses the retention clock and extends the deadline; consent withdrawal only accelerates the deadline when no active hold is present.

Use the policy and the provided data files directly; do not hardcode the expected rows.
