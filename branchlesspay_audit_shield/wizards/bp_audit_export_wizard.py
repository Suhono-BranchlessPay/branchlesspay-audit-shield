# -*- coding: utf-8 -*-

from odoo import fields, models


class BpAuditExportWizard(models.TransientModel):
    _name = "bp.audit.export.wizard"
    _description = "BranchlessPay Audit Trail Export"

    move_id = fields.Many2one("account.move", required=True)
    payment_id = fields.Many2one("account.payment")
    purchase_id = fields.Many2one("purchase.order")

    def action_export_pdf(self):
        self.ensure_one()
        if self.move_id:
            record = self.move_id
        elif self.payment_id:
            record = self.payment_id
        elif self.purchase_id:
            record = self.purchase_id
        else:
            record = self.move_id
        return self.env.ref(
            "branchlesspay_audit_shield.action_bp_audit_trail_report"
        ).report_action(record)
