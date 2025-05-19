# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.workflow import create_workflow

def setup_workflow():
    """Create Contractor Bid workflow if it doesn't exist"""
    if frappe.db.exists("Workflow", "Contractor Bid"):
        return
    
    workflow = frappe.new_doc("Workflow")
    workflow.workflow_name = "Contractor Bid"
    workflow.document_type = "Contractor Bid"
    workflow.workflow_state_field = "workflow_state"
    workflow.is_active = 1
    
    # States
    workflow.states = [
        {"state": "Draft", "doc_status": 0, "allow_edit": "Projects Manager"},
        {"state": "Submitted", "doc_status": 1, "allow_edit": "Projects Manager"},
        {"state": "Technical Evaluation", "doc_status": 1, "allow_edit": "Projects Manager"},
        {"state": "Financial Evaluation", "doc_status": 1, "allow_edit": "Projects Manager"},
        {"state": "Selected", "doc_status": 1, "allow_edit": "Projects Manager"},
        {"state": "Rejected", "doc_status": 1, "allow_edit": "Projects Manager"}
    ]
    
    # Transitions
    workflow.transitions = [
        {"state": "Draft", "action": "Submit", "next_state": "Submitted", "allowed": "Projects Manager"},
        {"state": "Submitted", "action": "Start Technical Evaluation", "next_state": "Technical Evaluation", "allowed": "Projects Manager"},
        {"state": "Technical Evaluation", "action": "Start Financial Evaluation", "next_state": "Financial Evaluation", "allowed": "Projects Manager"},
        {"state": "Financial Evaluation", "action": "Select", "next_state": "Selected", "allowed": "Projects Manager"},
        {"state": "Financial Evaluation", "action": "Reject", "next_state": "Rejected", "allowed": "Projects Manager"},
        {"state": "Technical Evaluation", "action": "Reject", "next_state": "Rejected", "allowed": "Projects Manager"}
    ]
    
    workflow.insert()
