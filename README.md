# BP Audit Shield (Odoo Module)

Official Odoo App Store module by **BranchlessPay, Inc.** — Phase 1 MVP.

| App Store field | Value |
|-----------------|-------|
| Name | BP Audit Shield (≤25 chars) |
| Price | $29 USD |
| Support | suhono@branchlesspay.com |
| Privacy | https://branchlesspay.com/compliance |

## Module location

```
Audit Shield/
└── branchlesspay_audit_shield/    ← install this addon in Odoo
```

> The previous prototype folder `audit_shield/` has been superseded. Use **`branchlesspay_audit_shield`** only.

## Features (Phase 1)

- Hooks: `account.move`, `account.payment`, `purchase.order`
- Optional: `approval.request` via addon `branchlesspay_audit_shield_approvals` (Odoo Enterprise `approvals`)
- `services/bp_api_service.py` — SHA-256 + `POST /api/v1/anchor`
- `bp.anchor.log` — anchor history per document
- Settings: license key, API URL, enable toggle, **Test Connection**
- Tab **BranchlessPay Audit** on invoices (statusbar: queued / anchored / failed)
- PDF audit trail export with Monad explorer URL

## Requirements

- Odoo **17** or **18** (Community or Enterprise)
- Python: `requests` (`pip install -r requirements.txt`)
- Optional: install **`branchlesspay_audit_shield_approvals`** if you use Odoo Enterprise **Approvals**

## Installation

1. Copy `branchlesspay_audit_shield` into your Odoo addons path.
2. `pip install -r requirements.txt`
3. Restart Odoo → **Apps** → Update Apps List.
4. Install **BranchlessPay Audit Shield**.
5. Open **Accounting → Configuration → Settings → BranchlessPay Audit Shield**:
   - Enable Audit Shield
   - Enter **License Key** (from [branchlesspay.com](https://branchlesspay.com))
   - Click **Test Connection**

## Configuration parameters

| Key | Purpose |
|-----|---------|
| `bp_audit.license_key` | Bearer token for API |
| `bp_audit.api_url` | Default: `https://branchlesspay.com/api/v1/anchor` |
| `bp_audit.explorer_url` | Default: `https://testnet.monadexplorer.com/tx/` |
| `bp_audit.enabled` | Master on/off switch |

Without a license key, anchoring is **skipped** (no error, TC-005).

## Test credentials (development)

1. Obtain your Bearer token from BranchlessPay (do **not** commit it to Git).
2. In Odoo Settings, paste the token into **License Key**.
3. Click **Test Connection** (POST `/api/v1/anchor`).
4. Create an invoice — fields `bp_content_hash`, `bp_anchor_id`, `bp_tx_hash` should populate.
5. If status is `queued`, click **Refresh Anchor Status** (GET `/api/v1/anchor/{anchor_id}`).

See `TESTING.local.example.md` for a local checklist template.

API docs: [branchlesspay.com/technology](https://branchlesspay.com/technology)

## Testing

```bash
odoo-bin -d your_db -i branchlesspay_audit_shield --test-enable --stop-after-init
```

## Milestones (Work Order)

| Milestone | Status |
|-----------|--------|
| M1 — Skeleton + account.move + API | Ready for review |
| M2 — All models + views + PDF + settings | See `MILESTONE2.md` + `VIDEO_DEMO_SCRIPT.md` |
| M3 — App Store assets (replace screenshots) | Placeholder screenshots included |
| M4 — Live on apps.odoo.com | Pending BranchlessPay |

Replace `static/description/screenshot_*.png` with real 1280×720 Odoo screenshots before App Store submission. Banner (`banner.png`) is the store cover/thumbnail.

## Odoo 18

Change `version` in `__manifest__.py` to `18.0.1.0.0`.

## License

OPL-1 — BranchlessPay, Inc.
