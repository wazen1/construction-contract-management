# Document Archiver Configuration

# OCR Configuration
TESSERACT_CONFIG = {
    'default_language': 'eng',
    'psm_mode': 6,  # Page segmentation mode
    'oem_mode': 3,  # OCR Engine mode
    'timeout': 30,  # Timeout in seconds
}

# Scanner Configuration
SCANNER_CONFIG = {
    'webcam': {
        'default_resolution': (640, 480),
        'max_resolution': (1920, 1080),
        'supported_formats': ['image/jpeg', 'image/png'],
    },
    'sane': {
        'default_dpi': 300,
        'max_dpi': 1200,
        'supported_formats': ['image/png', 'image/tiff'],
        'timeout': 60,
    },
    'twain': {
        'timeout': 60,
        'supported_formats': ['image/png', 'image/tiff', 'image/jpeg'],
    }
}

# File Processing Configuration
FILE_PROCESSING = {
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'supported_formats': ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'],
    'image_quality': 85,
    'max_image_dimension': 2048,
    'auto_rotate': True,
    'auto_crop': True,
    'auto_deskew': True,
}

# API Configuration
API_CONFIG = {
    'rate_limit': 100,  # requests per minute
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'timeout': 300,  # 5 minutes
    'allowed_origins': ['*'],  # Configure for production
}

# Mobile App Configuration
MOBILE_CONFIG = {
    'max_image_size': 2048,
    'compression_quality': 85,
    'supported_orientations': [1, 3, 6, 8],
    'auto_upload': False,
    'offline_support': True,
}

# Notification Configuration
NOTIFICATION_CONFIG = {
    'email_notifications': True,
    'scan_completion_notification': True,
    'error_notification': True,
    'batch_processing_notification': True,
}

# Security Configuration
SECURITY_CONFIG = {
    'encrypt_files': False,  # Set to True for production
    'file_access_control': True,
    'audit_logging': True,
    'api_key_required': False,  # Set to True for production
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    'enable_caching': True,
    'cache_ttl': 3600,  # 1 hour
    'batch_processing_size': 10,
    'parallel_processing': True,
    'max_workers': 4,
}

# Logging Configuration
LOGGING_CONFIG = {
    'log_level': 'INFO',
    'log_file': 'document_archiver.log',
    'max_log_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    'log_ocr_errors': True,
    'log_scanner_errors': True,
}