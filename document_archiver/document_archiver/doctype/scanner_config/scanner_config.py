import frappe
from frappe.model.document import Document
from frappe import _
import json
import subprocess
import platform

class ScannerConfig(Document):
	def validate(self):
		self.validate_scanner_connection()
		self.set_default_values()
	
	def set_default_values(self):
		"""Set default values based on scanner type"""
		if not self.default_resolution:
			self.default_resolution = 300
		
		if not self.default_color_mode:
			self.default_color_mode = "Color"
		
		if not self.default_quality:
			self.default_quality = "High"
		
		if not self.language:
			self.language = "eng"
	
	def validate_scanner_connection(self):
		"""Validate scanner connection based on type"""
		if self.scanner_type == "TWAIN":
			self.validate_twain_connection()
		elif self.scanner_type == "SANE":
			self.validate_sane_connection()
		elif self.scanner_type == "Webcam":
			self.validate_webcam_connection()
	
	def validate_twain_connection(self):
		"""Validate TWAIN scanner connection"""
		try:
			# Check if TWAIN is available
			if platform.system() == "Windows":
				# Windows TWAIN validation
				pass
			else:
				frappe.throw(_("TWAIN is only supported on Windows"))
		except Exception as e:
			frappe.throw(_("TWAIN connection validation failed: {0}").format(str(e)))
	
	def validate_sane_connection(self):
		"""Validate SANE scanner connection"""
		try:
			# Check if SANE is installed and working
			result = subprocess.run(['scanimage', '--version'], 
								  capture_output=True, text=True, timeout=10)
			if result.returncode != 0:
				frappe.throw(_("SANE is not properly installed or configured"))
		except subprocess.TimeoutExpired:
			frappe.throw(_("SANE validation timed out"))
		except FileNotFoundError:
			frappe.throw(_("SANE (scanimage) not found. Please install SANE tools"))
		except Exception as e:
			frappe.throw(_("SANE connection validation failed: {0}").format(str(e)))
	
	def validate_webcam_connection(self):
		"""Validate webcam connection"""
		try:
			import cv2
			cap = cv2.VideoCapture(0)
			if not cap.isOpened():
				frappe.throw(_("No webcam found or webcam is being used by another application"))
			cap.release()
		except ImportError:
			frappe.throw(_("OpenCV not installed. Please install opencv-python"))
		except Exception as e:
			frappe.throw(_("Webcam validation failed: {0}").format(str(e)))

@frappe.whitelist()
def get_available_scanners():
	"""Get list of available scanners"""
	scanners = []
	
	# Check for SANE scanners
	try:
		result = subprocess.run(['scanimage', '-L'], 
							  capture_output=True, text=True, timeout=10)
		if result.returncode == 0:
			for line in result.stdout.split('\n'):
				if 'device' in line.lower():
					scanners.append({
						'type': 'SANE',
						'name': line.strip(),
						'description': 'SANE-compatible scanner'
					})
	except:
		pass
	
	# Check for webcam
	try:
		import cv2
		cap = cv2.VideoCapture(0)
		if cap.isOpened():
			scanners.append({
				'type': 'Webcam',
				'name': 'Default Webcam',
				'description': 'Built-in or USB webcam'
			})
		cap.release()
	except:
		pass
	
	return scanners

@frappe.whitelist()
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
	# TWAIN testing would require platform-specific implementation
	return {"status": "info", "message": "TWAIN testing requires platform-specific implementation"}