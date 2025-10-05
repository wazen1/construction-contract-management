# Document Archiver - Installation Guide

## Quick Start

### 1. Prerequisites

- ERPNext version 13.0 or higher
- Python 3.7+
- Linux/Unix system (for SANE scanner support)
- Webcam or scanner device

### 2. Install Dependencies

Run the dependency installation script:

```bash
cd document_archiver
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### 3. Install the App

```bash
# In your ERPNext bench directory
bench get-app document_archiver /path/to/document_archiver
bench --site <site-name> install-app document_archiver
bench --site <site-name> migrate
```

### 4. Configure Scanners

1. Go to **Document Archiver > Scanner Config**
2. Create configurations for your scanners:
   - **Webcam**: Set type to "Webcam"
   - **SANE Scanner**: Set type to "SANE" and device ID
   - **TWAIN Scanner**: Set type to "TWAIN" (Windows only)

### 5. Test Installation

1. Go to **Document Archiver > Document Archive**
2. Create a new document
3. Try scanning with webcam or uploading a file
4. Verify OCR text extraction works

## Detailed Installation

### System Requirements

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    sane-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libopencv-dev \
    python3-opencv
```

#### CentOS/RHEL/Fedora
```bash
# For CentOS/RHEL
sudo yum install -y \
    sane-backends \
    tesseract \
    tesseract-langpack-eng \
    poppler-utils \
    opencv-devel

# For Fedora
sudo dnf install -y \
    sane-backends \
    tesseract \
    tesseract-langpack-eng \
    poppler-utils \
    opencv-devel
```

#### Arch Linux
```bash
sudo pacman -S --noconfirm \
    sane \
    tesseract \
    tesseract-data-eng \
    poppler \
    opencv
```

### Python Dependencies

```bash
pip install Pillow>=8.0.0
pip install python-tesseract>=0.3.8
pip install opencv-python>=4.5.0
pip install numpy>=1.19.0
pip install pdf2image>=1.16.0
pip install pytesseract>=0.3.8
```

### ERPNext Installation

1. **Get the app**:
   ```bash
   bench get-app document_archiver https://github.com/your-repo/document_archiver
   ```

2. **Install on site**:
   ```bash
   bench --site <site-name> install-app document_archiver
   ```

3. **Migrate database**:
   ```bash
   bench --site <site-name> migrate
   ```

4. **Restart services**:
   ```bash
   bench restart
   ```

## Configuration

### Scanner Configuration

#### Webcam Setup
1. Go to **Document Archiver > Scanner Config**
2. Create new configuration:
   - **Scanner Name**: "Default Webcam"
   - **Scanner Type**: "Webcam"
   - **Is Active**: ✓
   - **Default Resolution**: 300 DPI
   - **Default Quality**: "High"

#### SANE Scanner Setup
1. Test scanner detection:
   ```bash
   scanimage -L
   ```

2. Create scanner configuration:
   - **Scanner Name**: "Office Scanner"
   - **Scanner Type**: "SANE"
   - **Device ID**: (from scanimage -L output)
   - **Is Active**: ✓
   - **Default Resolution**: 300 DPI

#### TWAIN Scanner Setup (Windows)
1. Install TWAIN drivers for your scanner
2. Install python-twain:
   ```bash
   pip install python-twain
   ```

3. Create scanner configuration:
   - **Scanner Name**: "TWAIN Scanner"
   - **Scanner Type**: "TWAIN"
   - **Is Active**: ✓

### OCR Configuration

1. **Install Tesseract**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr tesseract-ocr-eng
   
   # Additional languages
   sudo apt-get install tesseract-ocr-spa tesseract-ocr-fra
   ```

2. **Configure Tesseract path** in scanner settings:
   - **Tesseract Path**: `/usr/bin/tesseract`
   - **Language**: `eng` (or your preferred language)

### File Storage Configuration

1. **Set file upload limits** in `site_config.json`:
   ```json
   {
       "max_file_size": 52428800,
       "file_upload_path": "/path/to/files"
   }
   ```

2. **Configure file permissions**:
   ```bash
   chmod 755 /path/to/files
   chown frappe:frappe /path/to/files
   ```

## Testing

### Test Scanner Connection

1. Go to **Document Archiver > Scanner Config**
2. Select your scanner configuration
3. Click "Test Connection"
4. Verify status shows "Success"

### Test Document Scanning

1. Go to **Document Archiver > Document Archive**
2. Create new document
3. Click "Scan with Webcam" or "Scan with SANE"
4. Verify document is scanned and OCR text is extracted

### Test Mobile API

```bash
# Test mobile API endpoint
curl -X GET "http://your-site/api/method/document_archiver.api.mobile.get_document_archive_list"
```

## Troubleshooting

### Common Issues

#### Webcam Not Working
- Check browser permissions for camera access
- Ensure webcam is not used by another application
- Try different browsers (Chrome, Firefox, Safari)

#### SANE Scanner Not Detected
- Check scanner is connected and powered on
- Run `scanimage -L` to list available scanners
- Check SANE configuration in `/etc/sane.d/`
- Add scanner to `/etc/sane.d/dll.conf`

#### OCR Not Working
- Verify Tesseract installation: `tesseract --version`
- Check Tesseract path in scanner configuration
- Ensure language packs are installed
- Check file permissions

#### Permission Errors
- Check ERPNext user roles and permissions
- Verify file system permissions
- Check API access permissions

### Debug Mode

Enable debug logging:

```python
# In site_config.json
{
    "developer_mode": 1,
    "log_level": "DEBUG",
    "log_file": "document_archiver.log"
}
```

### Log Files

Check log files for errors:
- ERPNext logs: `logs/error.log`
- App logs: `logs/document_archiver.log`
- System logs: `/var/log/syslog`

## Performance Optimization

### Server Configuration

1. **Increase file upload limits**:
   ```nginx
   client_max_body_size 50M;
   ```

2. **Configure PHP limits** (if using PHP):
   ```ini
   upload_max_filesize = 50M
   post_max_size = 50M
   max_execution_time = 300
   ```

3. **Optimize database**:
   ```sql
   ALTER TABLE `tabScanned Document` ADD INDEX `idx_ocr_text` (`ocr_text`(255));
   ```

### OCR Performance

1. **Use appropriate image quality**:
   - Draft: 150 DPI
   - Normal: 300 DPI
   - High: 600 DPI
   - Maximum: 1200 DPI

2. **Enable parallel processing**:
   ```python
   # In config.py
   PERFORMANCE_CONFIG = {
       'parallel_processing': True,
       'max_workers': 4
   }
   ```

## Security Considerations

### File Security

1. **Enable file encryption**:
   ```python
   # In config.py
   SECURITY_CONFIG = {
       'encrypt_files': True
   }
   ```

2. **Set up access control**:
   ```python
   SECURITY_CONFIG = {
       'file_access_control': True
   }
   ```

3. **Enable API authentication**:
   ```python
   SECURITY_CONFIG = {
       'api_key_required': True
   }
   ```

### Network Security

1. **Configure HTTPS** for file uploads
2. **Set up firewall rules** for scanner ports
3. **Use VPN** for remote scanner access

## Maintenance

### Regular Tasks

1. **Clean up old files**:
   ```bash
   find /path/to/files -type f -mtime +365 -delete
   ```

2. **Optimize database**:
   ```bash
   bench --site <site-name> mariadb optimize
   ```

3. **Update dependencies**:
   ```bash
   pip install --upgrade Pillow pytesseract opencv-python
   ```

### Backup

1. **Backup database**:
   ```bash
   bench --site <site-name> backup
   ```

2. **Backup files**:
   ```bash
   tar -czf document_archiver_files.tar.gz /path/to/files
   ```

## Support

For additional support:
- Check the README.md file
- Create an issue on GitHub
- Contact the development team
- Check ERPNext community forums