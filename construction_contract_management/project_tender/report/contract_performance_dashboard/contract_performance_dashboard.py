# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, today, date_diff

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
            "fieldname": "start_date",
            "label": _("Start Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "end_date",
            "label": _("End Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "duration",
            "label": _("Duration (Days)"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "completed_milestones",
            "label": _("Completed Milestones"),
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "total_milestones",
            "label": _("Total Milestones"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "progress",
            "label": _("Progress (%)"),
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "fieldname": "amount_paid",
            "label": _("Amount Paid"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "payment_progress",
            "label": _("Payment Progress (%)"),
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "fieldname": "time_elapsed",
            "label": _("Time Elapsed (%)"),
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
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
            cc.start_date,
            cc.end_date,
            DATEDIFF(cc.end_date, cc.start_date) as duration,
            (SELECT COUNT(*) FROM `tabContract Milestone` cm WHERE cm.parent = cc.name AND cm.status = 'Completed') as completed_milestones,
            (SELECT COUNT(*) FROM `tabContract Milestone` cm WHERE cm.parent = cc.name) as total_milestones,
            (SELECT SUM(pe.paid_amount) FROM `tabPayment Entry` pe 
             WHERE pe.party = cc.contractor_reference AND pe.project = cc.project_reference AND pe.docstatus = 1) as amount_paid
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
    today_date = getdate(today())
    for row in data:
        # Calculate progress percentage
        if row.total_milestones:
            row.progress = (row.completed_milestones / row.total_milestones) * 100
        else:
            row.progress = 0
            
        # Calculate payment progress
        if row.contract_value:
            row.payment_progress = (row.amount_paid or 0) / row.contract_value * 100
        else:
            row.payment_progress = 0
            
        # Calculate time elapsed
        start_date = getdate(row.start_date)
        end_date = getdate(row.end_date)
        
        if start_date and end_date:
            total_days = date_diff(end_date, start_date)
            days_elapsed = date_diff(today_date, start_date)
            
            if total_days > 0:
                row.time_elapsed = min(100, max(0, (days_elapsed / total_days) * 100))
            else:
                row.time_elapsed = 100
        else:
            row.time_elapsed = 0
            
        # Determine status
        if today_date > end_date:
            if row.progress < 100:
                row.status = "Overdue"
            else:
                row.status = "Completed"
        else:
            if row.progress >= row.time_elapsed:
                row.status = "On Track"
            else:
                row.status = "Delayed"
    
    return data

def get_chart(data):
    if not data:
        return None
        
    labels = [row.contract_id for row in data]
    progress_values = [row.progress for row in data]
    payment_values = [row.payment_progress for row in data]
    time_values = [row.time_elapsed for row in data]
    
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Progress",
                    "values": progress_values
                },
                {
                    "name": "Payment",
                    "values": payment_values
                },
                {
                    "name": "Time Elapsed",
                    "values": time_values
                }
            ]
        },
        "type": "bar",
        "colors": ["#7cd6fd", "#5e64ff", "#ff5858"]
    }
