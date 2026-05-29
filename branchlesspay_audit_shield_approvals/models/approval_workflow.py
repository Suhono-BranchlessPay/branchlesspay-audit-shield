# -*- coding: utf-8 -*-

from odoo import models

# Work Order: approval.workflow → Odoo Enterprise approval.request


class ApprovalRequest(models.Model):
    _name = "approval.request"
    _inherit = ["approval.request", "bp.audit.mixin"]

    def _bp_financial_fields(self):
        return {
            "amount",
            "request_owner_id",
            "request_status",
            "category_id",
            "date",
        }

    def _bp_anchor_event_type(self):
        self.ensure_one()
        status = getattr(self, "request_status", False) or getattr(
            self, "state", "draft"
        )
        return "approval_workflow_%s" % status

    def _bp_anchor_reference_id(self):
        self.ensure_one()
        return self.name or "approval_%s" % self.id
