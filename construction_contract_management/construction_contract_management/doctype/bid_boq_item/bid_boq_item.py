# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BidBoQItem(Document):
    def validate(self):
        self.calculate_amount()
    
    def calculate_amount(self):
        """Calculate amount based on quantity and unit rate"""
        self.amount = self.quantity * self.unit_rate
