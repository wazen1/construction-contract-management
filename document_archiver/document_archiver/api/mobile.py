import frappe
from frappe import _
import base64
import io
from PIL import Image
import json

@frappe.whitelist()
def mobile_scan_document(document_data):
	"""API endpoint for mobile app to scan and upload documents"""
	try:
		# Parse document data
		if isinstance(document_data, str):
			document_data = json.loads(document_data)
		
		# Extract data
		document_archive_id = document_data.get('document_archive_id')
		file_data = document_data.get('file_data')
		scanner_name = document_data.get('scanner_name', 'Mobile Scanner')
		quality = document_data.get('quality', 'High')
		metadata = document_data.get('metadata', {})
		
		if not file_data:
			return {"status": "error", "message": "No file data provided"}
		
		# Decode base64 file data
		file_bytes = base64.b64decode(file_data)
		
		# Process image if needed
		processed_file_data = process_mobile_image(file_bytes, metadata)
		
		# Create scanned document
		scanned_doc = create_mobile_scanned_document(
			document_archive_id=document_archive_id,
			scanner_name=scanner_name,
			file_data=processed_file_data,
			quality=quality,
			metadata=metadata
		)
		
		return {
			"status": "success",
			"message": "Document scanned and uploaded successfully",
			"scanned_document_id": scanned_doc.name,
			"file_url": scanned_doc.file_attachment
		}
		
	except Exception as e:
		frappe.log_error(f"Error in mobile scan: {str(e)}")
		return {"status": "error", "message": str(e)}

@frappe.whitelist()
def get_document_archive_list(filters=None, limit=20, offset=0):
	"""Get list of document archives for mobile app"""
	try:
		if filters:
			if isinstance(filters, str):
				filters = json.loads(filters)
		else:
			filters = {}
		
		# Add default filters
		filters['status'] = ['!=', 'Deleted']
		
		archives = frappe.get_all("Document Archive",
								filters=filters,
								fields=["name", "title", "document_type", "status", 
									   "created_date", "modified_date", "file_attachment"],
								limit=limit,
								start=offset,
								order_by="modified_date desc")
		
		# Get scanned documents count for each archive
		for archive in archives:
			scanned_count = frappe.db.count("Scanned Document", 
										  {"parent": archive.name})
			archive['scanned_documents_count'] = scanned_count
		
		return {
			"status": "success",
			"archives": archives,
			"total": len(archives)
		}
		
	except Exception as e:
		frappe.log_error(f"Error getting document archive list: {str(e)}")
		return {"status": "error", "message": str(e)}

@frappe.whitelist()
def get_document_archive_details(archive_id):
	"""Get detailed information about a document archive"""
	try:
		archive = frappe.get_doc("Document Archive", archive_id)
		
		# Get scanned documents
		scanned_docs = frappe.get_all("Scanned Document",
									filters={"parent": archive_id},
									fields=["name", "scanner_name", "scanner_type", 
										   "scan_date", "scan_quality", "file_attachment",
										   "processing_status", "file_size", "file_type"])
		
		return {
			"status": "success",
			"archive": {
				"name": archive.name,
				"title": archive.title,
				"document_type": archive.document_type,
				"category": archive.category,
				"description": archive.description,
				"tags": archive.tags,
				"status": archive.status,
				"created_date": archive.created_date,
				"modified_date": archive.modified_date,
				"file_attachment": archive.file_attachment
			},
			"scanned_documents": scanned_docs
		}
		
	except Exception as e:
		frappe.log_error(f"Error getting document archive details: {str(e)}")
		return {"status": "error", "message": str(e)}

@frappe.whitelist()
def create_document_archive_from_mobile(archive_data):
	"""Create a new document archive from mobile app"""
	try:
		if isinstance(archive_data, str):
			archive_data = json.loads(archive_data)
		
		# Create document archive
		archive = frappe.get_doc({
			"doctype": "Document Archive",
			"title": archive_data.get('title', 'Mobile Document'),
			"document_type": archive_data.get('document_type', 'Other'),
			"category": archive_data.get('category'),
			"description": archive_data.get('description'),
			"tags": archive_data.get('tags'),
			"status": "Draft"
		})
		
		archive.insert()
		
		# If file data is provided, add scanned document
		if archive_data.get('file_data'):
			file_data = base64.b64decode(archive_data['file_data'])
			metadata = archive_data.get('metadata', {})
			
			processed_file_data = process_mobile_image(file_data, metadata)
			
			create_mobile_scanned_document(
				document_archive_id=archive.name,
				scanner_name=archive_data.get('scanner_name', 'Mobile Scanner'),
				file_data=processed_file_data,
				quality=archive_data.get('quality', 'High'),
				metadata=metadata
			)
		
		return {
			"status": "success",
			"message": "Document archive created successfully",
			"archive_id": archive.name
		}
		
	except Exception as e:
		frappe.log_error(f"Error creating document archive from mobile: {str(e)}")
		return {"status": "error", "message": str(e)}

def process_mobile_image(file_data, metadata):
	"""Process image from mobile app for better quality"""
	try:
		# Open image
		image = Image.open(io.BytesIO(file_data))
		
		# Get metadata
		orientation = metadata.get('orientation', 1)
		quality = metadata.get('quality', 85)
		
		# Handle orientation
		if orientation in [3, 6, 8]:
			# Rotate image based on EXIF orientation
			rotation_map = {3: 180, 6: 270, 8: 90}
			image = image.rotate(rotation_map[orientation], expand=True)
		
		# Resize if too large (max 2048px on longest side)
		max_size = 2048
		if max(image.size) > max_size:
			ratio = max_size / max(image.size)
			new_size = tuple(int(dim * ratio) for dim in image.size)
			image = image.resize(new_size, Image.Resampling.LANCZOS)
		
		# Convert to RGB if necessary
		if image.mode != 'RGB':
			image = image.convert('RGB')
		
		# Save with appropriate quality
		output = io.BytesIO()
		image.save(output, format='JPEG', quality=quality, optimize=True)
		
		return output.getvalue()
		
	except Exception as e:
		frappe.log_error(f"Error processing mobile image: {str(e)}")
		return file_data  # Return original if processing fails

def create_mobile_scanned_document(document_archive_id, scanner_name, file_data, quality, metadata):
	"""Create scanned document from mobile upload"""
	try:
		# Create file attachment
		file_doc = frappe.get_doc({
			"doctype": "File",
			"file_name": f"{scanner_name}_{frappe.utils.now()}.jpg",
			"content": file_data,
			"is_private": 0
		})
		file_doc.insert()
		
		# Create scanned document
		scanned_doc = frappe.get_doc({
			"doctype": "Scanned Document",
			"scanner_name": scanner_name,
			"scanner_type": "Mobile App",
			"scan_date": frappe.utils.today(),
			"scan_time": frappe.utils.now_time(),
			"file_attachment": file_doc.file_url,
			"scan_quality": quality,
			"resolution": f"{metadata.get('width', 0)}x{metadata.get('height', 0)}",
			"color_mode": "Color",
			"processing_status": "Pending"
		})
		
		scanned_doc.insert()
		
		# Link to document archive
		if document_archive_id:
			archive_doc = frappe.get_doc("Document Archive", document_archive_id)
			archive_doc.append("scanned_documents", {
				"scanner_name": scanner_name,
				"scanner_type": "Mobile App",
				"scan_date": frappe.utils.today(),
				"file_attachment": file_doc.file_url,
				"scan_quality": quality,
				"resolution": f"{metadata.get('width', 0)}x{metadata.get('height', 0)}"
			})
			archive_doc.save()
		
		return scanned_doc
		
	except Exception as e:
		frappe.log_error(f"Error creating mobile scanned document: {str(e)}")
		raise

@frappe.whitelist()
def search_documents(query, limit=20):
	"""Search documents by text content (OCR)"""
	try:
		# Search in OCR text
		scanned_docs = frappe.db.sql("""
			SELECT sd.name, sd.parent, sd.ocr_text, da.title, da.document_type
			FROM `tabScanned Document` sd
			JOIN `tabDocument Archive` da ON sd.parent = da.name
			WHERE sd.ocr_text LIKE %s
			AND da.status != 'Deleted'
			ORDER BY sd.modified DESC
			LIMIT %s
		""", (f"%{query}%", limit), as_dict=True)
		
		# Search in document titles and descriptions
		archives = frappe.get_all("Document Archive",
								filters=[
									["title", "like", f"%{query}%"],
									["status", "!=", "Deleted"]
								],
								fields=["name", "title", "document_type", "description"],
								limit=limit)
		
		return {
			"status": "success",
			"scanned_documents": scanned_docs,
			"archives": archives
		}
		
	except Exception as e:
		frappe.log_error(f"Error searching documents: {str(e)}")
		return {"status": "error", "message": str(e)}