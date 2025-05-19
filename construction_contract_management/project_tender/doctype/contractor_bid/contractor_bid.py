# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow
from frappe.utils import flt

class ContractorBid(Document):
    def validate(self):
        self.validate_bid_amount()
        self.validate_boq_breakdown()
        
    def validate_bid_amount(self):
        """Ensure bid amount matches BoQ breakdown total"""
        total = sum(item.amount for item in self.boq_breakdown)
        if flt(total, 2) != flt(self.bid_amount, 2):
            frappe.throw(f"Bid Amount ({self.bid_amount}) does not match BoQ breakdown total ({total})")
    
    def validate_boq_breakdown(self):
        """Ensure all BoQ items are included in the breakdown"""
        tender_boq = frappe.get_doc("Bill of Quantities", {"project_tender": self.tender_reference, "is_latest_version": 1})
        
        # Create a set of item codes in the bid
        bid_items = {item.item_code for item in self.boq_breakdown}
        
        # Check if all tender BoQ items are in the bid
        for item in tender_boq.items:
            if item.item_code not in bid_items:
                frappe.throw(f"BoQ item {item.item_code} is missing from the bid breakdown")
    
    def on_update(self):
        """Update bid status based on workflow"""
        if self.workflow_state == "Submitted":
            self.notify_evaluators()
    
    def notify_evaluators(self):
        """Notify bid evaluators when a new bid is submitted"""
        recipients = frappe.get_all("User", 
            filters={"role": "Bid Evaluator"},
            fields=["email"]
        )
        
        if recipients:
            tender = frappe.get_doc("Project Tender", self.tender_reference)
            subject = f"New Bid Submitted: {self.name} for Tender {tender.name}"
            message = f"""
            <p>A new bid has been submitted:</p>
            <ul>
                <li><strong>Bid ID:</strong> {self.name}</li>
                <li><strong>Tender:</strong> {tender.name} - {tender.project_title}</li>
                <li><strong>Bidder:</strong> {self.bidder_name}</li>
                <li><strong>Bid Amount:</strong> {self.bid_amount}</li>
            </ul>
            <p>Please review the bid for evaluation.</p>
            """
            
            frappe.sendmail(
                recipients=[r.email for r in recipients],
                subject=subject,
                message=message
            )
    
    def generate_comparison_matrix(self):
        """Generate a comparison matrix with other bids for the same tender"""
        other_bids = frappe.get_all("Contractor Bid", 
            filters={
                "tender_reference": self.tender_reference,
                "name": ["!=", self.name],
                "workflow_state": ["in", ["Technical Evaluation", "Financial Evaluation", "Selected"]]
            },
            fields=["name", "bidder_name", "bid_amount"]
        )
        
        matrix = {
            "current_bid": {
                "name": self.name,
                "bidder": self.bidder_name,
                "amount": self.bid_amount
            },
            "other_bids": other_bids,
            "tender": self.tender_reference
        }
        
        return matrix
