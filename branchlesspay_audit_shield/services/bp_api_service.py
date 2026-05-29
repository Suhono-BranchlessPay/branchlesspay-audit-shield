# -*- coding: utf-8 -*-

import hashlib
import json
import logging
from datetime import datetime, timezone

import requests

_logger = logging.getLogger(__name__)

BP_API_URL = "https://branchlesspay.com/api/v1/anchor"
BP_API_TIMEOUT = 10
BP_EXPLORER_URL = "https://testnet.monadexplorer.com/tx/"


class BPApiService:
    """Client for BranchlessPay /api/v1/anchor."""

    def __init__(self, license_key, api_url=None):
        self.license_key = license_key
        self.api_url = (api_url or BP_API_URL).rstrip("/")
        self.headers = {
            "Authorization": "Bearer %s" % license_key,
            "Content-Type": "application/json",
        }

    def generate_hash(self, data):
        """Generate SHA-256 hash from canonical JSON document data."""
        canonical = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def anchor(
        self,
        event_type,
        reference_id,
        amount,
        currency,
        metadata=None,
    ):
        """Send anchor request to BranchlessPay API."""
        payload = {
            "event_type": event_type,
            "reference_id": reference_id,
            "amount": amount,
            "currency": currency,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        content_hash = self.generate_hash(payload)
        payload["content_hash"] = content_hash

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=BP_API_TIMEOUT,
            )
            if response.status_code in (200, 202):
                result = response.json()
                result["content_hash"] = content_hash
                result["ok"] = result.get("ok", True)
                return result
            _logger.error(
                "BP API error %s: %s", response.status_code, response.text
            )
            return {
                "ok": False,
                "error": response.text,
                "content_hash": content_hash,
            }
        except requests.exceptions.Timeout:
            _logger.warning("BP API timeout — record will be re-queued")
            return {
                "ok": False,
                "error": "timeout",
                "content_hash": content_hash,
            }
        except Exception as exc:
            _logger.error("BP API exception: %s", exc)
            return {
                "ok": False,
                "error": str(exc),
                "content_hash": content_hash,
            }

    def get_anchor_status(self, anchor_id):
        """GET /api/v1/anchor/{anchor_id} — poll anchoring status."""
        if not anchor_id:
            return {"ok": False, "error": "missing anchor_id"}
        url = "%s/%s" % (self.api_url, anchor_id)
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=BP_API_TIMEOUT,
            )
            if response.status_code == 200:
                result = response.json()
                result["ok"] = result.get("ok", True)
                return result
            _logger.error(
                "BP API GET error %s: %s", response.status_code, response.text
            )
            return {"ok": False, "error": response.text}
        except requests.exceptions.Timeout:
            _logger.warning("BP API GET timeout for anchor %s", anchor_id)
            return {"ok": False, "error": "timeout"}
        except Exception as exc:
            _logger.error("BP API GET exception: %s", exc)
            return {"ok": False, "error": str(exc)}

    @staticmethod
    def map_status_to_selection(api_status, ok=True):
        """Map API status string to Odoo bp_anchor_status selection."""
        if not ok:
            return "failed"
        status = (api_status or "").lower()
        if status in ("anchored", "confirmed", "completed"):
            return "anchored"
        if status in ("failed", "error"):
            return "failed"
        return "queued"

    @staticmethod
    def explorer_url(tx_hash, base_url=None):
        if not tx_hash or tx_hash == "pending":
            return False
        base = (base_url or BP_EXPLORER_URL).rstrip("/") + "/"
        if "{tx_hash}" in base:
            return base.format(tx_hash=tx_hash)
        return "%s%s" % (base, tx_hash)
