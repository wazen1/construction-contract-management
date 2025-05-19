# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}
        
    if not filters.get("tender"):
        frappe.throw(_("Please select a Tender to analyze"))
        
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data, None, None, None

def get_columns():
    return [
        {
            "fieldname": "bid_id",
            "label": _("Bid ID"),
            "fieldtype": "Link",
            "options": "Contractor Bid",
            "width": 120
        },
        {
            "fieldname": "bidder_name",
            "label": _("Bidder"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "bid_amount",
            "label": _("Bid Amount"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "variance_from_budget",
            "label": _("Variance from Budget (%)"),
            "fieldtype": "Percent",
            "width": 150
        },
        {
            "fieldname": "variance_from_average",
            "label": _("Variance from Average (%)"),
            "fieldtype": "Percent",
            "width": 150
        },
        {
            "fieldname": "workflow_state",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "technical_score",
            "label": _("Technical Score"),
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "financial_score",
            "label": _("Financial Score"),
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "total_score",
            "label": _("Total Score"),
            "fieldtype": "Float",
            "width": 120
        }
    ]

def get_data(filters):
    # Get tender details
    tender = frappe.get_doc("Project Tender", filters.get("tender"))
    budget = tender.initial_budget_amount
    
    # Get all bids for the tender
    bids = frappe.get_all("Contractor Bid", 
        filters={"tender_reference": filters.get("tender")},
        fields=["name as bid_id", "bidder_name", "bid_amount", "workflow_state"]
    )
    
    # Calculate average bid amount
    if bids:
        avg_bid = sum(bid.bid_amount for bid in bids) / len(bids)
    else:
        avg_bid = 0
    
    # Get technical and financial evaluation scores
    for bid in bids:
        # Get technical evaluation score
        tech_eval = frappe.db.get_value("Bid Technical Evaluation", 
            {"bid": bid.bid_id}, 
            "total_score"
        ) or 0
        
        # Get financial evaluation score
        fin_eval = frappe.db.get_value("Bid Financial Evaluation", 
            {"bid": bid.bid_id}, 
            "total_score"
        ) or 0
        
        bid.technical_score = tech_eval
        bid.financial_score = fin_eval
        bid.total_score = (tech_eval * 0.6) + (fin_eval * 0.4)  # Assuming 60-40 weightage
        
        # Calculate variances
        if budget:
            bid.variance_from_budget = ((bid.bid_amount - budget) / budget) * 100
        else:
            bid.variance_from_budget = 0
            
        if avg_bid:
            bid.variance_from_average = ((bid.bid_amount - avg_bid) / avg_bid) * 100
        else:
            bid.variance_from_average = 0
    
    # Sort by total score descending
    bids.sort(key=lambda x: x.total_score, reverse=True)
    
    return bids
