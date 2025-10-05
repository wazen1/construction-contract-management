import frappe
from frappe import _

def after_install():
	"""Called after app installation"""
	setup_default_scanner_configs()
	create_document_categories()
	setup_permissions()

def setup_default_scanner_configs():
	"""Create default scanner configurations"""
	try:
		# Webcam configuration
		if not frappe.db.exists("Scanner Config", "Default Webcam"):
			webcam_config = frappe.get_doc({
				"doctype": "Scanner Config",
				"scanner_name": "Default Webcam",
				"scanner_type": "Webcam",
				"is_active": 1,
				"default_resolution": 300,
				"default_color_mode": "Color",
				"default_quality": "High",
				"auto_crop": 1,
				"auto_rotate": 1,
				"auto_deskew": 1,
				"language": "eng"
			})
			webcam_config.insert()
		
		# SANE configuration
		if not frappe.db.exists("Scanner Config", "Default SANE"):
			sane_config = frappe.get_doc({
				"doctype": "Scanner Config",
				"scanner_name": "Default SANE Scanner",
				"scanner_type": "SANE",
				"is_active": 1,
				"device_id": "default",
				"default_resolution": 300,
				"default_color_mode": "Color",
				"default_quality": "High",
				"auto_crop": 1,
				"auto_rotate": 1,
				"auto_deskew": 1,
				"language": "eng"
			})
			sane_config.insert()
		
		frappe.db.commit()
		
	except Exception as e:
		frappe.log_error(f"Error setting up default scanner configs: {str(e)}")

def create_document_categories():
	"""Create default document categories"""
	categories = [
		"Financial Documents",
		"Legal Documents", 
		"Technical Documents",
		"Personal Documents",
		"Business Documents",
		"Medical Documents",
		"Educational Documents",
		"Other"
	]
	
	for category in categories:
		if not frappe.db.exists("Document Category", category):
			try:
				category_doc = frappe.get_doc({
					"doctype": "Document Category",
					"category_name": category,
					"description": f"Category for {category.lower()}"
				})
				category_doc.insert()
			except Exception as e:
				frappe.log_error(f"Error creating category {category}: {str(e)}")

def setup_permissions():
	"""Setup default permissions for the app"""
	try:
		# Create Document Manager role if it doesn't exist
		if not frappe.db.exists("Role", "Document Manager"):
			role = frappe.get_doc({
				"doctype": "Role",
				"role_name": "Document Manager",
				"desk_access": 1,
				"is_custom": 1
			})
			role.insert()
		
		# Create Document Permission doctype if it doesn't exist
		if not frappe.db.exists("DocType", "Document Permission"):
			permission_doc = frappe.get_doc({
				"doctype": "DocType",
				"name": "Document Permission",
				"module": "Document Archiver",
				"is_child_table": 1,
				"fields": [
					{
						"fieldname": "user",
						"fieldtype": "Link",
						"options": "User",
						"label": "User"
					},
					{
						"fieldname": "permission_type",
						"fieldtype": "Select",
						"options": "Read\nWrite\nDelete",
						"label": "Permission Type"
					}
				]
			})
			permission_doc.insert()
		
		frappe.db.commit()
		
	except Exception as e:
		frappe.log_error(f"Error setting up permissions: {str(e)}")

def before_uninstall():
	"""Called before app uninstallation"""
	cleanup_data()

def cleanup_data():
	"""Clean up app data before uninstallation"""
	try:
		# Delete scanner configs
		frappe.db.sql("DELETE FROM `tabScanner Config`")
		
		# Delete document archives
		frappe.db.sql("DELETE FROM `tabDocument Archive`")
		
		# Delete scanned documents
		frappe.db.sql("DELETE FROM `tabScanned Document`")
		
		# Delete document categories
		frappe.db.sql("DELETE FROM `tabDocument Category`")
		
		frappe.db.commit()
		
	except Exception as e:
		frappe.log_error(f"Error cleaning up data: {str(e)}")