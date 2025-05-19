frappe.whitelist = True

# Copyright (c) 2023, Manus and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class ProjectTender(Document):
    def autoname(self):
        # Set the naming series as per requirements
        self.name = make_autoname("TENDER-.YYYY.-")
    
    def validate(self):
        # Validate mandatory fields
        if not self.project_title:
            frappe.throw("Project Title is mandatory")
        
        # Additional validations can be added here
    
    def before_save(self):
        # Any processing before saving
        pass
    
    def on_submit(self):
        # Actions to take on submission
        pass
