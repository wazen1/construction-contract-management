# Document Archiver - ERPNext App

A comprehensive document archiving solution for ERPNext with advanced scanner integration capabilities.

## Features

### 📄 Document Management
- **Document Archive**: Centralized storage for all types of documents
- **Categorization**: Organize documents by type, category, and tags
- **Search & Filter**: Full-text search with OCR capabilities
- **Version Control**: Track document changes and modifications

### 📷 Scanner Integration
- **Webcam Scanning**: Direct integration with webcam for document capture
- **SANE Scanner Support**: Linux-compatible scanner integration
- **TWAIN Support**: Windows scanner integration (requires additional setup)
- **Mobile App Support**: Upload scanned documents from mobile devices
- **File Upload**: Support for various file formats (PDF, PNG, JPG, TIFF)

### 🔍 OCR & Text Extraction
- **Automatic OCR**: Extract text from scanned documents using Tesseract
- **Multi-language Support**: Support for multiple languages
- **Quality Optimization**: Image preprocessing for better OCR accuracy
- **Searchable Content**: Make scanned documents searchable

### 📱 Mobile Integration
- **Mobile API**: RESTful API for mobile app integration
- **Image Processing**: Automatic image optimization and rotation
- **Offline Support**: Queue documents for upload when connection is available

## Installation

### Prerequisites

1. **ERPNext**: Version 13.0 or higher
2. **Python Dependencies**:
   ```bash
   pip install Pillow>=8.0.0
   pip install python-tesseract>=0.3.8
   pip install opencv-python>=4.5.0
   pip install numpy>=1.19.0
   pip install pdf2image>=1.16.0
   pip install pytesseract>=0.3.8
   ```

3. **System Dependencies** (for SANE scanner support):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install sane-utils tesseract-ocr
   
   # CentOS/RHEL
   sudo yum install sane-backends tesseract
   ```

### Install the App

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd document_archiver
   ```

2. **Install the app**:
   ```bash
   bench --site <site-name> install-app document_archiver
   ```

3. **Migrate the database**:
   ```bash
   bench --site <site-name> migrate
   ```

## Configuration

### Scanner Setup

1. **Configure Webcam**:
   - Go to Document Archiver > Scanner Config
   - Create a new configuration for webcam
   - Set scanner type to "Webcam"
   - Test the connection

2. **Configure SANE Scanner**:
   - Install SANE drivers for your scanner
   - Test scanner connection: `scanimage -L`
   - Create scanner configuration in ERPNext
   - Set device ID and other parameters

3. **Configure TWAIN Scanner** (Windows only):
   - Install TWAIN drivers for your scanner
   - Install python-twain library
   - Create scanner configuration

### OCR Configuration

1. **Install Tesseract**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr tesseract-ocr-eng
   
   # For additional languages
   sudo apt-get install tesseract-ocr-spa tesseract-ocr-fra
   ```

2. **Configure Tesseract Path**:
   - Update scanner configuration with Tesseract path
   - Default path: `/usr/bin/tesseract`

## Usage

### Basic Document Archiving

1. **Create Document Archive**:
   - Go to Document Archiver > Document Archive
   - Fill in document details (title, type, category)
   - Upload main document file

2. **Scan Documents**:
   - Open a Document Archive record
   - Click "Scan with Webcam" or "Scan with SANE"
   - Follow the scanning interface
   - Review and save scanned document

3. **Search Documents**:
   - Use the search functionality to find documents
   - Search by title, content, or OCR text
   - Filter by document type or category

### Advanced Features

1. **Batch Processing**:
   - Process multiple documents at once
   - Bulk OCR processing
   - Batch categorization

2. **API Integration**:
   - Use REST API for external integrations
   - Mobile app integration
   - Webhook support

3. **Custom Workflows**:
   - Create custom document workflows
   - Set up approval processes
   - Configure notifications

## API Reference

### Scanner API

#### Scan with Webcam
```http
POST /api/method/document_archiver.api.scanner.scan_with_webcam
Content-Type: application/json

{
    "document_archive_id": "DOC-2024-0001",
    "quality": "High"
}
```

#### Scan with SANE
```http
POST /api/method/document_archiver.api.scanner.scan_with_sane
Content-Type: application/json

{
    "document_archive_id": "DOC-2024-0001",
    "scanner_config_id": "SC-0001",
    "quality": "High"
}
```

#### Upload Scanned Document
```http
POST /api/method/document_archiver.api.scanner.upload_scanned_document
Content-Type: application/json

{
    "document_archive_id": "DOC-2024-0001",
    "file_data": "base64_encoded_file_data",
    "scanner_name": "Mobile Scanner",
    "quality": "High"
}
```

### Mobile API

#### Get Document List
```http
GET /api/method/document_archiver.api.mobile.get_document_archive_list
```

#### Create Document Archive
```http
POST /api/method/document_archiver.api.mobile.create_document_archive_from_mobile
Content-Type: application/json

{
    "title": "Invoice 001",
    "document_type": "Invoice",
    "file_data": "base64_encoded_file_data",
    "metadata": {
        "width": 1920,
        "height": 1080,
        "orientation": 1
    }
}
```

## Troubleshooting

### Common Issues

1. **Webcam not working**:
   - Check browser permissions
   - Ensure webcam is not used by another application
   - Try different browsers

2. **SANE scanner not detected**:
   - Check if scanner is connected and powered on
   - Run `scanimage -L` to list available scanners
   - Check SANE configuration files

3. **OCR not working**:
   - Verify Tesseract installation
   - Check Tesseract path in scanner configuration
   - Ensure language packs are installed

4. **Permission errors**:
   - Check file permissions in ERPNext
   - Ensure proper user roles are assigned
   - Verify API access permissions

### Debug Mode

Enable debug mode for detailed logging:

```python
# In site_config.json
{
    "developer_mode": 1,
    "log_level": "DEBUG"
}
```

## Development

### Project Structure

```
document_archiver/
├── document_archiver/
│   ├── api/
│   │   ├── scanner.py          # Scanner integration APIs
│   │   └── mobile.py           # Mobile app APIs
│   ├── doctype/
│   │   ├── document_archive/   # Main document doctype
│   │   ├── scanned_document/   # Scanned document child doctype
│   │   ├── scanner_config/     # Scanner configuration
│   │   └── document_category/  # Document categories
│   ├── install.py              # Installation hooks
│   └── hooks.py                # App hooks
├── public/
│   ├── js/
│   │   └── scanner_integration.js
│   └── css/
│       └── document_archiver.css
├── www/
│   └── scanner.html            # Web scanner interface
└── requirements.txt
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Testing

Run tests using ERPNext's testing framework:

```bash
bench --site <site-name> run-tests --app document_archiver
```

## License

This app is licensed under the MIT License. See LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation wiki

## Changelog

### Version 0.0.1
- Initial release
- Basic document archiving functionality
- Webcam and SANE scanner integration
- OCR text extraction
- Mobile API support
- Web interface for scanning