# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
import json
import csv
import io
from frappe.utils.csvutils import read_csv_content

@frappe.whitelist()
def get_boq_template():
    """Generate a CSV template for Bill of Quantities import"""
    headers = ["Item Code", "Description", "Quantity", "UOM", "Estimated Unit Rate"]
    
    # Create a CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    
    # Add a sample row
    writer.writerow(["ITEM001", "Sample Item Description", "10", "Nos", "100"])
    
    return output.getvalue()

@frappe.whitelist()
def import_boq(tender_id, csv_content):
    """Import BoQ items from CSV"""
    if not frappe.has_permission("Project Tender", "write"):
        frappe.throw("Not permitted")
        
    rows = read_csv_content(csv_content)
    headers = rows[0]
    
    # Validate headers
    required_headers = ["Item Code", "Description", "Quantity", "UOM", "Estimated Unit Rate"]
    for header in required_headers:
        if header not in headers:
            frappe.throw(f"Required header '{header}' not found in CSV")
    
    # Process rows
    for i, row in enumerate(rows[1:], 1):
        if len(row) != len(headers):
            frappe.throw(f"Row {i} has incorrect number of columns")
            
        # Create dictionary from row
        row_dict = dict(zip(headers, row))
        
        # Create BoQ item
        boq_item = frappe.get_doc({
            "doctype": "Bill of Quantities",
            "parent_tender": tender_id,
            "item_code": row_dict["Item Code"],
            "description": row_dict["Description"],
            "quantity": float(row_dict["Quantity"]),
            "uom": row_dict["UOM"],
            "estimated_unit_rate": float(row_dict["Estimated Unit Rate"])
        })
        
        boq_item.insert()
    
    # Update tender
    tender = frappe.get_doc("Project Tender", tender_id)
    tender.calculate_total_boq_value()
    tender.save()
    
    return {
        "status": "success",
        "message": f"Imported {len(rows) - 1} BoQ items"
    }

@frappe.whitelist()
def export_boq(tender_id):
    """Export BoQ items to CSV"""
    if not frappe.has_permission("Project Tender", "read"):
        frappe.throw("Not permitted")
        
    boq_items = frappe.get_all(
        "Bill of Quantities",
        filters={"parent_tender": tender_id},
        fields=["item_code", "description", "quantity", "uom", "estimated_unit_rate", "total_amount"]
    )
    
    headers = ["Item Code", "Description", "Quantity", "UOM", "Estimated Unit Rate", "Total Amount"]
    
    # Create a CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    
    for item in boq_items:
        writer.writerow([
            item.item_code,
            item.description,
            item.quantity,
            item.uom,
            item.estimated_unit_rate,
            item.total_amount
        ])
    
    return output.getvalue()
