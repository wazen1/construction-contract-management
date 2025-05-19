# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime, add_days, today

class ProjectTender(Document):
    def validate(self):
        self.validate_mandatory_fields()
        self.validate_dates()
        
    def validate_mandatory_fields(self):
        if not self.project_title:
            frappe.throw("Project Title is mandatory")
        
        if not self.initial_budget_amount:
            frappe.throw("Initial Budget Amount is mandatory")
            
        if not self.submission_deadline:
            frappe.throw("Submission Deadline is mandatory")
    
    def validate_dates(self):
        if self.submission_deadline and getdate(self.submission_deadline) < getdate(now_datetime()):
            frappe.throw("Submission Deadline cannot be in the past")
    
    def on_update(self):
        if self.status == "Published":
            self.notify_stakeholders()
    
    def notify_stakeholders(self):
        """Send notifications to relevant stakeholders when tender is published"""
        recipients = frappe.get_all("User", 
            filters={"role": ["in", ["Tender Manager", "Bid Evaluator"]]},
            fields=["email"]
        )
        
        if recipients:
            subject = f"New Tender Published: {self.name} - {self.project_title}"
            message = f"""
            <p>A new tender has been published:</p>
            <ul>
                <li><strong>Tender ID:</strong> {self.name}</li>
                <li><strong>Project Title:</strong> {self.project_title}</li>
                <li><strong>Submission Deadline:</strong> {self.submission_deadline}</li>
                <li><strong>Initial Budget:</strong> {self.initial_budget_amount}</li>
            </ul>
            <p>Please review the tender details in the system.</p>
            """
            
            frappe.sendmail(
                recipients=[r.email for r in recipients],
                subject=subject,
                message=message
            )
    
    def before_submit(self):
        """Ensure proper approvals before submission"""
        approval_count = frappe.db.count("Tender Approval", 
            filters={"tender": self.name, "status": "Approved"}
        )
        
        if approval_count < 2:
            frappe.throw("Minimum 2-level approval required before publishing tender")

# Add the missing method referenced in hooks.py
@frappe.whitelist()
def send_tender_deadline_reminders():
    """
    Send reminders for tenders with approaching deadlines.
    This function is called by the scheduler daily.
    """
    # Find tenders with deadlines in the next 5 days
    upcoming_deadline = add_days(today(), 5)
    
    tenders = frappe.get_all(
        "Project Tender",
        filters={
            "submission_deadline": ["between", [today(), upcoming_deadline]],
            "status": "Published"
        },
        fields=["name", "project_title", "submission_deadline"]
    )
    
    for tender in tenders:
        # Get stakeholders to notify
        recipients = frappe.get_all(
            "User",
            filters={"role": ["in", ["Tender Manager", "Bid Evaluator"]]},
            fields=["email"]
        )
        
        if recipients:
            subject = f"Reminder: Tender {tender.name} deadline approaching"
            message = f"""
            <p>This is a reminder that the following tender is approaching its submission deadline:</p>
            <ul>
                <li><strong>Tender ID:</strong> {tender.name}</li>
                <li><strong>Project Title:</strong> {tender.project_title}</li>
                <li><strong>Submission Deadline:</strong> {tender.submission_deadline}</li>
            </ul>
            <p>Please ensure all necessary actions are completed before the deadline.</p>
            """
            
            frappe.sendmail(
                recipients=[r.email for r in recipients],
                subject=subject,
                message=message
            )
    
    frappe.logger().info(f"Sent tender deadline reminders for {len(tenders)} tenders")
    return len(tenders)
