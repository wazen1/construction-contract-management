import frappe
from frappe import _
import base64
import io
import os
import subprocess
import tempfile
from PIL import Image
import cv2
import numpy as np

@frappe.whitelist()
def scan_with_webcam(document_archive_id=None, quality="High"):
	"""Scan document using webcam"""
	try:
		import cv2
		
		# Initialize webcam
		cap = cv2.VideoCapture(0)
		if not cap.isOpened():
			return {"status": "error", "message": "Webcam not accessible"}
		
		# Capture image
		ret, frame = cap.read()
		cap.release()
		
		if not ret:
			return {"status": "error", "message": "Failed to capture image"}
		
		# Process image based on quality
		processed_frame = process_webcam_image(frame, quality)
		
		# Save image
		image_data = save_scanned_image(processed_frame, "webcam_scan")
		
		# Create scanned document record
		scanned_doc = create_scanned_document(
			document_archive_id=document_archive_id,
			scanner_name="Webcam",
			scanner_type="Webcam",
			file_data=image_data,
			scan_quality=quality
		)
		
		return {
			"status": "success",
			"message": "Document scanned successfully",
			"scanned_document_id": scanned_doc.name,
			"file_url": scanned_doc.file_attachment
		}
		
	except Exception as e:
		frappe.log_error(f"Error in webcam scanning: {str(e)}")
		return {"status": "error", "message": str(e)}

@frappe.whitelist()
def scan_with_sane(document_archive_id=None, scanner_config_id=None, quality="High"):
	"""Scan document using SANE"""
	try:
		# Get scanner configuration
		if scanner_config_id:
			config = frappe.get_doc("Scanner Config", scanner_config_id)
			device_id = config.device_id or "default"
			resolution = config.default_resolution or 300
		else:
			device_id = "default"
			resolution = 300
		
		# Create temporary file for scan
		with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
			temp_path = temp_file.name
		
		# Run scanimage command
		cmd = [
			'scanimage',
			'-d', device_id,
			'--resolution', str(resolution),
			'--format', 'png',
			'--output-file', temp_path
		]
		
		result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
		
		if result.returncode != 0:
			os.unlink(temp_path)
			return {"status": "error", "message": f"SANE scan failed: {result.stderr}"}
		
		# Read scanned image
		with open(temp_path, 'rb') as f:
			image_data = f.read()
		
		# Clean up temporary file
		os.unlink(temp_path)
		
		# Create scanned document record
		scanned_doc = create_scanned_document(
			document_archive_id=document_archive_id,
			scanner_name=f"SANE Scanner ({device_id})",
			scanner_type="SANE",
			file_data=image_data,
			scan_quality=quality,
			resolution=f"{resolution} DPI"
		)
		
		return {
			"status": "success",
			"message": "Document scanned successfully",
			"scanned_document_id": scanned_doc.name,
			"file_url": scanned_doc.file_attachment
		}
		
	except subprocess.TimeoutExpired:
		return {"status": "error", "message": "Scan operation timed out"}
	except FileNotFoundError:
		return {"status": "error", "message": "SANE tools not installed"}
	except Exception as e:
		frappe.log_error(f"Error in SANE scanning: {str(e)}")
		return {"status": "error", "message": str(e)}

@frappe.whitelist()
def scan_with_twain(document_archive_id=None, scanner_config_id=None, quality="High"):
	"""Scan document using TWAIN (Windows only)"""
	try:
		import platform
		if platform.system() != "Windows":
			return {"status": "error", "message": "TWAIN is only supported on Windows"}
		
		# This would require a TWAIN library like python-twain
		# For now, return a placeholder
		return {
			"status": "info",
			"message": "TWAIN integration requires additional setup",
			"note": "Install python-twain library and configure TWAIN drivers"
		}
		
	except Exception as e:
		frappe.log_error(f"Error in TWAIN scanning: {str(e)}")
		return {"status": "error", "message": str(e)}

@frappe.whitelist()
def upload_scanned_document(document_archive_id=None, file_data=None, scanner_name="File Upload", quality="High"):
	"""Upload a scanned document from mobile app or file upload"""
	try:
		if not file_data:
			return {"status": "error", "message": "No file data provided"}
		
		# Decode base64 file data
		if isinstance(file_data, str):
			file_data = base64.b64decode(file_data)
		
		# Create scanned document record
		scanned_doc = create_scanned_document(
			document_archive_id=document_archive_id,
			scanner_name=scanner_name,
			scanner_type="Mobile App",
			file_data=file_data,
			scan_quality=quality
		)
		
		return {
			"status": "success",
			"message": "Document uploaded successfully",
			"scanned_document_id": scanned_doc.name,
			"file_url": scanned_doc.file_attachment
		}
		
	except Exception as e:
		frappe.log_error(f"Error uploading scanned document: {str(e)}")
		return {"status": "error", "message": str(e)}

def process_webcam_image(frame, quality):
	"""Process webcam image for better quality"""
	try:
		# Convert BGR to RGB
		rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		
		# Apply image enhancement based on quality
		if quality == "Maximum":
			# Apply denoising
			rgb_frame = cv2.fastNlMeansDenoisingColored(rgb_frame, None, 10, 10, 7, 21)
			
			# Apply sharpening
			kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
			rgb_frame = cv2.filter2D(rgb_frame, -1, kernel)
		
		return rgb_frame
		
	except Exception as e:
		frappe.log_error(f"Error processing webcam image: {str(e)}")
		return frame

def save_scanned_image(image_data, filename_prefix):
	"""Save scanned image and return file data"""
	try:
		# Convert image to bytes
		if isinstance(image_data, np.ndarray):
			# Convert numpy array to PIL Image
			pil_image = Image.fromarray(image_data)
		else:
			pil_image = image_data
        
		# Convert to bytes
		img_buffer = io.BytesIO()
		pil_image.save(img_buffer, format='PNG')
		file_data = img_buffer.getvalue()
		
		return file_data
		
	except Exception as e:
		frappe.log_error(f"Error saving scanned image: {str(e)}")
		raise

def create_scanned_document(document_archive_id=None, scanner_name="Unknown", scanner_type="Unknown", 
						   file_data=None, scan_quality="High", resolution=None):
	"""Create a new Scanned Document record"""
	try:
		# Create file attachment
		file_doc = frappe.get_doc({
			"doctype": "File",
			"file_name": f"{scanner_name}_{frappe.utils.now()}.png",
			"content": file_data,
			"is_private": 0
		})
		file_doc.insert()
		
		# Create scanned document
		scanned_doc = frappe.get_doc({
			"doctype": "Scanned Document",
			"scanner_name": scanner_name,
			"scanner_type": scanner_type,
			"scan_date": frappe.utils.today(),
			"scan_time": frappe.utils.now_time(),
			"file_attachment": file_doc.file_url,
			"scan_quality": scan_quality,
			"resolution": resolution,
			"processing_status": "Pending"
		})
		
		scanned_doc.insert()
		
		# Link to document archive if provided
		if document_archive_id:
			archive_doc = frappe.get_doc("Document Archive", document_archive_id)
			archive_doc.append("scanned_documents", {
				"scanner_name": scanner_name,
				"scanner_type": scanner_type,
				"scan_date": frappe.utils.today(),
				"file_attachment": file_doc.file_url,
				"scan_quality": scan_quality,
				"resolution": resolution
			})
			archive_doc.save()
		
		return scanned_doc
		
	except Exception as e:
		frappe.log_error(f"Error creating scanned document: {str(e)}")
		raise

@frappe.whitelist()
def get_scanner_status():
	"""Get status of all configured scanners"""
	try:
		scanners = frappe.get_all("Scanner Config", 
								 filters={"is_active": 1},
								 fields=["name", "scanner_name", "scanner_type", "device_id"])
		
		status_list = []
		for scanner in scanners:
			status = test_scanner_connection(scanner.name)
			status_list.append({
				"scanner_name": scanner.scanner_name,
				"scanner_type": scanner.scanner_type,
				"device_id": scanner.device_id,
				"status": status.get("status", "unknown"),
				"message": status.get("message", "")
			})
		
		return {"status": "success", "scanners": status_list}
		
	except Exception as e:
		frappe.log_error(f"Error getting scanner status: {str(e)}")
		return {"status": "error", "message": str(e)}

def test_scanner_connection(scanner_config_id):
	"""Test connection to a specific scanner"""
	try:
		config = frappe.get_doc("Scanner Config", scanner_config_id)
		
		if config.scanner_type == "SANE":
			return test_sane_scanner(config)
		elif config.scanner_type == "Webcam":
			return test_webcam_scanner(config)
		elif config.scanner_type == "TWAIN":
			return test_twain_scanner(config)
		else:
			return {"status": "error", "message": "Unsupported scanner type"}
			
	except Exception as e:
		frappe.log_error(f"Error testing scanner connection: {str(e)}")
		return {"status": "error", "message": str(e)}

def test_sane_scanner(config):
	"""Test SANE scanner connection"""
	try:
		device_id = config.device_id or "default"
		result = subprocess.run(['scanimage', '-d', device_id, '--test'], 
							  capture_output=True, text=True, timeout=30)
		
		if result.returncode == 0:
			return {"status": "success", "message": "SANE scanner connection successful"}
		else:
			return {"status": "error", "message": f"SANE scanner test failed: {result.stderr}"}
	except Exception as e:
		return {"status": "error", "message": f"SANE test error: {str(e)}"}

def test_webcam_scanner(config):
	"""Test webcam connection"""
	try:
		import cv2
		cap = cv2.VideoCapture(0)
		if cap.isOpened():
			ret, frame = cap.read()
			cap.release()
			if ret:
				return {"status": "success", "message": "Webcam connection successful"}
			else:
				return {"status": "error", "message": "Webcam cannot capture frames"}
		else:
			return {"status": "error", "message": "Webcam not accessible"}
	except Exception as e:
		return {"status": "error", "message": f"Webcam test error: {str(e)}"}

def test_twain_scanner(config):
	"""Test TWAIN scanner connection"""
	return {"status": "info", "message": "TWAIN testing requires platform-specific implementation"}