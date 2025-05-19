# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
import json

@frappe.whitelist()
def generate_bid_comparison(tender_id):
    """Generate a comparison matrix for all bids on a tender"""
    if not frappe.has_permission("Project Tender", "read"):
        frappe.throw("Not permitted")
        
    # Get all bids for the tender
    bids = frappe.get_all(
        "Contractor Bid",
        filters={"tender_reference": tender_id, "workflow_state": ["in", ["Submitted", "Technical Evaluation", "Financial Evaluation", "Selected"]]},
        fields=["name", "bidder", "bid_amount", "workflow_state"]
    )
    
    if not bids:
        return {
            "status": "error",
            "message": "No valid bids found for this tender"
        }
    
    # Get BoQ items for comparison
    boq_items = frappe.get_all(
        "Bill of Quantities",
        filters={"parent_tender": tender_id},
        fields=["item_code", "description"]
    )
    
    # Get bid breakdown for each bid
    comparison_data = {
        "bids": [],
        "items": []
    }
    
    for bid in bids:
        bid_data = {
            "bid_id": bid.name,
            "bidder_name": frappe.get_value("Supplier", bid.bidder, "supplier_name"),
            "bid_amount": bid.bid_amount,
            "status": bid.workflow_state,
            "items": {}
        }
        
        # Get bid breakdown items
        bid_items = frappe.get_all(
            "Bid BoQ Item",
            filters={"parent": bid.name},
            fields=["item_code", "description", "quantity", "unit_rate", "amount"]
        )
        
        for item in bid_items:
            bid_data["items"][item.item_code] = {
                "unit_rate": item.unit_rate,
                "amount": item.amount
            }
        
        comparison_data["bids"].append(bid_data)
    
    # Add item details
    for item in boq_items:
        item_data = {
            "item_code": item.item_code,
            "description": item.description,
            "bid_rates": {}
        }
        
        for bid in comparison_data["bids"]:
            if item.item_code in bid["items"]:
                item_data["bid_rates"][bid["bid_id"]] = bid["items"][item.item_code]["unit_rate"]
            else:
                item_data["bid_rates"][bid["bid_id"]] = None
        
        comparison_data["items"].append(item_data)
    
    return {
        "status": "success",
        "data": comparison_data
    }
