import frappe
from frappe.model.document import Document

class DocumentCategory(Document):
	def validate(self):
		self.validate_category_name()
	
	def validate_category_name(self):
		"""Validate that category name is unique"""
		if frappe.db.exists("Document Category", 
						   {"category_name": self.category_name, "name": ["!=", self.name]}):
			frappe.throw(f"Category '{self.category_name}' already exists")