# -*- coding: utf-8 -*-

from odoo import models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "bp.audit.mixin"]

    def _bp_financial_fields(self):
        return {
            "amount_total",
            "invoice_line_ids",
            "partner_id",
            "invoice_date",
            "state",
        }

    def _bp_anchor_event_type(self):
        self.ensure_one()
        return "invoice_%s" % (self.move_type or "entry")

    def _bp_anchor_metadata(self):
        self.ensure_one()
        meta = super()._bp_anchor_metadata()
        meta.update(
            {
                "move_type": self.move_type,
                "journal_name": self.journal_id.name or "",
                "invoice_date": str(self.invoice_date) if self.invoice_date else "",
                "line_count": len(self.invoice_line_ids),
            }
        )
        return meta
