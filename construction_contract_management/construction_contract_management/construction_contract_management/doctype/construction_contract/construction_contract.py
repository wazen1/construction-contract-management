frappe.whitelist = True

# Copyright (c) 2023, Manus and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class ConstructionContract(Document):
    def autoname(self):
        # Auto-generate contract number
        self.contract_number = make_autoname("CONTRACT-.YYYY.-.####")
        self.name = self.contract_number
    
    def validate(self):
        # Validate mandatory fields
        if not self.project_reference:
            frappe.throw("Project Reference is mandatory")
        if not self.contractor_reference:
            frappe.throw("Contractor Reference is mandatory")
        if not self.start_date:
            frappe.throw("Start Date is mandatory")
        if not self.end_date:
            frappe.throw("End Date is mandatory")
        
        # Validate date logic
        if self.start_date and self.end_date and self.start_date > self.end_date:
            frappe.throw("End Date cannot be before Start Date")
        
        # Calculate total milestone amount
        self.calculate_milestone_total()
    
    def calculate_milestone_total(self):
        """Calculate the total of all milestone amounts"""
        total = 0
        for milestone in self.milestones:
            total += milestone.amount
        
        # Set warning if milestone total doesn't match contract value
        if self.contract_value and total != self.contract_value:
            frappe.msgprint(f"Warning: Total milestone amount ({total}) does not match contract value ({self.contract_value})")
