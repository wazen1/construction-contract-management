# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url

@frappe.whitelist()
def generate_contract_document(contract_id):
    """Generate a PDF contract document"""
    if not frappe.has_permission("Construction Contract", "read"):
        frappe.throw("Not permitted")
        
    contract = frappe.get_doc("Construction Contract", contract_id)
    
    # Get contractor and project details
    contractor = frappe.get_doc("Supplier", contract.contractor_reference)
    project = frappe.get_doc("Project", contract.project_reference)
    
    # Prepare context for the template
    context = {
        "contract": contract,
        "contractor": contractor,
        "project": project,
        "milestones": contract.milestones,
        "company": frappe.get_doc("Company", frappe.defaults.get_user_default("Company")),
        "url": get_url()
    }
    
    # Generate PDF using a template
    html = frappe.render_template(
        "construction_contract_management/templates/contract_document.html", 
        context
    )
    
    pdf_data = get_pdf(html, {"orientation": "Portrait"})
    
    # Save as attachment
    file_name = f"Contract-{contract.contract_number}.pdf"
    
    _file = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "attached_to_doctype": "Construction Contract",
        "attached_to_name": contract_id,
        "content": pdf_data,
        "is_private": 1
    })
    
    _file.insert()
    
    return {
        "status": "success",
        "message": "Contract document generated successfully",
        "file_url": _file.file_url
    }
