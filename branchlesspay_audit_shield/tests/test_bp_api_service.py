# -*- coding: utf-8 -*-

from odoo.tests import tagged, TransactionCase

from odoo.addons.branchlesspay_audit_shield.services.bp_api_service import BPApiService


@tagged("post_install", "-at_install")
class TestBPApiService(TransactionCase):
    def test_generate_hash_deterministic(self):
        service = BPApiService("test-key")
        payload = {
            "event_type": "invoice_created",
            "reference_id": "INV-001",
            "amount": 100.0,
            "currency": "IDR",
            "timestamp": "2026-05-28T10:00:00Z",
            "metadata": {},
        }
        self.assertEqual(service.generate_hash(payload), service.generate_hash(payload))

    def test_map_status_to_selection(self):
        self.assertEqual(BPApiService.map_status_to_selection("queued", True), "queued")
        self.assertEqual(BPApiService.map_status_to_selection("anchored", True), "anchored")
        self.assertEqual(BPApiService.map_status_to_selection("failed", True), "failed")
        self.assertEqual(BPApiService.map_status_to_selection("queued", False), "failed")

    def test_timeout_returns_failed(self):
        service = BPApiService("invalid-key", api_url="http://127.0.0.1:1")
        result = service.anchor(
            event_type="test",
            reference_id="T-1",
            amount=0,
            currency="USD",
        )
        self.assertFalse(result.get("ok"))
        self.assertTrue(result.get("content_hash"))
