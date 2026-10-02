# 300-disability-benefits-auto-apply

Deterministic disability benefits orchestration engine. Automates member eligibility checks, pre-fills application fields from a member profile, and submits applications for qualified members.

`300.py` requires an explicit `EligibilityPolicy` with the applicable annual-income limit, a benefits API endpoint, and an `AuditSink`. KYC, address, and identity checks are required by default; additional compliance flags can be configured. Submission is halted unless all required compliance checks pass and the member meets the configured disability and income rules.

The HTTP transport submits a JSON payload using POST and treats 2xx responses as successful. A custom transport and timezone-aware clock can be supplied for integration and reproducible testing. Each audit event includes a timestamp and a deterministic state hash; configure the audit sink to persist events according to your retention and privacy requirements.
