# -*- coding: utf-8 -*-

import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

from ..services.bp_api_service import BPApiService, BP_API_URL

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    bp_license_key = fields.Char(
        string="BranchlessPay License Key",
        config_parameter="bp_audit.license_key",
    )
    bp_api_url = fields.Char(
        string="BranchlessPay API URL",
        config_parameter="bp_audit.api_url",
        default=BP_API_URL,
    )
    bp_explorer_url = fields.Char(
        string="Monad Explorer URL",
        config_parameter="bp_audit.explorer_url",
        default="https://testnet.monadexplorer.com/tx/",
    )
    bp_enabled = fields.Boolean(
        string="Enable BranchlessPay Audit Shield",
        config_parameter="bp_audit.enabled",
        default=True,
    )

    def _bp_normalize_api_url(self, url):
        url = (url or "").strip() or BP_API_URL
        if not url.endswith("/anchor"):
            if url.endswith("/api") or url.endswith("/api/"):
                url = url.rstrip("/") + "/v1/anchor"
            elif "/v1/" not in url:
                url = url.rstrip("/") + "/v1/anchor"
        return url

    def action_test_bp_connection(self):
        """Test BranchlessPay API and show visible feedback in Odoo 19."""
        self.ensure_one()
        # Persist unsaved settings values before testing.
        self.set_values()

        icp = self.env["ir.config_parameter"].sudo()
        license_key = (self.bp_license_key or icp.get_param("bp_audit.license_key", "")).strip()
        api_url = self._bp_normalize_api_url(
            self.bp_api_url or icp.get_param("bp_audit.api_url", BP_API_URL)
        )

        if not license_key:
            raise UserError(_("License key is not configured. Paste your Bearer token and try again."))

        _logger.info("BP Audit Shield: testing connection to %s", api_url)
        service = BPApiService(license_key, api_url)
        result = service.anchor(
            event_type="connection_test",
            reference_id="TEST-001",
            amount=0,
            currency="USD",
            metadata={"test": True, "source": "odoo_settings"},
        )

        if result.get("ok"):
            anchor_id = result.get("anchor_id", "N/A")
            status = result.get("status", "unknown")
            msg = _("Connection successful!\n\nAnchor ID: %s\nStatus: %s\nAPI: %s") % (
                anchor_id,
                status,
                api_url,
            )
            if anchor_id and anchor_id != "N/A":
                check = service.get_anchor_status(anchor_id)
                if check.get("ok"):
                    msg = _(
                        "Connection successful!\n\nAnchor ID: %s\nGET status: %s\nAPI: %s"
                    ) % (anchor_id, check.get("status", status), api_url)
            # Save corrected API URL if user had truncated value.
            icp.set_param("bp_audit.api_url", api_url)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("BranchlessPay Connected"),
                    "message": msg,
                    "type": "success",
                    "sticky": True,
                },
            }

        raise UserError(
            _("Connection failed.\n\nAPI: %s\nError: %s")
            % (api_url, result.get("error", "unknown error"))
        )