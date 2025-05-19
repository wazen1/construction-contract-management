# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow

class ContractorBid(Document):
    def validate(self):
        self.validate_bid_amount()
        self.validate_boq_breakdown()
    
    def validate_bid_amount(self):
        """Validate that bid amount matches BoQ breakdown total"""
        total_boq = sum(item.amount for item in self.boq_price_breakdown)
        if abs(self.bid_amount - total_boq) > 0.01:  # Allow small rounding differences
            frappe.throw("Bid Amount must match the total of BoQ Price Breakdown")
    
    def validate_boq_breakdown(self):
        """Ensure BoQ breakdown items match the tender BoQ items"""
        if not self.tender_reference:
            return
            
        tender_boq_items = frappe.get_all(
            "Bill of Quantities",
            filters={"parent_tender": self.tender_reference},
            fields=["item_code", "description"]
        )
        
        tender_items = {item.item_code: item.description for item in tender_boq_items}
        bid_items = {item.item_code: item.description for item in self.boq_price_breakdown}
        
        # Check if all tender items are in the bid
        for item_code in tender_items:
            if item_code not in bid_items:
                frappe.throw(f"BoQ item {item_code} is missing from the bid breakdown")
    
    def generate_comparison_matrix(self):
        """Generate comparison matrix with other bids for the same tender"""
        if not self.tender_reference:
            return {}
            
        all_bids = frappe.get_all(
            "Contractor Bid",
            filters={"tender_reference": self.tender_reference, "workflow_state": ["in", ["Submitted", "Technical Evaluation", "Financial Evaluation", "Selected"]]},
            fields=["name", "bidder", "bid_amount"]
        )
        
        return {
            "bids": all_bids,
            "current_bid": self.name
        }
