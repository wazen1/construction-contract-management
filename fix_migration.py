import os
import sys
import frappe
from frappe.modules import get_module_path, get_app_modules

def find_problematic_modules():
    """Find modules that might be causing the migration error"""
    print("Checking for problematic modules...")
    
    # Get all installed apps
    apps = frappe.get_installed_apps()
    problematic_modules = []
    
    for app in apps:
        try:
            # Get all modules for this app
            modules = get_app_modules(app)
            
            for module in modules:
                try:
                    # Try to get the module path
                    module_path = get_module_path(module, app)
                    if not os.path.exists(module_path):
                        problematic_modules.append((app, module, "Module path doesn't exist"))
                except Exception as e:
                    problematic_modules.append((app, module, str(e)))
        except Exception as e:
            problematic_modules.append((app, None, str(e)))
    
    return problematic_modules

def check_hooks_files():
    """Check hooks.py files for potential issues"""
    print("Checking hooks.py files...")
    
    apps = frappe.get_installed_apps()
    issues = []
    
    for app in apps:
        try:
            # Get the app path
            app_path = frappe.get_app_path(app)
            hooks_path = os.path.join(app_path, "hooks.py")
            
            if not os.path.exists(hooks_path):
                issues.append((app, "hooks.py file not found"))
                continue
                
            # Check if hooks.py has valid Python syntax
            with open(hooks_path, 'r') as f:
                hooks_content = f.read()
                
            try:
                compile(hooks_content, hooks_path, 'exec')
            except SyntaxError as e:
                issues.append((app, f"Syntax error in hooks.py: {str(e)}"))
                
        except Exception as e:
            issues.append((app, str(e)))
    
    return issues

def fix_construction_contract_management():
    """Fix specific issues in the construction_contract_management app"""
    print("Attempting to fix construction_contract_management app...")
    
    try:
        # Check if the app exists
        app_path = frappe.get_app_path("construction_contract_management")
        
        # Check if the app has the proper structure
        project_tender_path = os.path.join(app_path, "project_tender")
        if not os.path.exists(project_tender_path):
            os.makedirs(project_tender_path)
            print(f"Created missing directory: {project_tender_path}")
        
        # Create an __init__.py file if it doesn't exist
        init_file = os.path.join(project_tender_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write("# -*- coding: utf-8 -*-\n")
            print(f"Created missing __init__.py file: {init_file}")
        
        # Check hooks.py for proper module references
        hooks_path = os.path.join(app_path, "hooks.py")
        if os.path.exists(hooks_path):
            with open(hooks_path, 'r') as f:
                hooks_content = f.read()
            
            # Make sure fixtures are properly formatted
            if "fixtures = [" in hooks_content and "]" in hooks_content:
                print("hooks.py file looks properly formatted")
            else:
                print("WARNING: hooks.py might have incorrect fixtures format")
        
        return True
    except Exception as e:
        print(f"Error fixing construction_contract_management: {str(e)}")
        return False

def main():
    """Main function to diagnose and fix migration issues"""
    print("Starting diagnosis of migration error...")
    
    # Initialize Frappe
    try:
        frappe.init(site="site1.local")
        frappe.connect()
        print("Successfully connected to Frappe")
    except Exception as e:
        print(f"Error connecting to Frappe: {str(e)}")
        return
    
    # Find problematic modules
    problematic_modules = find_problematic_modules()
    if problematic_modules:
        print("\nProblematic modules found:")
        for app, module, error in problematic_modules:
            print(f"  - App: {app}, Module: {module}, Error: {error}")
    else:
        print("\nNo problematic modules found")
    
    # Check hooks.py files
    hooks_issues = check_hooks_files()
    if hooks_issues:
        print("\nIssues found in hooks.py files:")
        for app, error in hooks_issues:
            print(f"  - App: {app}, Error: {error}")
    else:
        print("\nNo issues found in hooks.py files")
    
    # Try to fix construction_contract_management app
    if "construction_contract_management" in frappe.get_installed_apps():
        if fix_construction_contract_management():
            print("\nFixed issues in construction_contract_management app")
        else:
            print("\nCould not fix all issues in construction_contract_management app")
    
    print("\nDiagnosis complete. Please check the issues reported above.")
    print("After fixing the issues, try running 'bench migrate' again.")

if __name__ == "__main__":
    main()
