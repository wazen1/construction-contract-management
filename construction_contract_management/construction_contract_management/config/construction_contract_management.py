# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
    return [
        {
            "label": _("Contract Management"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Project Tender",
                    "description": _("Project Tenders"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Bill of Quantities",
                    "description": _("Bill of Quantities"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Contractor Bid",
                    "description": _("Contractor Bids"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Construction Contract",
                    "description": _("Construction Contracts"),
                    "onboard": 1,
                }
            ]
        },
        {
            "label": _("Reports"),
            "items": [
                {
                    "type": "report",
                    "name": "Tender Status Report",
                    "doctype": "Project Tender",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "Contract Status Report",
                    "doctype": "Construction Contract",
                    "is_query_report": True
                }
            ]
        },
        {
            "label": _("Tools"),
            "items": [
                {
                    "type": "page",
                    "name": "bid-comparison-tool",
                    "label": _("Bid Comparison Tool"),
                    "description": _("Compare contractor bids")
                },
                {
                    "type": "page",
                    "name": "boq-import-export",
                    "label": _("BoQ Import/Export"),
                    "description": _("Import/Export Bill of Quantities")
                }
            ]
        }
    ]
