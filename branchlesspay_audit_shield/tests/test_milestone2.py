# -*- coding: utf-8 -*-
"""Work Order test cases TC-001 through TC-012."""

from unittest.mock import patch

from odoo.tests import tagged
from odoo.tools import file_open

from odoo.addons.branchlesspay_audit_shield.services.bp_api_service import (
    BPApiService,
    BP_API_URL,
)

from .test_common import BpAuditTestCommon


def _api_ok(content_hash="abc123hash"):
    return {
        "ok": True,
        "anchor_id": "11111111-2222-3333-4444-555555555555",
        "content_hash": content_hash,
        "tx_hash": "pending",
        "status": "queued",
    }


def _api_auth_fail(content_hash="failhash"):
    return {
        "ok": False,
        "error": "Unauthorized",
        "content_hash": content_hash,
    }


@tagged("post_install", "-at_install")
class TestMilestone2TC(BpAuditTestCommon):
    """Automated coverage for Work Order acceptance tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.icp.set_param("bp_audit.enabled", "True")
        cls.icp.set_param("bp_audit.license_key", "test-license-m2")
        cls.icp.set_param("bp_audit.api_url", BP_API_URL)

    def _invoice_vals(self, price=100.0):
        return {
            "move_type": "out_invoice",
            "partner_id": self.partner.id,
            "journal_id": self._sale_journal().id,
            "invoice_line_ids": [
                (0, 0, {"name": "Test Line", "quantity": 1, "price_unit": price})
            ],
        }

    # TC-001: module installed without breaking core models
    def test_tc001_module_installed(self):
        module = self.env["ir.module.module"].search(
            [("name", "=", "branchlesspay_audit_shield")], limit=1
        )
        self.assertTrue(module)
        self.assertEqual(module.state, "installed")
        self.env["account.move"].search([], limit=1)

    # TC-002: new invoice gets bp_content_hash
    @patch.object(BPApiService, "anchor", return_value=_api_ok())
    def test_tc002_invoice_hash_on_create(self, _mock):
        move = self.env["account.move"].create(self._invoice_vals())
        self.assertTrue(move.bp_content_hash)
        self.assertEqual(move.bp_anchor_status, "queued")

    # TC-003: financial write re-anchors (new log entry)
    @patch.object(BPApiService, "anchor", return_value=_api_ok())
    def test_tc003_invoice_reanchor_on_write(self, mock_anchor):
        move = self.env["account.move"].create(self._invoice_vals(100))
        first_hash = move.bp_content_hash
        move.write({"invoice_line_ids": [(1, move.invoice_line_ids[0].id, {"price_unit": 200})]})
        self.assertGreaterEqual(mock_anchor.call_count, 2)
        logs = self.env["bp.anchor.log"].search(
            [("res_model", "=", "account.move"), ("res_id", "=", move.id)]
        )
        self.assertGreaterEqual(len(logs), 2)
        self.assertTrue(first_hash)

    # TC-004: BranchlessPay Audit tab view exists on invoice form
    def test_tc004_invoice_audit_tab_view(self):
        view = self.env.ref("branchlesspay_audit_shield.view_move_form_bp")
        self.assertEqual(view.model, "account.move")
        arch = view.arch
        self.assertIn("BranchlessPay Audit", arch)
        self.assertIn("bp_content_hash", arch)

    # TC-005: no license key — skip anchoring, no error
    def test_tc005_no_license_skips_silently(self):
        self.icp.set_param("bp_audit.license_key", "")
        move = self.env["account.move"].create(self._invoice_vals())
        self.assertFalse(move.bp_content_hash)
        self.assertFalse(move.bp_anchor_id)

    # TC-006: invalid license — status failed, warning logged
    @patch.object(BPApiService, "anchor", return_value=_api_auth_fail())
    def test_tc006_invalid_license_sets_failed(self, _mock):
        self.icp.set_param("bp_audit.license_key", "bad-key")
        move = self.env["account.move"].create(self._invoice_vals())
        self.assertEqual(move.bp_anchor_status, "failed")
        self.assertTrue(move.bp_content_hash)

    # TC-007: API timeout / unreachable — failed status, Odoo continues
    @patch("odoo.addons.branchlesspay_audit_shield.services.bp_api_service.requests.post")
    def test_tc007_timeout_sets_failed(self, mock_post):
        import requests

        mock_post.side_effect = requests.exceptions.Timeout("timed out")
        service = BPApiService("key", api_url=BP_API_URL)
        result = service.anchor(
            event_type="test",
            reference_id="T-1",
            amount=0,
            currency="USD",
        )
        self.assertFalse(result.get("ok"))
        self.assertEqual(result.get("error"), "timeout")
        self.assertTrue(result.get("content_hash"))

    # TC-008: PDF export renders with anchor fields
    @patch.object(BPApiService, "anchor", return_value=_api_ok())
    def test_tc008_pdf_export(self, _mock):
        move = self.env["account.move"].create(self._invoice_vals())
        report_xmlid = "branchlesspay_audit_shield.action_bp_audit_trail_report"
        pdf_content, _report_type = self.env["ir.actions.report"]._render_qweb_pdf(
            report_xmlid,
            res_ids=move.ids,
        )
        self.assertTrue(pdf_content)
        self.assertGreater(len(pdf_content), 100)

    # TC-009: Test Connection returns success notification
    @patch.object(BPApiService, "anchor", return_value=_api_ok())
    @patch.object(BPApiService, "get_anchor_status", return_value=_api_ok())
    def test_tc009_test_connection_action(self, _get_mock, _post_mock):
        settings = self.env["res.config.settings"].create(
            {
                "bp_license_key": "test-license-m2",
                "bp_api_url": BP_API_URL,
            }
        )
        action = settings.action_test_bp_connection()
        self.assertEqual(action["tag"], "display_notification")
        self.assertEqual(action["params"]["type"], "success")

    # TC-010: account.payment hash on create
    @patch.object(BPApiService, "anchor", return_value=_api_ok())
    def test_tc010_payment_hash_on_create(self, _mock):
        journal = self.env["account.journal"].search(
            [("type", "in", ("bank", "cash"))], limit=1
        )
        payment = self.env["account.payment"].create(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": self.partner.id,
                "amount": 50.0,
                "journal_id": journal.id,
            }
        )
        self.assertTrue(payment.bp_content_hash)
        log = self.env["bp.anchor.log"].search(
            [("res_model", "=", "account.payment"), ("res_id", "=", payment.id)],
            limit=1,
        )
        self.assertTrue(log)

    # TC-011: purchase.order hash on create
    @patch.object(BPApiService, "anchor", return_value=_api_ok())
    def test_tc011_purchase_order_hash_on_create(self, _mock):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"name": "PO Line", "product_qty": 1, "price_unit": 25})
                ],
            }
        )
        self.assertTrue(po.bp_content_hash)
        log = self.env["bp.anchor.log"].search(
            [("res_model", "=", "purchase.order"), ("res_id", "=", po.id)],
            limit=1,
        )
        self.assertTrue(log)

    # TC-012: App Store manifest required fields
    def test_tc012_manifest_required_fields(self):
        with file_open(
            "branchlesspay_audit_shield/__manifest__.py", "r"
        ) as manifest_file:
            manifest = manifest_file.read()
        for key in (
            '"name"',
            '"version"',
            '"author"',
            '"website"',
            '"license"',
            '"depends"',
            '"data"',
            '"installable"',
            '"images"',
        ):
            self.assertIn(key, manifest)
        self.assertIn("static/description/icon.png", manifest)
        self.assertIn("static/description/screenshot_invoice.png", manifest)
