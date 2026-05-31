# BranchlessPay Audit Shield
# ERP Compatibility Matrix
# Last updated: May 31, 2026

## Live & In Development

| ERP | Version | Method | Status | Date |
|-----|---------|--------|--------|------|
| Odoo | 17 + 18 | Native module | ✅ Live | May 30, 2026 |
| Odoo | 19 | Native module | 🔄 Dev (local bench) | Q3 2026 |
| ERPNext | 14 + 15 | Frappe hooks | 🔄 In Development | Q3 2026 |
| Tally Prime | 2.0+ | TDL + HTTP | 📋 Planned | Q4 2026 |
| Zoho Books | Any | Webhooks | 📋 Planned | Q1 2027 |
| QuickBooks | Online | Webhooks | 📋 Planned | Q1 2027 |
| NetSuite | Any | SuiteScript | 📋 Planned | Q3 2027 |
| Dynamics 365 | Any | Dataverse API | 📋 Planned | Q3 2027 |
| SAP B1 | 9.3+ | Service Layer | 📋 Planned | Q1 2028 |
| SAP S/4HANA | Any | SAP BTP | 📋 Planned | 2028+ |
| Oracle Fusion | Any | REST API | 📋 Planned | 2028+ |

## Repository Map

| ERP | Repository | Branch | Status |
|-----|-----------|--------|--------|
| Odoo 17/18 | branchlesspay-audit-shield | 17.0 | ✅ Live |
| Odoo 19 | branchlesspay-audit-shield | 19.0 (local) | 🔄 Dev |
| ERPNext | branchlesspay-audit-shield-erpnext | 14.0 | 🔄 Dev |

## Notes

- **Odoo 17/18** — Live on apps.odoo.com: https://apps.odoo.com/apps/modules/17.0/branchlesspay_audit_shield
- **Odoo 19** — In development on local bench. Will be added to the monorepo when ready for public release.
- **ERPNext** — v2.0.0 (commit `5b457a4`). `BP Anchor Log` DocType installed. Journal Entry custom field installed. `branchlesspay_core` shared adapter.
- All ERPs use the same API endpoint: `POST https://branchlesspay.com/api/v1/anchor` with `Bearer bp_live_xxx` or `Bearer bp_test_xxx`.

## API (Universal)

All integrations use an identical endpoint.

```http
POST /api/v1/anchor
Authorization: Bearer {license_key}
Content-Type: application/json

{
  "event_type": "invoice_created",
  "reference_id": "INV-001",
  "amount": 150000,
  "currency": "IDR",
  "timestamp": "2026-05-31T00:00:00Z"
}
```
