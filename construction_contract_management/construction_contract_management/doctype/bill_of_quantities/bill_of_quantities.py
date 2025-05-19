# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BillofQuantities(Document):
    def validate(self):
        self.calculate_total_amount()
    
    def calculate_total_amount(self):
        """Calculate total amount based on quantity and unit rate"""
        self.total_amount = self.quantity * self.estimated_unit_rate
    
    def after_save(self):
        """Update parent tender's total BoQ value"""
        if self.parent_tender:
            parent = frappe.get_doc("Project Tender", self.parent_tender)
            parent.calculate_total_boq_value()
            parent.save()
