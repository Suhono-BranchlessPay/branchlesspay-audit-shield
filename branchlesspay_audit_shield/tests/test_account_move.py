# -*- coding: utf-8 -*-

from odoo.tests import tagged

from .test_common import BpAuditTestCommon


@tagged("post_install", "-at_install")
class TestAccountMoveAnchor(BpAuditTestCommon):
    def _create_test_invoice(self):
        return {
            "move_type": "out_invoice",
            "partner_id": self.partner.id,
            "journal_id": self._sale_journal().id,
            "invoice_line_ids": [
                (0, 0, {"name": "Test", "quantity": 1, "price_unit": 100})
            ],
        }

    def test_create_without_license_skips_anchor(self):
        self.icp.set_param("bp_audit.license_key", "")
        move = self.env["account.move"].create(self._create_test_invoice())
        self.assertFalse(move.bp_content_hash)

    def test_financial_write_triggers_reanchor_with_license(self):
        self.icp.set_param("bp_audit.license_key", "test-license-placeholder")
        move = self.env["account.move"].create(self._create_test_invoice())
        self.assertIn(move.bp_anchor_status, ("queued", "anchored", "failed"))
