# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days, add_months, today, flt, format_date
from frappe.model.naming import make_autoname

class ConstructionContract(Document):
    def autoname(self):
        self.name = make_autoname("CONTRACT-.YYYY.-.####")
    
    def validate(self):
        self.validate_dates()
        self.validate_milestones()
        self.sync_with_project()
    
    def validate_dates(self):
        """Validate contract start and end dates"""
        if self.start_date and self.end_date:
            if getdate(self.start_date) > getdate(self.end_date):
                frappe.throw("End Date cannot be before Start Date")
    
    def validate_milestones(self):
        """Validate milestone dates and amounts"""
        total_milestone_amount = 0
        
        for milestone in self.milestones:
            # Validate milestone date is within contract period
            if milestone.due_date:
                if getdate(milestone.due_date) < getdate(self.start_date):
                    frappe.throw(f"Milestone '{milestone.description}' due date cannot be before contract start date")
                
                if getdate(milestone.due_date) > getdate(self.end_date):
                    frappe.throw(f"Milestone '{milestone.description}' due date cannot be after contract end date")
            
            # Sum up milestone amounts
            total_milestone_amount += milestone.amount
        
        # Validate total milestone amount matches contract value
        if total_milestone_amount != self.contract_value:
            frappe.throw(f"Total milestone amount ({total_milestone_amount}) does not match contract value ({self.contract_value})")
    
    def sync_with_project(self):
        """Sync contract details with the linked project"""
        if self.project_reference:
            project = frappe.get_doc("Project", self.project_reference)
            
            # Update project expected start and end dates
            if self.start_date:
                project.expected_start_date = self.start_date
            
            if self.end_date:
                project.expected_end_date = self.end_date
            
            # Create project tasks from milestones if they don't exist
            for milestone in self.milestones:
                task_exists = frappe.db.exists("Task", {
                    "project": self.project_reference,
                    "subject": f"Milestone: {milestone.description}"
                })
                
                if not task_exists:
                    task = frappe.new_doc("Task")
                    task.project = self.project_reference
                    task.subject = f"Milestone: {milestone.description}"
                    task.description = milestone.description
                    task.exp_start_date = self.start_date
                    task.exp_end_date = milestone.due_date
                    task.insert()
            
            project.save()
    
    def on_submit(self):
        """Actions to perform when contract is submitted"""
        self.create_project_if_not_exists()
        self.setup_accounting_entries()
        self.setup_notifications()
    
    def create_project_if_not_exists(self):
        """Create a project if it doesn't exist"""
        if not self.project_reference:
            project = frappe.new_doc("Project")
            project.project_name = f"Contract: {self.name}"
            project.expected_start_date = self.start_date
            project.expected_end_date = self.end_date
            project.customer = frappe.get_value("Supplier", self.contractor_reference, "customer")
            project.status = "Open"
            project.insert()
            
            self.project_reference = project.name
            self.save()
    
    def setup_accounting_entries(self):
        """Setup accounting entries for the contract"""
        # Create a project budget
        if self.project_reference:
            budget = frappe.new_doc("Budget")
            budget.budget_against = "Project"
            budget.project = self.project_reference
            budget.company = frappe.defaults.get_user_default("Company")
            budget.fiscal_year = frappe.defaults.get_user_default("fiscal_year")
            budget.from_date = self.start_date
            budget.to_date = self.end_date
            budget.action_if_annual_budget_exceeded = "Stop"
            budget.monthly_distribution = self.create_monthly_distribution()
            
            # Add budget accounts
            account = frappe.db.get_value("Account", {"account_type": "Expense", "is_group": 0}, "name")
            if account:
                budget.append("accounts", {
                    "account": account,
                    "budget_amount": self.contract_value
                })
            
            budget.insert()
            budget.submit()
    
    def create_monthly_distribution(self):
        """Create monthly distribution for budget based on contract duration"""
        if not self.start_date or not self.end_date:
            return None
            
        start = getdate(self.start_date)
        end = getdate(self.end_date)
        
        # Calculate number of months in contract
        months = (end.year - start.year) * 12 + end.month - start.month + 1
        
        if months <= 0:
            return None
            
        # Create even distribution
        monthly_percentage = 100.0 / months
        
        # Create monthly distribution
        md = frappe.new_doc("Monthly Distribution")
        md.name = f"Contract {self.name} Distribution"
        md.fiscal_year = frappe.defaults.get_user_default("fiscal_year")
        
        current_date = start
        while current_date <= end:
            md.append("percentages", {
                "month": current_date.strftime("%B"),
                "percentage_allocation": monthly_percentage
            })
            current_date = add_months(current_date, 1)
        
        md.insert()
        return md.name
    
    def setup_notifications(self):
        """Setup notifications for contract milestones"""
        for milestone in self.milestones:
            # Create notification 5 days before milestone due date
            if milestone.due_date:
                reminder_date = add_days(getdate(milestone.due_date), -5)
                
                if getdate(reminder_date) >= getdate(today()):
                    frappe.get_doc({
                        "doctype": "Notification",
                        "subject": f"Upcoming Milestone: {milestone.description}",
                        "document_type": "Construction Contract",
                        "event": "Days Before",
                        "days_in_advance": 5,
                        "message": f"""
                        <p>This is a reminder for an upcoming milestone in contract {self.name}:</p>
                        <ul>
                            <li><strong>Milestone:</strong> {milestone.description}</li>
                            <li><strong>Due Date:</strong> {milestone.due_date}</li>
                            <li><strong>Amount:</strong> {milestone.amount}</li>
                        </ul>
                        <p>Please ensure all preparations are complete.</p>
                        """,
                        "recipients": [
                            {"receiver_by_role": "Project Manager"},
                            {"receiver_by_role": "Contract Manager"}
                        ]
                    }).insert()
    
    def generate_contract_document(self):
        """Generate a contract document based on template"""
        # This would typically use a document generator like WeasyPrint or similar
        # For demonstration, we'll return a simple HTML structure
        
        html_content = f"""
        <h1>Construction Contract</h1>
        <p><strong>Contract Number:</strong> {self.name}</p>
        <p><strong>Project:</strong> {self.project_reference}</p>
        <p><strong>Contractor:</strong> {self.contractor_reference}</p>
        <p><strong>Contract Period:</strong> {self.start_date} to {self.end_date}</p>
        <p><strong>Contract Value:</strong> {self.contract_value}</p>
        
        <h2>Payment Terms</h2>
        <p>{self.payment_terms}</p>
        
        <h2>Milestones</h2>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>Description</th>
                <th>Due Date</th>
                <th>Amount</th>
                <th>Status</th>
            </tr>
        """
        
        for milestone in self.milestones:
            html_content += f"""
            <tr>
                <td>{milestone.description}</td>
                <td>{milestone.due_date}</td>
                <td>{milestone.amount}</td>
                <td>{milestone.status}</td>
            </tr>
            """
        
        html_content += """
        </table>
        
        <h2>Signatures</h2>
        <div style="display: flex; justify-content: space-between; margin-top: 50px;">
            <div>
                <p>_______________________</p>
                <p>Client Representative</p>
            </div>
            <div>
                <p>_______________________</p>
                <p>Contractor Representative</p>
            </div>
        </div>
        """
        
        return html_content

# Add the missing methods referenced in hooks.py
@frappe.whitelist()
def check_milestone_status():
    """
    Check the status of contract milestones and update accordingly.
    This function is called by the scheduler daily.
    """
    today_date = getdate(today())
    
    # Get all active contracts
    contracts = frappe.get_all(
        "Construction Contract",
        filters={"docstatus": 1},
        fields=["name"]
    )
    
    updated_count = 0
    
    for contract_data in contracts:
        contract = frappe.get_doc("Construction Contract", contract_data.name)
        
        for milestone in contract.milestones:
            # Check if milestone is due but not completed
            if milestone.status in ["Pending", "In Progress"] and getdate(milestone.due_date) < today_date:
                milestone.status = "Delayed"
                updated_count += 1
        
        if updated_count > 0:
            contract.save()
            
            # Notify project manager about delayed milestones
            recipients = frappe.get_all(
                "User",
                filters={"role": "Project Manager"},
                fields=["email"]
            )
            
            if recipients:
                subject = f"Delayed Milestones in Contract {contract.name}"
                message = f"""
                <p>The following contract has delayed milestones:</p>
                <ul>
                    <li><strong>Contract:</strong> {contract.name}</li>
                    <li><strong>Project:</strong> {contract.project_reference}</li>
                    <li><strong>Contractor:</strong> {contract.contractor_reference}</li>
                </ul>
                <p>Please review the contract and take necessary actions.</p>
                """
                
                frappe.sendmail(
                    recipients=[r.email for r in recipients],
                    subject=subject,
                    message=message
                )
    
    frappe.logger().info(f"Updated status for {updated_count} milestones")
    return updated_count

@frappe.whitelist()
def send_weekly_progress_report():
    """
    Generate and send weekly progress reports for active contracts.
    This function is called by the scheduler weekly.
    """
    # Get all active contracts
    contracts = frappe.get_all(
        "Construction Contract",
        filters={
            "docstatus": 1,
            "start_date": ["<=", today()],
            "end_date": [">=", today()]
        },
        fields=["name", "project_reference", "contractor_reference", "contract_value", "start_date", "end_date"]
    )
    
    for contract_data in contracts:
        # Get contract details
        contract = frappe.get_doc("Construction Contract", contract_data.name)
        
        # Calculate progress metrics
        total_milestones = len(contract.milestones)
        completed_milestones = sum(1 for m in contract.milestones if m.status == "Completed")
        progress_percentage = (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
        
        # Get financial data
        payments = frappe.get_all(
            "Payment Entry",
            filters={
                "project": contract.project_reference,
                "party": contract.contractor_reference,
                "docstatus": 1
            },
            fields=["sum(paid_amount) as total_paid"]
        )
        
        total_paid = payments[0].total_paid if payments and payments[0].total_paid else 0
        payment_percentage = (total_paid / contract.contract_value * 100) if contract.contract_value > 0 else 0
        
        # Generate report
        report_html = f"""
        <h2>Weekly Progress Report: {contract.name}</h2>
        <p><strong>Period:</strong> {format_date(add_days(today(), -7))} to {format_date(today())}</p>
        
        <h3>Contract Details</h3>
        <ul>
            <li><strong>Contract:</strong> {contract.name}</li>
            <li><strong>Project:</strong> {contract.project_reference}</li>
            <li><strong>Contractor:</strong> {contract.contractor_reference}</li>
            <li><strong>Contract Value:</strong> {contract.contract_value}</li>
            <li><strong>Duration:</strong> {format_date(contract.start_date)} to {format_date(contract.end_date)}</li>
        </ul>
        
        <h3>Progress Summary</h3>
        <ul>
            <li><strong>Milestones Completed:</strong> {completed_milestones} of {total_milestones} ({progress_percentage:.2f}%)</li>
            <li><strong>Payments Made:</strong> {total_paid} ({payment_percentage:.2f}% of contract value)</li>
        </ul>
        
        <h3>Recent Milestone Updates</h3>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>Milestone</th>
                <th>Due Date</th>
                <th>Status</th>
            </tr>
        """
        
        for milestone in contract.milestones:
            report_html += f"""
            <tr>
                <td>{milestone.description}</td>
                <td>{format_date(milestone.due_date)}</td>
                <td>{milestone.status}</td>
            </tr>
            """
        
        report_html += """
        </table>
        
        <p>Please review this report and take necessary actions if there are any delays or issues.</p>
        """
        
        # Send report to stakeholders
        recipients = frappe.get_all(
            "User",
            filters={"role": ["in", ["Project Manager", "Contract Manager", "Finance Manager"]]},
            fields=["email"]
        )
        
        if recipients:
            frappe.sendmail(
                recipients=[r.email for r in recipients],
                subject=f"Weekly Progress Report: Contract {contract.name}",
                message=report_html
            )
    
    frappe.logger().info(f"Sent weekly progress reports for {len(contracts)} contracts")
    return len(contracts)

@frappe.whitelist()
def generate_monthly_performance_report():
    """
    Generate monthly performance reports for all contracts.
    This function is called by the scheduler monthly.
    """
    # Get all contracts
    contracts = frappe.get_all(
        "Construction Contract",
        filters={"docstatus": 1},
        fields=["name"]
    )
    
    # Prepare monthly report data
    month_start = today().replace(day=1)
    prev_month_end = add_days(month_start, -1)
    prev_month_start = prev_month_end.replace(day=1)
    
    report_html = f"""
    <h1>Monthly Contract Performance Report</h1>
    <p><strong>Period:</strong> {format_date(prev_month_start)} to {format_date(prev_month_end)}</p>
    
    <h2>Contract Performance Summary</h2>
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>Contract</th>
            <th>Project</th>
            <th>Contractor</th>
            <th>Progress</th>
            <th>Financial Status</th>
            <th>Schedule Status</th>
        </tr>
    """
    
    for contract_data in contracts:
        contract = frappe.get_doc("Construction Contract", contract_data.name)
        
        # Calculate progress
        total_milestones = len(contract.milestones)
        completed_milestones = sum(1 for m in contract.milestones if m.status == "Completed")
        progress_percentage = (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
        
        # Get financial data
        payments = frappe.get_all(
            "Payment Entry",
            filters={
                "project": contract.project_reference,
                "party": contract.contractor_reference,
                "docstatus": 1
            },
            fields=["sum(paid_amount) as total_paid"]
        )
        
        total_paid = payments[0].total_paid if payments and payments[0].total_paid else 0
        payment_percentage = (total_paid / contract.contract_value * 100) if contract.contract_value > 0 else 0
        
        # Determine schedule status
        delayed_milestones = sum(1 for m in contract.milestones if m.status == "Delayed")
        if delayed_milestones > 0:
            schedule_status = f"Delayed ({delayed_milestones} milestones)"
        else:
            schedule_status = "On Schedule"
        
        report_html += f"""
        <tr>
            <td>{contract.name}</td>
            <td>{contract.project_reference}</td>
            <td>{contract.contractor_reference}</td>
            <td>{progress_percentage:.2f}%</td>
            <td>{payment_percentage:.2f}% paid (₹{total_paid})</td>
            <td>{schedule_status}</td>
        </tr>
        """
    
    report_html += """
    </table>
    
    <h2>Performance Analysis</h2>
    <p>This section provides an analysis of contract performance trends over the past month.</p>
    
    <h3>Key Observations</h3>
    <ul>
        <li>Contracts with significant delays should be reviewed for corrective actions.</li>
        <li>Financial disbursements should be aligned with physical progress.</li>
        <li>Contractors with multiple delayed milestones may require performance reviews.</li>
    </ul>
    
    <p>Please review this report and schedule performance review meetings as necessary.</p>
    """
    
    # Send report to management
    recipients = frappe.get_all(
        "User",
        filters={"role": ["in", ["System Manager", "Finance Manager"]]},
        fields=["email"]
    )
    
    if recipients:
        frappe.sendmail(
            recipients=[r.email for r in recipients],
            subject=f"Monthly Contract Performance Report: {format_date(prev_month_start)} to {format_date(prev_month_end)}",
            message=report_html
        )
    
    frappe.logger().info(f"Generated monthly performance report for {len(contracts)} contracts")
    return len(contracts)
