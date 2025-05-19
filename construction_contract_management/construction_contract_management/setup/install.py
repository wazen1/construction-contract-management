# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe

def after_install():
    """Setup workflows and other configurations after app installation"""
    setup_workflows()
    create_custom_fields()
    
def setup_workflows():
    """Setup all workflows for the app"""
    from construction_contract_management.workflow.contractor_bid_workflow.contractor_bid_workflow import setup_workflow
    setup_workflow()
    
def create_custom_fields():
    """Create custom fields in existing doctypes"""
    # Add custom fields to Project doctype to link with tenders and contracts
    if not frappe.db.exists("Custom Field", "Project-construction_tenders"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Project",
            "label": "Construction Tenders",
            "fieldname": "construction_tenders",
            "fieldtype": "Table",
            "options": "Project Tender Link",
            "insert_after": "status"
        }).insert()
        
    if not frappe.db.exists("Custom Field", "Project-construction_contracts"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Project",
            "label": "Construction Contracts",
            "fieldname": "construction_contracts",
            "fieldtype": "Table",
            "options": "Construction Contract Link",
            "insert_after": "construction_tenders"
        }).insert()
