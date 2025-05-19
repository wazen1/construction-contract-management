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
            "fieldname": "contractor",
            "label": _("Contractor"),
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 200
        },
        {
            "fieldname": "total_contracts",
            "label": _("Total Contracts"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "completed_contracts",
            "label": _("Completed Contracts"),
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "active_contracts",
            "label": _("Active Contracts"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "total_value",
            "label": _("Total Contract Value"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "on_time_completion",
            "label": _("On-Time Completion (%)"),
            "fieldtype": "Percent",
            "width": 150
        },
        {
            "fieldname": "quality_score",
            "label": _("Quality Score"),
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "avg_delay",
            "label": _("Average Delay (Days)"),
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "cost_variance",
            "label": _("Cost Variance (%)"),
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "fieldname": "safety_incidents",
            "label": _("Safety Incidents"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "overall_rating",
            "label": _("Overall Rating"),
            "fieldtype": "Float",
            "width": 120
        }
    ]

def get_data(filters):
    conditions = ""
    if filters.get("contractor"):
        conditions += f" AND cc.contractor_reference = '{filters.get('contractor')}'"
    
    if filters.get("from_date"):
        conditions += f" AND cc.start_date >= '{filters.get('from_date')}'"
    
    if filters.get("to_date"):
        conditions += f" AND cc.end_date <= '{filters.get('to_date')}'"
    
    # Get basic contractor data
    contractors = frappe.db.sql("""
        SELECT 
            s.name as contractor,
            s.supplier_name as contractor_name,
            COUNT(cc.name) as total_contracts,
            SUM(CASE WHEN cc.end_date < CURDATE() THEN 1 ELSE 0 END) as completed_contracts,
            SUM(CASE WHEN cc.end_date >= CURDATE() THEN 1 ELSE 0 END) as active_contracts,
            SUM(cc.contract_value) as total_value
        FROM 
            `tabSupplier` s
        LEFT JOIN 
            `tabConstruction Contract` cc ON cc.contractor_reference = s.name
        WHERE 
            cc.docstatus = 1
            {conditions}
        GROUP BY 
            s.name
        ORDER BY 
            total_contracts DESC
    """.format(conditions=conditions), as_dict=1)
    
    # Enhance with performance metrics
    for contractor in contractors:
        # Get on-time completion percentage
        on_time = frappe.db.sql("""
            SELECT 
                COUNT(*) as count
            FROM 
                `tabConstruction Contract` cc
            WHERE 
                cc.contractor_reference = %s
                AND cc.end_date < CURDATE()
                AND (SELECT COUNT(*) FROM `tabContract Milestone` cm 
                     WHERE cm.parent = cc.name AND cm.status = 'Delayed') = 0
        """, contractor.contractor, as_dict=1)[0].count
        
        if contractor.completed_contracts:
            contractor.on_time_completion = (on_time / contractor.completed_contracts) * 100
        else:
            contractor.on_time_completion = 0
            
        # Get quality score (from custom evaluation doctype)
        quality_scores = frappe.db.sql("""
            SELECT 
                AVG(quality_score) as avg_score
            FROM 
                `tabContractor Evaluation`
            WHERE 
                contractor = %s
        """, contractor.contractor, as_dict=1)
        
        contractor.quality_score = flt(quality_scores[0].avg_score) if quality_scores and quality_scores[0].avg_score else 0
        
        # Get average delay
        delay_data = frappe.db.sql("""
            SELECT 
                AVG(DATEDIFF(actual_completion_date, cm.due_date)) as avg_delay
            FROM 
                `tabContract Milestone` cm
            JOIN 
                `tabConstruction Contract` cc ON cc.name = cm.parent
            WHERE 
                cc.contractor_reference = %s
                AND cm.status = 'Completed'
                AND actual_completion_date > cm.due_date
        """, contractor.contractor, as_dict=1)
        
        contractor.avg_delay = int(delay_data[0].avg_delay) if delay_data and delay_data[0].avg_delay else 0
        
        # Get cost variance
        cost_data = frappe.db.sql("""
            SELECT 
                AVG((final_amount - cc.contract_value) / cc.contract_value * 100) as avg_variance
            FROM 
                `tabConstruction Contract` cc
            WHERE 
                cc.contractor_reference = %s
                AND cc.end_date < CURDATE()
                AND final_amount IS NOT NULL
        """, contractor.contractor, as_dict=1)
        
        contractor.cost_variance = flt(cost_data[0].avg_variance) if cost_data and cost_data[0].avg_variance else 0
        
        # Get safety incidents
        safety_data = frappe.db.sql("""
            SELECT 
                COUNT(*) as incidents
            FROM 
                `tabSafety Incident`
            WHERE 
                contractor = %s
        """, contractor.contractor, as_dict=1)
        
        contractor.safety_incidents = safety_data[0].incidents if safety_data else 0
        
        # Calculate overall rating
        # Formula: (On-time % * 0.3) + (Quality * 0.3) + ((100 - Cost Variance) * 0.2) + ((10 - Safety Incidents) * 0.2)
        # Normalized to 0-5 scale
        on_time_factor = contractor.on_time_completion * 0.3
        quality_factor = (contractor.quality_score / 5) * 100 * 0.3
        cost_factor = (100 - abs(contractor.cost_variance)) * 0.2
        safety_factor = max(0, (10 - contractor.safety_incidents)) * 10 * 0.2
        
        overall_score = on_time_factor + quality_factor + cost_factor + safety_factor
        contractor.overall_rating = min(5, max(0, overall_score / 20))  # Convert to 0-5 scale
    
    return contractors

def get_chart(data):
    if not data:
        return None
        
    labels = [row.contractor_name for row in data]
    ratings = [row.overall_rating for row in data]
    
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Overall Rating",
                    "values": ratings
                }
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff"]
    }
