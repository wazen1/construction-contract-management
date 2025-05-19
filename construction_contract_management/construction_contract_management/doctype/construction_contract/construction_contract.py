# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import nowdate

class ConstructionContract(Document):
    def autoname(self):
        # Auto-generate contract number
        self.name = make_autoname("CONTRACT-.YYYY.-.####")
    
    def validate(self):
        self.validate_dates()
        self.validate_milestones()
        self.set_status()
    
    def validate_dates(self):
        """Validate start and end dates"""
        if self.start_date and self.end_date and self.start_date > self.end_date:
            frappe.throw("End Date cannot be before Start Date")
    
    def validate_milestones(self):
        """Validate milestone dates and amounts"""
        total_milestone_amount = sum(milestone.amount for milestone in self.milestones)
        
        # Allow small rounding differences
        if abs(total_milestone_amount - self.contract_value) > 0.01:
            frappe.throw("Total milestone amounts must equal the Contract Value")
            
        for milestone in self.milestones:
            if milestone.due_date and milestone.due_date < self.start_date:
                frappe.throw(f"Milestone '{milestone.description}' due date cannot be before contract start date")
            
            if milestone.due_date and self.end_date and milestone.due_date > self.end_date:
                frappe.throw(f"Milestone '{milestone.description}' due date cannot be after contract end date")
    
    def set_status(self):
        """Set contract status based on dates and milestones"""
        today = nowdate()
        
        if not self.start_date:
            self.status = "Draft"
        elif self.start_date > today:
            self.status = "Pending"
        elif self.end_date and self.end_date < today:
            # Check if all milestones are completed
            all_completed = all(milestone.status == "Completed" for milestone in self.milestones)
            self.status = "Completed" if all_completed else "Expired"
        else:
            # Check milestone status
            any_overdue = any(milestone.status == "Pending" and milestone.due_date and milestone.due_date < today for milestone in self.milestones)
            self.status = "Active" if not any_overdue else "Overdue"
    
    def generate_contract_document(self):
        """Generate contract document as PDF"""
        # This would typically use a template and frappe.utils.pdf.get_pdf
        # For simplicity, we're just returning a placeholder
        return {
            "status": "success",
            "message": "Contract document generated successfully"
        }
