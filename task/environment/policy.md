Retention policy
================

As of 2026-01-01, determine whether each record is overdue for deletion.

1. Determine the retention period from the category/region table below.
2. A record is overdue when the audit date is later than the record's created date plus the retention period in years.
3. Ignore records that are under an active legal hold.
4. If a record has a consent withdrawal date that is on or after the record creation date, do not report it.

Category/region retention table
-------------------------------
- customer_records / North America: 3 years
- customer_records / EU: 5 years
- customer_records / APAC: 2 years
- customer_records / LATAM: 4 years
- customer_records / MEA: 6 years
- financial / North America: 7 years
- financial / EU: 4 years
- financial / APAC: 5 years
- financial / LATAM: 6 years
- financial / MEA: 8 years
- healthcare / North America: 10 years
- healthcare / EU: 7 years
- healthcare / APAC: 9 years
- healthcare / LATAM: 8 years
- healthcare / MEA: 10 years
- other / North America: 5 years
- other / EU: 6 years
- other / APAC: 4 years
- other / LATAM: 5 years
- other / MEA: 7 years

Legal hold rule
---------------
- If a record has an active legal hold, it is exempt from deletion even if overdue.
- A hold is active if the hold start date is on or before the audit date and the hold end date is on or after the audit date.

Consent withdrawal rule
-----------------------
- If a consent withdrawal date exists and is on or after the record creation date, the record is excluded from the report.
