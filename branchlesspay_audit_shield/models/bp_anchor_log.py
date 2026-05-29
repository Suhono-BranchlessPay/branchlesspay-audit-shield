# -*- coding: utf-8 -*-

from odoo import api, fields, models


class BpAnchorLog(models.Model):
    _name = "bp.anchor.log"
    _description = "BranchlessPay Anchor Log"
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    res_model = fields.Char(required=True, index=True)
    res_id = fields.Integer(required=True, index=True)
    event_type = fields.Char(required=True)
    reference_id = fields.Char()
    content_hash = fields.Char()
    anchor_id = fields.Char()
    tx_hash = fields.Char()
    anchor_status = fields.Selection(
        [
            ("queued", "Queued"),
            ("anchored", "Anchored"),
            ("failed", "Failed"),
        ],
        default="queued",
    )
    error_message = fields.Text()
    amount = fields.Float()
    currency = fields.Char()
    payload_snapshot = fields.Text()

    def name_get(self):
        result = []
        for record in self:
            label = "%s [%s:%s] %s" % (
                record.event_type or "",
                record.res_model or "",
                record.res_id or 0,
                record.anchor_status or "",
            )
            result.append((record.id, label))
        return result

    @api.model
    def log_anchor(self, record, event_type, reference_id, result, amount=0.0, currency="USD"):
        """Persist anchor attempt for audit trail."""
        status = "anchored" if result.get("ok") else "failed"
        if result.get("ok") and result.get("status") == "queued":
            status = "queued"
        return self.create(
            {
                "company_id": record._get_bp_company().id,
                "res_model": record._name,
                "res_id": record.id,
                "event_type": event_type,
                "reference_id": reference_id,
                "content_hash": result.get("content_hash"),
                "anchor_id": result.get("anchor_id"),
                "tx_hash": result.get("tx_hash"),
                "anchor_status": status,
                "error_message": result.get("error"),
                "amount": amount,
                "currency": currency,
            }
        )
