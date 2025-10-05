import frappe
from frappe.model.document import Document
from frappe import _
import os
from PIL import Image
import pytesseract
import cv2
import numpy as np

class DocumentArchive(Document):
	def validate(self):
		self.set_creation_date()
		self.set_modified_date()
		self.validate_file_attachment()
	
	def before_save(self):
		self.process_scanned_documents()
	
	def set_creation_date(self):
		if not self.created_date:
			self.created_date = frappe.utils.today()
	
	def set_modified_date(self):
		self.modified_date = frappe.utils.today()
	
	def validate_file_attachment(self):
		if self.file_attachment and not self.scanned_documents:
			# If there's a file attachment but no scanned documents, create one
			self.add_scanned_document_from_attachment()
	
	def add_scanned_document_from_attachment(self):
		"""Add a scanned document entry from the main file attachment"""
		if not self.scanned_documents:
			self.append("scanned_documents", {
				"scanner_name": "File Upload",
				"scan_date": frappe.utils.today(),
				"file_attachment": self.file_attachment,
				"scan_quality": "High",
				"notes": "Main document file"
			})
	
	def process_scanned_documents(self):
		"""Process all scanned documents for OCR and metadata extraction"""
		for doc in self.scanned_documents:
			if doc.file_attachment and not doc.ocr_text:
				doc.ocr_text = self.extract_text_from_file(doc.file_attachment)
				doc.file_size = self.get_file_size(doc.file_attachment)
				doc.file_type = self.get_file_type(doc.file_attachment)
	
	def extract_text_from_file(self, file_path):
		"""Extract text from uploaded file using OCR"""
		try:
			file_doc = frappe.get_doc("File", {"file_url": file_path})
			full_path = file_doc.get_full_path()
			
			# Check file type and process accordingly
			file_extension = os.path.splitext(full_path)[1].lower()
			
			if file_extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
				return self.extract_text_from_image(full_path)
			elif file_extension == '.pdf':
				return self.extract_text_from_pdf(full_path)
			else:
				return ""
		except Exception as e:
			frappe.log_error(f"Error extracting text from {file_path}: {str(e)}")
			return ""
	
	def extract_text_from_image(self, image_path):
		"""Extract text from image using OCR"""
		try:
			# Load image
			image = cv2.imread(image_path)
			
			# Preprocess image for better OCR
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			
			# Apply denoising
			denoised = cv2.fastNlMeansDenoising(gray)
			
			# Apply threshold
			_, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
			
			# Extract text using pytesseract
			text = pytesseract.image_to_string(thresh, config='--psm 6')
			
			return text.strip()
		except Exception as e:
			frappe.log_error(f"Error in OCR processing: {str(e)}")
			return ""
	
	def extract_text_from_pdf(self, pdf_path):
		"""Extract text from PDF"""
		try:
			from pdf2image import convert_from_path
			
			# Convert PDF to images
			images = convert_from_path(pdf_path)
			text = ""
			
			for image in images:
				# Convert PIL image to OpenCV format
				img_array = np.array(image)
				img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
				
				# Extract text
				page_text = pytesseract.image_to_string(img_cv, config='--psm 6')
				text += page_text + "\n"
			
			return text.strip()
		except Exception as e:
			frappe.log_error(f"Error extracting text from PDF: {str(e)}")
			return ""
	
	def get_file_size(self, file_path):
		"""Get file size in bytes"""
		try:
			file_doc = frappe.get_doc("File", {"file_url": file_path})
			full_path = file_doc.get_full_path()
			return os.path.getsize(full_path)
		except:
			return 0
	
	def get_file_type(self, file_path):
		"""Get file type from extension"""
		try:
			file_doc = frappe.get_doc("File", {"file_url": file_path})
			return os.path.splitext(file_doc.file_name)[1].lower()
		except:
			return ""

@frappe.whitelist()
def scan_document_with_scanner(document_archive_id, scanner_type="webcam"):
	"""API endpoint to scan document with various scanner types"""
	try:
		doc = frappe.get_doc("Document Archive", document_archive_id)
		
		if scanner_type == "webcam":
			return scan_with_webcam(doc)
		elif scanner_type == "twain":
			return scan_with_twain(doc)
		elif scanner_type == "sane":
			return scan_with_sane(doc)
		else:
			return {"error": "Unsupported scanner type"}
			
	except Exception as e:
		frappe.log_error(f"Error in scan_document_with_scanner: {str(e)}")
		return {"error": str(e)}

def scan_with_webcam(document_archive):
	"""Scan document using webcam"""
	# This would integrate with webcam scanning functionality
	# For now, return a placeholder
	return {
		"status": "success",
		"message": "Webcam scanning initiated",
		"scanner_type": "webcam"
	}

def scan_with_twain(document_archive):
	"""Scan document using TWAIN scanner"""
	# This would integrate with TWAIN-compatible scanners
	return {
		"status": "success", 
		"message": "TWAIN scanning initiated",
		"scanner_type": "twain"
	}

def scan_with_sane(document_archive):
	"""Scan document using SANE (Scanner Access Now Easy)"""
	# This would integrate with SANE-compatible scanners
	return {
		"status": "success",
		"message": "SANE scanning initiated", 
		"scanner_type": "sane"
	}