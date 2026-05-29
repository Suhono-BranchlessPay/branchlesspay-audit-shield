# -*- coding: utf-8 -*-

from odoo import fields, models

from ..services.bp_api_service import BPApiService


class ReportBpAuditTrail(models.AbstractModel):
    _name = "report.branchlesspay_audit_shield.bp_audit_trail_document"
    _description = "BranchlessPay Audit Trail PDF"

    def _get_report_values(self, docids, data=None):
        doc_model = (data or {}).get("doc_model") or self.env.context.get(
            "active_model", "account.move"
        )
        docs = self.env[doc_model].browse(docids)
        icp = self.env["ir.config_parameter"].sudo()
        explorer_base = icp.get_param(
            "bp_audit.explorer_url",
            "https://testnet.monadexplorer.com/tx/",
        )
        logs = self.env["bp.anchor.log"]
        records = []
        for doc in docs:
            entries = logs.search(
                [("res_model", "=", doc._name), ("res_id", "=", doc.id)],
                order="create_date asc",
            )
            records.append(
                {
                    "doc": doc,
                    "entries": entries,
                    "explorer_url": BPApiService.explorer_url(
                        doc.bp_tx_hash, explorer_base
                    ),
                }
            )
        return {
            "doc_ids": docids,
            "doc_model": docs._name if docs else doc_model,
            "docs": docs,
            "records": records,
            "company": self.env.company,
            "context_timestamp": fields.Datetime.now(),
        }
