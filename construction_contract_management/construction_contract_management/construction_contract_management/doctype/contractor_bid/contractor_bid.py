frappe.whitelist = True

# Copyright (c) 2023, Manus and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class ContractorBid(Document):
    def autoname(self):
        # Auto-generate bid number
        self.name = make_autoname("BID-.YYYY.-.####")
    
    def validate(self):
        # Validate mandatory fields
        if not self.bidder:
            frappe.throw("Bidder Information is mandatory")
        if not self.tender_reference:
            frappe.throw("Tender Reference is mandatory")
        
        # Calculate total from BoQ breakdown
        self.calculate_total_bid_amount()
    
    def calculate_total_bid_amount(self):
        """Calculate the total bid amount from the BoQ price breakdown"""
        total = 0
        for item in self.boq_price_breakdown:
            item.total_amount = item.quantity * item.unit_rate
            total += item.total_amount
        
        # Only update if calculated from breakdown
        if self.boq_price_breakdown:
            self.bid_amount = total
