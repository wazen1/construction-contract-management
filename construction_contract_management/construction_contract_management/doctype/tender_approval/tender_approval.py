# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class TenderApproval(Document):
    def validate(self):
        self.validate_approver()
        
    def validate_approver(self):
        """Ensure approver has the right role"""
        roles = frappe.get_roles(self.approver)
        valid_roles = ["Tender Manager", "System Manager"]
        
        if not any(role in valid_roles for role in roles):
            frappe.throw(f"User {self.approver} does not have the required roles for tender approval")
    
    def on_update(self):
        """Update approval date when status changes"""
        if self.status in ["Approved", "Rejected"]:
            self.approval_date = now_datetime()
            
            # Update tender status if approved
            if self.status == "Approved":
                self.update_tender_status()
    
    def update_tender_status(self):
        """Update tender status based on approval count"""
        approval_count = frappe.db.count("Tender Approval", 
            filters={"tender": self.tender, "status": "Approved"}
        )
        
        if approval_count >= 2:
            frappe.db.set_value("Project Tender", self.tender, "status", "Published")
            
            # Notify stakeholders
            self.notify_publication()
    
    def notify_publication(self):
        """Notify stakeholders when tender is published"""
        tender = frappe.get_doc("Project Tender", self.tender)
        
        recipients = frappe.get_all("User", 
            filters={"role": ["in", ["Tender Manager", "Bid Evaluator", "Project Manager"]]},
            fields=["email"]
        )
        
        if recipients:
            subject = f"Tender Published: {tender.name} - {tender.project_title}"
            message = f"""
            <p>A tender has been published after receiving the required approvals:</p>
            <ul>
                <li><strong>Tender ID:</strong> {tender.name}</li>
                <li><strong>Project Title:</strong> {tender.project_title}</li>
                <li><strong>Submission Deadline:</strong> {tender.submission_deadline}</li>
                <li><strong>Initial Budget:</strong> {tender.initial_budget_amount}</li>
            </ul>
            <p>Please review the tender details in the system.</p>
            """
            
            frappe.sendmail(
                recipients=[r.email for r in recipients],
                subject=subject,
                message=message
            )
