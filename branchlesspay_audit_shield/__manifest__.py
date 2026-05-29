# -*- coding: utf-8 -*-
{
    "name": "BP Audit Shield",
    "version": "17.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Immutable blockchain audit trail",
    "description": """
BP Audit Shield — BranchlessPay
================================

Add tamper-proof audit trail to every Odoo transaction.
Invoices, payments, purchase orders, and approvals are anchored
to the BranchlessPay network with SHA-256 hashing.

This module requires an external BranchlessPay API service.
See https://branchlesspay.com for details.

Privacy Policy: https://branchlesspay.com/compliance
    """,
    "author": "Branchlesspay, Inc.",
    "website": "https://branchlesspay.com",
    "support": "suhono@branchlesspay.com",
    "license": "OPL-1",
    "depends": [
        "base",
        "account",
        "purchase",
    ],
    "data": [
        "security/bp_security.xml",
        "security/ir.model.access.csv",
        "data/bp_config_data.xml",
        "views/bp_anchor_log_views.xml",
        "views/account_move_views.xml",
        "views/account_payment_views.xml",
        "views/purchase_order_views.xml",
        "views/res_config_settings_views.xml",
        "reports/bp_audit_trail_report.xml",
        "reports/bp_audit_trail_templates.xml",
        "wizards/bp_audit_export_wizard_views.xml",
    ],
    "assets": {},
    "installable": True,
    "application": False,
    "auto_install": False,
    "price": 29.0,
    "currency": "USD",
    "live_test_url": "",
    "images": [
        "static/description/icon.png",
        "static/description/banner.png",
        "static/description/screenshot_settings.png",
        "static/description/screenshot_invoice.png",
        "static/description/screenshot_anchor_log.png",
    ],
    "external_dependencies": {
        "python": ["requests"],
    },
}
