#!/usr/bin/env python3
"""
Document Archiver - Usage Examples
This file contains examples of how to use the Document Archiver app programmatically.
"""

import frappe
from frappe import _

def create_document_archive_example():
    """Example: Create a new document archive"""
    
    # Create a new document archive
    archive = frappe.get_doc({
        "doctype": "Document Archive",
        "title": "Invoice #INV-2024-001",
        "document_type": "Invoice",
        "category": "Financial Documents",
        "description": "Monthly invoice for services rendered",
        "tags": "invoice, monthly, services",
        "status": "Draft"
    })
    
    archive.insert()
    print(f"Created document archive: {archive.name}")
    
    return archive

def scan_document_example():
    """Example: Scan a document using webcam"""
    
    # Get or create a document archive
    archive = create_document_archive_example()
    
    # Scan using webcam (this would be called from the web interface)
    result = frappe.call("document_archiver.api.scanner.scan_with_webcam", {
        "document_archive_id": archive.name,
        "quality": "High"
    })
    
    print(f"Scan result: {result}")
    return result

def upload_scanned_document_example():
    """Example: Upload a scanned document"""
    
    # Simulate file data (in real usage, this would come from file upload)
    import base64
    
    # Read a sample image file and encode it
    with open("sample_document.png", "rb") as f:
        file_data = base64.b64encode(f.read()).decode()
    
    # Upload the scanned document
    result = frappe.call("document_archiver.api.scanner.upload_scanned_document", {
        "document_archive_id": "DOC-2024-0001",
        "file_data": file_data,
        "scanner_name": "Example Scanner",
        "quality": "High"
    })
    
    print(f"Upload result: {result}")
    return result

def search_documents_example():
    """Example: Search documents by content"""
    
    # Search for documents containing specific text
    result = frappe.call("document_archiver.api.mobile.search_documents", {
        "query": "invoice",
        "limit": 10
    })
    
    print(f"Search results: {result}")
    return result

def get_scanner_status_example():
    """Example: Get status of all configured scanners"""
    
    result = frappe.call("document_archiver.api.scanner.get_scanner_status")
    
    print(f"Scanner status: {result}")
    return result

def configure_scanner_example():
    """Example: Configure a new scanner"""
    
    # Create a new scanner configuration
    scanner_config = frappe.get_doc({
        "doctype": "Scanner Config",
        "scanner_name": "Office Scanner",
        "scanner_type": "SANE",
        "is_active": 1,
        "device_id": "brother4:net1;dev0",
        "default_resolution": 300,
        "default_color_mode": "Color",
        "default_quality": "High",
        "auto_crop": 1,
        "auto_rotate": 1,
        "auto_deskew": 1,
        "language": "eng"
    })
    
    scanner_config.insert()
    print(f"Created scanner config: {scanner_config.name}")
    
    return scanner_config

def batch_process_documents_example():
    """Example: Batch process multiple documents"""
    
    # Get all pending scanned documents
    pending_docs = frappe.get_all("Scanned Document", 
                                 filters={"processing_status": "Pending"},
                                 fields=["name", "file_attachment"])
    
    print(f"Found {len(pending_docs)} pending documents")
    
    # Process each document
    for doc in pending_docs:
        try:
            # Reprocess the document
            result = frappe.call("document_archiver.doctype.scanned_document.scanned_document.reprocess_scanned_document", {
                "scanned_doc_id": doc.name
            })
            print(f"Processed {doc.name}: {result}")
        except Exception as e:
            print(f"Error processing {doc.name}: {e}")

def create_document_category_example():
    """Example: Create document categories"""
    
    categories = [
        "Financial Documents",
        "Legal Documents",
        "Technical Documents",
        "Personal Documents",
        "Business Documents"
    ]
    
    for category_name in categories:
        if not frappe.db.exists("Document Category", category_name):
            category = frappe.get_doc({
                "doctype": "Document Category",
                "category_name": category_name,
                "description": f"Category for {category_name.lower()}",
                "is_active": 1
            })
            category.insert()
            print(f"Created category: {category_name}")

def mobile_api_example():
    """Example: Mobile API usage"""
    
    # Get document list for mobile app
    documents = frappe.call("document_archiver.api.mobile.get_document_archive_list", {
        "filters": {"status": "Active"},
        "limit": 20,
        "offset": 0
    })
    
    print(f"Mobile API - Document list: {documents}")
    
    # Create document from mobile
    mobile_doc = frappe.call("document_archiver.api.mobile.create_document_archive_from_mobile", {
        "title": "Mobile Document",
        "document_type": "Other",
        "description": "Created from mobile app",
        "scanner_name": "Mobile Scanner",
        "quality": "High"
    })
    
    print(f"Mobile API - Created document: {mobile_doc}")

def webhook_example():
    """Example: Webhook integration"""
    
    # This would be called when a document is processed
    def on_document_processed(doc, method):
        """Webhook: Document processed"""
        print(f"Document {doc.name} has been processed")
        
        # Send notification
        frappe.publish_realtime("document_processed", {
            "document_id": doc.name,
            "status": doc.processing_status
        })
    
    # Register the webhook
    frappe.get_doc("Document Archive").on_update = on_document_processed

def main():
    """Run all examples"""
    
    print("Document Archiver - Usage Examples")
    print("=" * 40)
    
    try:
        # Initialize Frappe (this would be done automatically in ERPNext)
        frappe.init()
        frappe.connect()
        
        # Run examples
        print("\n1. Creating document archive...")
        create_document_archive_example()
        
        print("\n2. Configuring scanner...")
        configure_scanner_example()
        
        print("\n3. Creating document categories...")
        create_document_category_example()
        
        print("\n4. Getting scanner status...")
        get_scanner_status_example()
        
        print("\n5. Mobile API example...")
        mobile_api_example()
        
        print("\n6. Batch processing...")
        batch_process_documents_example()
        
        print("\nAll examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
    finally:
        frappe.destroy()

if __name__ == "__main__":
    main()