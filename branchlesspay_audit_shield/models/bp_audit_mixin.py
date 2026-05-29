# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..services.bp_api_service import BPApiService, BP_API_URL

_logger = logging.getLogger(__name__)


class BpAuditMixin(models.AbstractModel):
    _name = "bp.audit.mixin"
    _description = "BranchlessPay Audit Mixin"

    bp_content_hash = fields.Char(
        string="BP Content Hash",
        readonly=True,
        copy=False,
        help="SHA-256 hash of document content",
    )
    bp_anchor_id = fields.Char(
        string="BP Anchor ID",
        readonly=True,
        copy=False,
    )
    bp_tx_hash = fields.Char(
        string="BP TX Hash",
        readonly=True,
        copy=False,
    )
    bp_anchor_status = fields.Selection(
        [
            ("queued", "Queued"),
            ("anchored", "Anchored"),
            ("failed", "Failed"),
        ],
        string="BP Status",
        default="queued",
        readonly=True,
        copy=False,
    )
    bp_anchored_at = fields.Datetime(
        string="BP Anchored At",
        readonly=True,
        copy=False,
    )
    bp_tsa_token = fields.Char(
        string="BP TSA Token",
        readonly=True,
        copy=False,
        help="RFC 3161 timestamp token (Phase 2)",
    )
    bp_explorer_url = fields.Char(
        string="Verification URL",
        compute="_compute_bp_explorer_url",
    )

    @api.depends("bp_tx_hash")
    def _compute_bp_explorer_url(self):
        icp = self.env["ir.config_parameter"].sudo()
        base_url = icp.get_param(
            "bp_audit.explorer_url",
            "https://testnet.monadexplorer.com/tx/",
        )
        for record in self:
            record.bp_explorer_url = BPApiService.explorer_url(
                record.bp_tx_hash, base_url
            )

    def _get_bp_company(self):
        self.ensure_one()
        if "company_id" in self._fields and self.company_id:
            return self.company_id
        return self.env.company

    def _bp_is_enabled(self):
        icp = self.env["ir.config_parameter"].sudo()
        enabled = icp.get_param("bp_audit.enabled", "True")
        return enabled not in ("0", "False", "false")

    def _bp_get_config(self):
        icp = self.env["ir.config_parameter"].sudo()
        return {
            "license_key": icp.get_param("bp_audit.license_key", ""),
            "api_url": icp.get_param("bp_audit.api_url", BP_API_URL),
        }

    def _bp_financial_fields(self):
        """Override in concrete models to limit re-anchoring on write."""
        return set()

    def _bp_anchor_event_type(self):
        self.ensure_one()
        return "%s_updated" % self._name.replace(".", "_")

    def _bp_anchor_reference_id(self):
        self.ensure_one()
        if hasattr(self, "name") and self.name:
            return self.name
        return "%s_%s" % (self._name.replace(".", "_"), self.id)

    def _bp_anchor_amount(self):
        self.ensure_one()
        for fname in ("amount_total", "amount", "amount_untaxed"):
            if fname in self._fields:
                return float(getattr(self, fname) or 0.0)
        return 0.0

    def _bp_anchor_currency(self):
        self.ensure_one()
        if "currency_id" in self._fields and self.currency_id:
            return self.currency_id.name
        company = self._get_bp_company()
        return company.currency_id.name if company.currency_id else "USD"

    def _bp_anchor_metadata(self):
        self.ensure_one()
        meta = {
            "odoo_model": self._name,
            "odoo_id": self.id,
            "state": getattr(self, "state", False),
        }
        if "partner_id" in self._fields and self.partner_id:
            meta["partner_name"] = self.partner_id.name
        return meta

    def _bp_apply_anchor_result(self, result):
        """Write anchor fields from POST or GET API response."""
        self.ensure_one()
        vals = {
            "bp_content_hash": result.get("content_hash") or self.bp_content_hash,
            "bp_anchor_id": result.get("anchor_id") or self.bp_anchor_id,
            "bp_tx_hash": result.get("tx_hash") or self.bp_tx_hash,
            "bp_anchor_status": BPApiService.map_status_to_selection(
                result.get("status"),
                ok=result.get("ok", False),
            ),
        }
        if result.get("tsa_token") and result.get("tsa_token") != "pending":
            vals["bp_tsa_token"] = result.get("tsa_token")
        anchored_at = result.get("anchored_at")
        if anchored_at and vals["bp_anchor_status"] == "anchored":
            vals["bp_anchored_at"] = anchored_at
        elif vals["bp_anchor_status"] == "anchored" and result.get("ok"):
            vals["bp_anchored_at"] = fields.Datetime.now()
        self.with_context(bp_skip_anchor=True).write(vals)
        return vals

    def _bp_anchor(self):
        """Send document data to BranchlessPay for anchoring."""
        if not self._bp_is_enabled():
            return

        config = self._bp_get_config()
        license_key = config["license_key"]
        if not license_key:
            _logger.warning("BranchlessPay: license_key not configured")
            return

        service = BPApiService(license_key, config["api_url"])

        for record in self:
            if not record.id:
                continue

            event_type = record._bp_anchor_event_type()
            reference_id = record._bp_anchor_reference_id()
            amount = record._bp_anchor_amount()
            currency = record._bp_anchor_currency()
            metadata = record._bp_anchor_metadata()

            result = service.anchor(
                event_type=event_type,
                reference_id=reference_id,
                amount=amount,
                currency=currency,
                metadata=metadata,
            )

            record._bp_apply_anchor_result(result)

            self.env["bp.anchor.log"].log_anchor(
                record,
                event_type,
                reference_id,
                result,
                amount=amount,
                currency=currency,
            )

    def action_bp_refresh_anchor_status(self):
        """Poll GET /api/v1/anchor/{anchor_id} for latest status."""
        self.ensure_one()
        if not self.bp_anchor_id:
            raise UserError(_("No BranchlessPay anchor ID on this document yet."))
        config = self._bp_get_config()
        if not config["license_key"]:
            raise UserError(_("BranchlessPay license key is not configured."))
        service = BPApiService(config["license_key"], config["api_url"])
        result = service.get_anchor_status(self.bp_anchor_id)
        if not result.get("ok"):
            raise UserError(
                _("Status check failed: %s") % result.get("error", "unknown")
            )
        self._bp_apply_anchor_result(result)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Anchor status updated"),
                "message": _("Status: %s") % self.bp_anchor_status,
                "type": "success",
                "sticky": False,
            },
        }

    def action_bp_export_audit(self):
        self.ensure_one()
        report_map = {
            "account.move": "branchlesspay_audit_shield.action_bp_audit_trail_report",
            "account.payment": "branchlesspay_audit_shield.action_bp_audit_trail_report_payment",
            "purchase.order": "branchlesspay_audit_shield.action_bp_audit_trail_report_po",
        }
        xml_id = report_map.get(
            self._name, "branchlesspay_audit_shield.action_bp_audit_trail_report"
        )
        return self.env.ref(xml_id).report_action(self)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._bp_anchor()
        return records

    def write(self, vals):
        result = super().write(vals)
        if self.env.context.get("bp_skip_anchor"):
            return result
        financial = self._bp_financial_fields()
        if financial and financial.intersection(vals.keys()):
            self._bp_anchor()
        return result
