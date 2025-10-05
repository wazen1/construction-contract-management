import frappe
from frappe.model.document import Document
from frappe import _
import os
from PIL import Image
import pytesseract
import cv2
import numpy as np

class ScannedDocument(Document):
	def validate(self):
		self.set_scan_time()
		self.process_file()
	
	def set_scan_time(self):
		if not self.scan_time:
			self.scan_time = frappe.utils.now_time()
	
	def process_file(self):
		"""Process the scanned file for metadata and OCR"""
		if self.file_attachment:
			self.extract_file_metadata()
			if not self.ocr_text:
				self.extract_ocr_text()
	
	def extract_file_metadata(self):
		"""Extract file metadata like size and type"""
		try:
			file_doc = frappe.get_doc("File", {"file_url": self.file_attachment})
			full_path = file_doc.get_full_path()
			
			# Get file size
			self.file_size = os.path.getsize(full_path)
			
			# Get file type
			self.file_type = os.path.splitext(file_doc.file_name)[1].lower()
			
		except Exception as e:
			frappe.log_error(f"Error extracting file metadata: {str(e)}")
	
	def extract_ocr_text(self):
		"""Extract text from scanned document using OCR"""
		try:
			file_doc = frappe.get_doc("File", {"file_url": self.file_attachment})
			full_path = file_doc.get_full_path()
			
			# Check file type and process accordingly
			file_extension = os.path.splitext(full_path)[1].lower()
			
			if file_extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
				self.ocr_text = self.extract_text_from_image(full_path)
			elif file_extension == '.pdf':
				self.ocr_text = self.extract_text_from_pdf(full_path)
			
			self.processing_status = "Completed"
			
		except Exception as e:
			frappe.log_error(f"Error in OCR processing: {str(e)}")
			self.processing_status = "Failed"
	
	def extract_text_from_image(self, image_path):
		"""Extract text from image using OCR"""
		try:
			# Load image
			image = cv2.imread(image_path)
			
			# Preprocess image for better OCR
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			
			# Apply denoising
			denoised = cv2.fastNlMeansDenoising(gray)
			
			# Apply threshold based on scan quality
			if self.scan_quality == "Draft":
				_, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
			else:
				# More sophisticated preprocessing for higher quality
				thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
			
			# Extract text using pytesseract
			config = '--psm 6'
			if self.scan_quality == "Maximum":
				config += ' -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?@#$%^&*()_+-=[]{}|;:,.<>?/~` '
			
			text = pytesseract.image_to_string(thresh, config=config)
			
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

@frappe.whitelist()
def reprocess_scanned_document(scanned_doc_id):
	"""Reprocess a scanned document for OCR"""
	try:
		doc = frappe.get_doc("Scanned Document", scanned_doc_id)
		doc.processing_status = "Processing"
		doc.save()
		
		# Force reprocessing
		doc.extract_ocr_text()
		doc.save()
		
		return {"status": "success", "message": "Document reprocessed successfully"}
		
	except Exception as e:
		frappe.log_error(f"Error reprocessing scanned document: {str(e)}")
		return {"status": "error", "message": str(e)}