import os
import sys
import shutil
import frappe
from frappe.modules import get_module_path, get_app_modules

def check_app_structure():
    """Check if the app structure follows ERPNext v15 standards"""
    print("Checking app structure for ERPNext v15 compatibility...")
    
    app_name = "construction_contract_management"
    
    # Check if the app exists
    try:
        app_path = frappe.get_app_path(app_name)
        print(f"App found at: {app_path}")
    except Exception as e:
        print(f"Error finding app: {str(e)}")
        return False
    
    # Check for proper module structure
    module_name = "Construction Contract Management"
    module_path = os.path.join(app_path, app_name.replace("_", " ").title().replace(" ", ""))
    
    if not os.path.exists(module_path):
        print(f"Module path does not exist: {module_path}")
        print(f"Creating module path...")
        try:
            os.makedirs(module_path, exist_ok=True)
            # Create __init__.py
            with open(os.path.join(module_path, "__init__.py"), "w") as f:
                f.write("# -*- coding: utf-8 -*-\nfrom __future__ import unicode_literals\n")
            print(f"Created module path: {module_path}")
        except Exception as e:
            print(f"Error creating module path: {str(e)}")
            return False
    else:
        print(f"Module path exists: {module_path}")
    
    # Check for doctype directory
    doctype_path = os.path.join(module_path, "doctype")
    if not os.path.exists(doctype_path):
        print(f"Doctype path does not exist: {doctype_path}")
        print(f"Creating doctype path...")
        try:
            os.makedirs(doctype_path, exist_ok=True)
            # Create __init__.py
            with open(os.path.join(doctype_path, "__init__.py"), "w") as f:
                f.write("# -*- coding: utf-8 -*-\nfrom __future__ import unicode_literals\n")
            print(f"Created doctype path: {doctype_path}")
        except Exception as e:
            print(f"Error creating doctype path: {str(e)}")
            return False
    else:
        print(f"Doctype path exists: {doctype_path}")
    
    # Check for report directory
    report_path = os.path.join(module_path, "report")
    if not os.path.exists(report_path):
        print(f"Report path does not exist: {report_path}")
        print(f"Creating report path...")
        try:
            os.makedirs(report_path, exist_ok=True)
            # Create __init__.py
            with open(os.path.join(report_path, "__init__.py"), "w") as f:
                f.write("# -*- coding: utf-8 -*-\nfrom __future__ import unicode_literals\n")
            print(f"Created report path: {report_path}")
        except Exception as e:
            print(f"Error creating report path: {str(e)}")
            return False
    else:
        print(f"Report path exists: {report_path}")
    
    return True

def check_hooks_file():
    """Check if hooks.py has the correct paths for scheduler events"""
    print("Checking hooks.py file...")
    
    app_name = "construction_contract_management"
    hooks_path = os.path.join(frappe.get_app_path(app_name), "hooks.py")
    
    if not os.path.exists(hooks_path):
        print(f"hooks.py file not found at: {hooks_path}")
        return False
    
    with open(hooks_path, "r") as f:
        hooks_content = f.read()
    
    # Check for correct scheduler event paths
    correct_paths = [
        f"{app_name}.{app_name}.doctype.project_tender.project_tender.send_tender_deadline_reminders",
        f"{app_name}.{app_name}.doctype.construction_contract.construction_contract.check_milestone_status",
        f"{app_name}.{app_name}.doctype.construction_contract.construction_contract.send_weekly_progress_report",
        f"{app_name}.{app_name}.doctype.construction_contract.construction_contract.generate_monthly_performance_report"
    ]
    
    all_correct = True
    for path in correct_paths:
        if path not in hooks_content:
            print(f"Missing or incorrect path in hooks.py: {path}")
            all_correct = False
    
    if all_correct:
        print("hooks.py file has correct paths for scheduler events")
    
    return all_correct

def fix_module_references():
    """Fix module references in JSON files"""
    print("Fixing module references in JSON files...")
    
    app_name = "construction_contract_management"
    app_path = frappe.get_app_path(app_name)
    module_path = os.path.join(app_path, app_name)
    
    # Find all JSON files
    json_files = []
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    
    print(f"Found {len(json_files)} JSON files")
    
    # Check and fix module references
    for json_file in json_files:
        try:
            with open(json_file, "r") as f:
                content = f.read()
            
            # Replace "Project Tender" module with "Construction Contract Management"
            if '"module": "Project Tender"' in content:
                content = content.replace('"module": "Project Tender"', '"module": "Construction Contract Management"')
                
                with open(json_file, "w") as f:
                    f.write(content)
                
                print(f"Fixed module reference in: {json_file}")
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
    
    return True

def migrate_old_files():
    """Migrate files from old structure to new structure"""
    print("Checking for files in old structure...")
    
    app_name = "construction_contract_management"
    app_path = frappe.get_app_path(app_name)
    
    old_module_path = os.path.join(app_path, "project_tender")
    new_module_path = os.path.join(app_path, app_name)
    
    if os.path.exists(old_module_path):
        print(f"Found old module path: {old_module_path}")
        print(f"Migrating files to new structure...")
        
        try:
            # Copy doctype files
            old_doctype_path = os.path.join(old_module_path, "doctype")
            new_doctype_path = os.path.join(new_module_path, "doctype")
            
            if os.path.exists(old_doctype_path):
                os.makedirs(new_doctype_path, exist_ok=True)
                
                for item in os.listdir(old_doctype_path):
                    old_item_path = os.path.join(old_doctype_path, item)
                    new_item_path = os.path.join(new_doctype_path, item)
                    
                    if os.path.isdir(old_item_path) and not os.path.exists(new_item_path):
                        shutil.copytree(old_item_path, new_item_path)
                        print(f"Copied: {old_item_path} -> {new_item_path}")
            
            # Copy report files
            old_report_path = os.path.join(old_module_path, "report")
            new_report_path = os.path.join(new_module_path, "report")
            
            if os.path.exists(old_report_path):
                os.makedirs(new_report_path, exist_ok=True)
                
                for item in os.listdir(old_report_path):
                    old_item_path = os.path.join(old_report_path, item)
                    new_item_path = os.path.join(new_report_path, item)
                    
                    if os.path.isdir(old_item_path) and not os.path.exists(new_item_path):
                        shutil.copytree(old_item_path, new_item_path)
                        print(f"Copied: {old_item_path} -> {new_item_path}")
            
            # Copy workspace files
            old_workspace_path = os.path.join(old_module_path, "workspace")
            new_workspace_path = os.path.join(new_module_path, "workspace")
            
            if os.path.exists(old_workspace_path):
                os.makedirs(new_workspace_path, exist_ok=True)
                
                for item in os.listdir(old_workspace_path):
                    old_item_path = os.path.join(old_workspace_path, item)
                    new_item_path = os.path.join(new_workspace_path, item)
                    
                    if os.path.isdir(old_item_path) and not os.path.exists(new_item_path):
                        shutil.copytree(old_item_path, new_item_path)
                        print(f"Copied: {old_item_path} -> {new_item_path}")
            
            print("Migration of files completed")
            
            # Ask if user wants to remove old files
            response = input("Do you want to remove the old files? (y/n): ")
            if response.lower() == 'y':
                shutil.rmtree(old_module_path)
                print(f"Removed old module path: {old_module_path}")
            
        except Exception as e:
            print(f"Error migrating files: {str(e)}")
            return False
    else:
        print("No old module structure found, skipping migration")
    
    return True

def main():
    """Main function to fix migration issues for ERPNext v15"""
    print("Starting fix for ERPNext v15 migration...")
    
    # Initialize Frappe
    try:
        frappe.init(site="site1.local")
        frappe.connect()
        print("Successfully connected to Frappe")
    except Exception as e:
        print(f"Error connecting to Frappe: {str(e)}")
        return
    
    # Check app structure
    if not check_app_structure():
        print("App structure check failed")
        return
    
    # Check hooks file
    if not check_hooks_file():
        print("hooks.py check failed")
        print("Please update the hooks.py file with the correct paths")
    
    # Fix module references
    if not fix_module_references():
        print("Failed to fix module references")
        return
    
    # Migrate old files
    if not migrate_old_files():
        print("Failed to migrate old files")
        return
    
    print("\nFix completed. Please run 'bench migrate' to apply the changes.")
    print("If you encounter any issues, please check the logs for more information.")

if __name__ == "__main__":
    main()
