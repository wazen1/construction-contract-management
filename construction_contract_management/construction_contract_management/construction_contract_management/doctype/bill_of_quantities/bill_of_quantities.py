frappe.whitelist = True

# Copyright (c) 2023, Manus and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class BillofQuantities(Document):
    def autoname(self):
        # Auto-generate BoQ number
        self.name = make_autoname("BOQ-.YYYY.-.####")
    
    def validate(self):
        # Ensure project tender is specified
        if not self.project_tender:
            frappe.throw("Project Tender is mandatory")
            
        # Ensure at least one item exists
        if not self.items or len(self.items) == 0:
            frappe.throw("Bill of Quantities must have at least one item")
            
        self.calculate_total()
    
    def calculate_total(self):
        """Calculate the total BoQ value based on all items"""
        total = 0
        for item in self.items:
            item.total_amount = item.quantity * item.estimated_unit_rate
            total += item.total_amount
        
        self.total_boq_value = total
