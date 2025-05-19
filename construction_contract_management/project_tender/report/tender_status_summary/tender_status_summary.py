# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}
        
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data, None, None, None

def get_columns():
    return [
        {
            "fieldname": "tender_id",
            "label": _("Tender ID"),
            "fieldtype": "Link",
            "options": "Project Tender",
            "width": 120
        },
        {
            "fieldname": "project_title",
            "label": _("Project Title"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "submission_deadline",
            "label": _("Submission Deadline"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "initial_budget",
            "label": _("Initial Budget"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "bid_count",
            "label": _("Bids Received"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "lowest_bid",
            "label": _("Lowest Bid"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "highest_bid",
            "label": _("Highest Bid"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "days_remaining",
            "label": _("Days Remaining"),
            "fieldtype": "Int",
            "width": 120
        }
    ]

def get_data(filters):
    conditions = ""
    if filters.get("status"):
        conditions += f" AND pt.status = '{filters.get('status')}'"
    
    if filters.get("from_date"):
        conditions += f" AND pt.submission_deadline >= '{filters.get('from_date')}'"
    
    if filters.get("to_date"):
        conditions += f" AND pt.submission_deadline <= '{filters.get('to_date')}'"
    
    data = frappe.db.sql("""
        SELECT 
            pt.name as tender_id,
            pt.project_title,
            pt.status,
            pt.submission_deadline,
            pt.initial_budget_amount as initial_budget,
            COUNT(cb.name) as bid_count,
            MIN(cb.bid_amount) as lowest_bid,
            MAX(cb.bid_amount) as highest_bid,
            DATEDIFF(pt.submission_deadline, CURDATE()) as days_remaining
        FROM 
            `tabProject Tender` pt
        LEFT JOIN 
            `tabContractor Bid` cb ON cb.tender_reference = pt.name
        WHERE 
            pt.docstatus = 1
            {conditions}
        GROUP BY 
            pt.name
        ORDER BY 
            pt.submission_deadline DESC
    """.format(conditions=conditions), as_dict=1)
    
    return data
