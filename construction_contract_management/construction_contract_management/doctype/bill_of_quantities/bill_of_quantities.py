# Copyright (c) 2023, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
import json

class BillofQuantities(Document):
    def autoname(self):
        self.name = make_autoname(f"BOQ-{self.project_tender}-.####")
    
    def validate(self):
        self.calculate_totals()
        self.validate_version()
    
    def calculate_totals(self):
        """Calculate total BoQ value from all items"""
        total = 0
        for item in self.items:
            item.total_amount = item.quantity * item.estimated_unit_rate
            total += item.total_amount
        
        self.total_boq_value = total
    
    def validate_version(self):
        """Ensure proper version control"""
        if not self.is_new():
            return
            
        existing_boqs = frappe.get_all(
            "Bill of Quantities",
            filters={"project_tender": self.project_tender},
            fields=["name", "version"]
        )
        
        if existing_boqs:
            max_version = max([boq.version for boq in existing_boqs])
            self.version = max_version + 1
        else:
            self.version = 1
    
    def on_update(self):
        """Update tender with latest BoQ information"""
        if self.is_latest_version:
            frappe.db.set_value("Project Tender", self.project_tender, "current_boq", self.name)
    
    def get_template(self):
        """Generate template for import/export"""
        template = {
            "headers": ["Item Code", "Description", "Quantity", "UOM", "Estimated Unit Rate"],
            "data": []
        }
        
        for item in self.items:
            template["data"].append([
                item.item_code,
                item.description,
                item.quantity,
                item.uom,
                item.estimated_unit_rate
            ])
        
        return json.dumps(template)
    
    def import_from_template(self, template_data):
        """Import data from template"""
        try:
            data = json.loads(template_data)
            self.items = []
            
            for row in data.get("data", []):
                if len(row) >= 5:
                    self.append("items", {
                        "item_code": row[0],
                        "description": row[1],
                        "quantity": float(row[2]),
                        "uom": row[3],
                        "estimated_unit_rate": float(row[4])
                    })
            
            self.calculate_totals()
            return True
        except Exception as e:
            frappe.throw(f"Error importing template: {str(e)}")
            return False
