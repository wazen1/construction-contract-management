# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}
    
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "contract_number",
            "label": _("Contract Number"),
            "fieldtype": "Link",
            "options": "Construction Contract",
            "width": 130
        },
        {
            "fieldname": "project",
            "label": _("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "width": 180
        },
        {
            "fieldname": "contractor",
            "label": _("Contractor"),
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 180
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
            "fieldname": "contract_value",
            "label": _("Contract Value"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "completed_milestones",
            "label": _("Completed Milestones"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "total_milestones",
            "label": _("Total Milestones"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "completion_percentage",
            "label": _("Completion %"),
            "fieldtype": "Percent",
            "width": 100
        }
    ]

def get_data(filters):
    conditions = ""
    if filters.get("status"):
        conditions += f" AND cc.status = '{filters.get('status')}'"
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
            cc.name as contract_number,
            cc.project_reference as project,
            cc.contractor_reference as contractor,
            cc.start_date,
            cc.end_date,
            cc.contract_value,
            cc.status,
            SUM(CASE WHEN cm.status = 'Completed' THEN 1 ELSE 0 END) as completed_milestones,
            COUNT(cm.name) as total_milestones,
            (SUM(CASE WHEN cm.status = 'Completed' THEN 1 ELSE 0 END) / COUNT(cm.name)) * 100 as completion_percentage
        FROM 
            `tabConstruction Contract` cc
        LEFT JOIN 
            `tabContract Milestone` cm ON cm.parent = cc.name
        WHERE 
            cc.docstatus < 2
            {conditions}
        GROUP BY 
            cc.name
        ORDER BY 
            cc.start_date DESC
    """.format(conditions=conditions), as_dict=1)
    
    return data
