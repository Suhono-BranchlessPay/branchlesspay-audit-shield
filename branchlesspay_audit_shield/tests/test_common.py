# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase


class BpAuditTestCommon(TransactionCase):
    """Shared helpers — no dependency on demo XML IDs."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "BP Test Partner"})
        cls.icp = cls.env["ir.config_parameter"].sudo()

    def _sale_journal(self):
        journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
        if not journal:
            journal = self.env["account.journal"].create(
                {
                    "name": "BP Test Sales",
                    "type": "sale",
                    "code": "BPTS",
                }
            )
        return journal
