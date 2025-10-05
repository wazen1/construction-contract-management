from . import __version__ as app_version

app_name = "document_archiver"
app_title = "Document Archiver"
app_publisher = "Your Name"
app_description = "Document Archiving App with Scanner Integration"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "your.email@example.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/document_archiver/css/document_archiver.css"
# app_include_js = "/assets/document_archiver/js/document_archiver.js"

# include js, css files in header of web template
# web_include_css = "/assets/document_archiver/css/document_archiver.css"
# web_include_js = "/assets/document_archiver/js/document_archiver.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "document_archiver/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "document_archiver.install.before_install"
# after_install = "document_archiver.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "document_archiver.uninstall.before_uninstall"
# after_uninstall = "document_archiver.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "document_archiver.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"document_archiver.tasks.all"
#	],
#	"daily": [
#		"document_archiver.tasks.daily"
#	],
#	"hourly": [
#		"document_archiver.tasks.hourly"
#	],
#	"weekly": [
#		"document_archiver.tasks.weekly"
#	]
#	"monthly": [
#		"document_archiver.tasks.monthly"
#	]
# }

# Testing
# -------

# before_tests = "document_archiver.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "document_archiver.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "document_archiver.task.get_dashboard_data"
# }

# exempt linked doctypes from automatic linking
# auto_linked_doctypes = ["Task"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"document_archiver.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Translatable = ["DocType", "Custom Field", "Web Page"]