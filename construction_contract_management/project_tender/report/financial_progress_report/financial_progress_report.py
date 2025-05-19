# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
    if not filters:
        filters = {}
        
    columns = get_columns()
    data = get_data(filters)
    
    chart = get_chart(data)
    
    return columns, data, None, chart, None

def get_columns():
    return [
        {
            "fieldname": "contract_id",
            "label": _("Contract ID"),
            "fieldtype": "Link",
            "options": "Construction Contract",
            "width": 120
        },
        {
            "fieldname": "project",
            "label": _("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "width": 120
        },
        {
            "fieldname": "contractor",
            "label": _("Contractor"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "contract_value",
            "label": _("Contract Value"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "planned_payment",
            "label": _("Planned Payment"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "actual_payment",
            "label": _("Actual Payment"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "payment_variance",
            "label": _("Payment Variance"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "variance_percent",
            "label": _("Variance (%)"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "retention_amount",
            "label": _("Retention Amount"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "pending_invoices",
            "label": _("Pending Invoices"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "budget_consumed",
            "label": _("Budget Consumed (%)"),
            "fieldtype": "Percent",
            "width": 120
        }
    ]

def get_data(filters):
    conditions = ""
    if filters.get("contractor"):
        conditions += f" AND cc.contractor_reference = '{filters.get('contractor')}'"
    
    if filters.get("project"):
        conditions += f" AND cc.project_reference = '{filters.get('project')}'"
    
    if filters.get("from_date"):
        conditions += f" AND cc.start_date >= '{filters.get('from_date')}'"
    
    if filters.get("to_date"):
        conditions += f" AND cc.end_date <= '{filters.get('to_date')}'"
    
    data = frappe.db.sql("""
        SELECT 
            cc.name as contract_id,
            cc.project_reference as project,
            s.supplier_name as contractor,
            cc.contract_value,
            (SELECT SUM(cm.amount) FROM `tabContract Milestone` cm 
             WHERE cm.parent = cc.name AND cm.due_date <= CURDATE()) as planned_payment,
            (SELECT SUM(pe.paid_amount) FROM `tabPayment Entry` pe 
             WHERE pe.party = cc.contractor_reference AND pe.project = cc.project_reference AND pe.docstatus = 1) as actual_payment,
            (SELECT SUM(pi.outstanding_amount) FROM `tabPurchase Invoice` pi 
             WHERE pi.supplier = cc.contractor_reference AND pi.project = cc.project_reference AND pi.docstatus = 1) as pending_invoices,
            (SELECT SUM(je.debit) FROM `tabJournal Entry Account` je 
             JOIN `tabJournal Entry` j ON j.name = je.parent
             WHERE je.party = cc.contractor_reference AND je.project = cc.project_reference 
             AND j.docstatus = 1 AND je.account LIKE '%Retention%') as retention_amount
        FROM 
            `tabConstruction Contract` cc
        LEFT JOIN 
            `tabSupplier` s ON s.name = cc.contractor_reference
        WHERE 
            cc.docstatus = 1
            {conditions}
        ORDER BY 
            cc.end_date DESC
    """.format(conditions=conditions), as_dict=1)
    
    # Calculate additional metrics
    for row in data:
        # Calculate payment variance
        row.planned_payment = flt(row.planned_payment)
        row.actual_payment = flt(row.actual_payment)
        row.payment_variance = row.planned_payment - row.actual_payment
        
        # Calculate variance percentage
        if row.planned_payment:
            row.variance_percent = (row.payment_variance / row.planned_payment) * 100
        else:
            row.variance_percent = 0
            
        # Calculate budget consumed percentage
        if row.contract_value:
            row.budget_consumed = (row.actual_payment / row.contract_value) * 100
        else:
            row.budget_consumed = 0
            
        # Ensure values are not None
        row.retention_amount = flt(row.retention_amount)
        row.pending_invoices = flt(row.pending_invoices)
    
    return data

def get_chart(data):
    if not data:
        return None
        
    labels = [row.contract_id for row in data]
    planned_values = [row.planned_payment for row in data]
    actual_values = [row.actual_payment for row in data]
    
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Planned Payment",
                    "values": planned_values
                },
                {
                    "name": "Actual Payment",
                    "values": actual_values
                }
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff", "#7cd6fd"]
    }
