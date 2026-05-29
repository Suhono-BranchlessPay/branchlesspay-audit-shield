# -*- coding: utf-8 -*-

from odoo import models


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "bp.audit.mixin"]

    def _bp_financial_fields(self):
        return {
            "amount_total",
            "order_line",
            "partner_id",
            "date_order",
            "state",
        }

    def _bp_anchor_event_type(self):
        self.ensure_one()
        return "purchase_order_%s" % (self.state or "draft")
