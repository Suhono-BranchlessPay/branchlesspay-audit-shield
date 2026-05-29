# Development Guide — BranchlessPay Audit Shield

## Prerequisites
- Python 3.10+
- Odoo 17 or 18 (Community or Enterprise)
- Git
- requests>=2.28.0 (see requirements.txt)

## Setup Local Development

1. Clone this repo:
   git clone [repo-url]

2. Install Odoo 17 or 18 locally
   https://www.odoo.com/documentation/17.0/administration/install

3. Copy module to Odoo addons:
   cp -r branchlesspay_audit_shield /path/to/odoo/addons/

4. Install via Odoo:
   Settings → Apps → Search "BranchlessPay"
   → Install

## API Credentials
Request test credentials from:
hello@branchlesspay.com

Test API via curl:
curl -X POST \
  https://branchlesspay.com/api/v1/anchor \
  -H "Authorization: Bearer {TEST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "invoice_created",
    "reference_id": "INV-TEST-001",
    "amount": 150000,
    "currency": "IDR",
    "timestamp": "2026-05-28T10:00:00Z",
    "metadata": {"test": true}
  }'

Expected response (HTTP 202):
{
  "ok": true,
  "anchor_id": "uuid-xxx",
  "content_hash": "sha256-hash",
  "tx_hash": "pending",
  "status": "queued",
  "anchored_at": "2026-05-28T10:00:01Z"
}

## API Documentation
Full docs: https://branchlesspay.com/technology
API spec: https://branchlesspay.com/docs

## Configuration in Odoo
Settings → Technical → BranchlessPay
→ Enter License Key
→ Click Test Connection
→ Status: Connected ✓

## Branch Strategy
- main: production-ready code
- develop: active development
- feature/xxx: feature branches
- fix/xxx: bug fix branches

## Commit Convention
feat: New feature
fix: Bug fix
docs: Documentation
test: Tests
chore: Maintenance

## Running Tests
cd /path/to/odoo
python odoo-bin -c odoo.conf \
  --test-enable \
  --stop-after-init \
  -d testdb \
  -i branchlesspay_audit_shield

## Work Order Reference
Full technical specifications:
BranchlessPay_WorkOrder_Verry_AuditShield.docx
(provided separately)

## Contact
Technical: engineering@branchlesspay.com
General: hello@branchlesspay.com
Website: branchlesspay.com
