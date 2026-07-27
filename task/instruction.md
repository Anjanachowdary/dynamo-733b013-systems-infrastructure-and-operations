There is a retention compliance dataset at /app/data/, and a normative retention policy at /app/policy.md. Use the policy and the provided CSV files to compute, as of 2026-01-01, which records are overdue for deletion and are not protected by an active legal hold. Write the result as a CSV file at /app/output/violations.csv with exactly these columns, in this order: record_id,customer_id,category,region,created_date,retention_years,delete_after,reason.

The policy defines the retention period by category and region, a legal-hold exemption rule, and a consent-withdrawal override rule. Apply the rules exactly as written in the policy. Ignore any records that are under an active legal hold. If a record has a consent withdrawal date that is on or after the record creation date, do not report it. The reason field must be one of the following values: retention_period_expired.

The output must be sorted by record_id in ascending order.
