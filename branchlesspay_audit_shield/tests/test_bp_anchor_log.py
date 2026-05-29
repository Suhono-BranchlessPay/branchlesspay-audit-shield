# -*- coding: utf-8 -*-

from odoo.tests import tagged

from .test_common import BpAuditTestCommon


@tagged("post_install", "-at_install")
class TestBpAnchorLog(BpAuditTestCommon):
    def test_log_anchor_creates_entry(self):
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "journal_id": self._sale_journal().id,
                "invoice_line_ids": [
                    (0, 0, {"name": "Line", "quantity": 1, "price_unit": 10})
                ],
            }
        )
        log = self.env["bp.anchor.log"].log_anchor(
            move,
            "test_event",
            "INV-TEST",
            {"ok": False, "error": "test", "content_hash": "abc123"},
            amount=10.0,
            currency="USD",
        )
        self.assertEqual(log.res_model, "account.move")
        self.assertEqual(log.anchor_status, "failed")
