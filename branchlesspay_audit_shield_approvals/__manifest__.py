# -*- coding: utf-8 -*-
{
    "name": "BP Audit Shield — Approvals",
    "version": "17.0.1.0.0",
    "category": "Human Resources/Approvals",
    "summary": "Anchor Odoo approval requests to BranchlessPay",
    "description": """
Optional bridge for Odoo Enterprise **approvals** module.
Maps Work Order model ``approval.workflow`` to ``approval.request``.
    """,
    "author": "Branchlesspay, Inc.",
    "website": "https://branchlesspay.com",
    "license": "OPL-1",
    "depends": [
        "branchlesspay_audit_shield",
        "approvals",
    ],
    "data": [
        "views/approval_request_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
