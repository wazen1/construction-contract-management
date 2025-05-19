# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class ProjectTender(Document):
    def autoname(self):
        # Custom naming series: TENDER-.YYYY.-
        self.name = make_autoname("TENDER-.YYYY.-")
    
    def validate(self):
        self.validate_mandatory_fields()
        self.calculate_total_boq_value()
    
    def validate_mandatory_fields(self):
        if not self.project_title:
            frappe.throw("Project Title is mandatory")
    
    def calculate_total_boq_value(self):
        """Calculate the total value from Bill of Quantities"""
        boq_list = frappe.get_all(
            "Bill of Quantities",
            filters={"parent_tender": self.name},
            fields=["SUM(total_amount) as total_value"]
        )
        
        if boq_list and boq_list[0].get("total_value"):
            self.total_boq_value = boq_list[0].get("total_value")
        else:
            self.total_boq_value = 0
