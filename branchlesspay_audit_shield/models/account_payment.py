# -*- coding: utf-8 -*-

from odoo import models


class AccountPayment(models.Model):
    _name = "account.payment"
    _inherit = ["account.payment", "bp.audit.mixin"]

    def _bp_financial_fields(self):
        return {
            "amount",
            "partner_id",
            "date",
            "state",
            "payment_type",
            "currency_id",
        }

    def _bp_anchor_event_type(self):
        self.ensure_one()
        return "payment_%s" % (self.state or "draft")
