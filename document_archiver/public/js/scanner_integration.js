// Scanner Integration JavaScript for Document Archiver
frappe.provide("document_archiver.scanner");

document_archiver.scanner = {
	init: function() {
		this.setup_scanner_ui();
		this.setup_webcam_integration();
		this.setup_file_upload();
	},

	setup_scanner_ui: function() {
		// Add scanner buttons to Document Archive form
		if (cur_frm && cur_frm.doctype === "Document Archive") {
			this.add_scanner_buttons();
		}
	},

	add_scanner_buttons: function() {
		// Add scanner buttons to the form
		cur_frm.add_custom_button(__("Scan with Webcam"), function() {
			document_archiver.scanner.open_webcam_modal();
		}, __("Scan"));

		cur_frm.add_custom_button(__("Scan with SANE"), function() {
			document_archiver.scanner.scan_with_sane();
		}, __("Scan"));

		cur_frm.add_custom_button(__("Upload Scanned File"), function() {
			document_archiver.scanner.open_file_upload_modal();
		}, __("Upload"));
	},

	open_webcam_modal: function() {
		let d = new frappe.ui.Dialog({
			title: __("Scan with Webcam"),
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "webcam_container",
					options: `
						<div id="webcam-container" style="text-align: center;">
							<video id="webcam-video" width="640" height="480" autoplay style="display: none;"></video>
							<canvas id="webcam-canvas" width="640" height="480" style="display: none;"></canvas>
							<div id="webcam-preview" style="margin: 10px 0;"></div>
						</div>
					`
				},
				{
					fieldtype: "Select",
					fieldname: "scan_quality",
					label: __("Scan Quality"),
					options: "Draft\nNormal\nHigh\nMaximum",
					default: "High"
				},
				{
					fieldtype: "Button",
					fieldname: "capture_btn",
					label: __("Capture"),
					click: function() {
						document_archiver.scanner.capture_webcam_image();
					}
				}
			],
			primary_action_label: __("Scan Document"),
			primary_action: function() {
				document_archiver.scanner.process_webcam_scan(d);
			}
		});

		d.show();
		this.start_webcam();
	},

	start_webcam: function() {
		navigator.mediaDevices.getUserMedia({ video: true })
			.then(function(stream) {
				const video = document.getElementById('webcam-video');
				video.srcObject = stream;
				video.style.display = 'block';
			})
			.catch(function(err) {
				frappe.msgprint(__("Error accessing webcam: ") + err.message);
			});
	},

	capture_webcam_image: function() {
		const video = document.getElementById('webcam-video');
		const canvas = document.getElementById('webcam-canvas');
		const preview = document.getElementById('webcam-preview');
		
		const ctx = canvas.getContext('2d');
		ctx.drawImage(video, 0, 0, 640, 480);
		
		// Show preview
		const dataURL = canvas.toDataURL('image/png');
		preview.innerHTML = `<img src="${dataURL}" style="max-width: 300px; max-height: 200px;">`;
		
		// Store image data for processing
		this.captured_image_data = dataURL;
	},

	process_webcam_scan: function(dialog) {
		if (!this.captured_image_data) {
			frappe.msgprint(__("Please capture an image first"));
			return;
		}

		const quality = dialog.get_value('scan_quality') || 'High';
		
		frappe.call({
			method: "document_archiver.api.scanner.scan_with_webcam",
			args: {
				document_archive_id: cur_frm.doc.name,
				quality: quality
			},
			callback: function(r) {
				if (r.message.status === 'success') {
					frappe.msgprint(__("Document scanned successfully"));
					cur_frm.reload_doc();
					dialog.hide();
				} else {
					frappe.msgprint(__("Error: ") + r.message.message);
				}
			}
		});
	},

	scan_with_sane: function() {
		frappe.call({
			method: "document_archiver.api.scanner.scan_with_sane",
			args: {
				document_archive_id: cur_frm.doc.name
			},
			callback: function(r) {
				if (r.message.status === 'success') {
					frappe.msgprint(__("Document scanned successfully"));
					cur_frm.reload_doc();
				} else {
					frappe.msgprint(__("Error: ") + r.message.message);
				}
			}
		});
	},

	open_file_upload_modal: function() {
		let d = new frappe.ui.Dialog({
			title: __("Upload Scanned Document"),
			fields: [
				{
					fieldtype: "Attach",
					fieldname: "file_attachment",
					label: __("Scanned File"),
					reqd: 1
				},
				{
					fieldtype: "Data",
					fieldname: "scanner_name",
					label: __("Scanner Name"),
					default: "Mobile Upload"
				},
				{
					fieldtype: "Select",
					fieldname: "scan_quality",
					label: __("Scan Quality"),
					options: "Draft\nNormal\nHigh\nMaximum",
					default: "High"
				}
			],
			primary_action_label: __("Upload Document"),
			primary_action: function() {
				document_archiver.scanner.process_file_upload(d);
			}
		});

		d.show();
	},

	process_file_upload: function(dialog) {
		const file_attachment = dialog.get_value('file_attachment');
		const scanner_name = dialog.get_value('scanner_name') || 'Mobile Upload';
		const quality = dialog.get_value('scan_quality') || 'High';

		if (!file_attachment) {
			frappe.msgprint(__("Please select a file"));
			return;
		}

		// Get file data
		frappe.call({
			method: "frappe.client.get_file",
			args: {
				file_url: file_attachment
			},
			callback: function(r) {
				if (r.message) {
					// Convert file to base64
					const file_data = btoa(String.fromCharCode.apply(null, new Uint8Array(r.message)));
					
					frappe.call({
						method: "document_archiver.api.scanner.upload_scanned_document",
						args: {
							document_archive_id: cur_frm.doc.name,
							file_data: file_data,
							scanner_name: scanner_name,
							quality: quality
						},
						callback: function(r) {
							if (r.message.status === 'success') {
								frappe.msgprint(__("Document uploaded successfully"));
								cur_frm.reload_doc();
								dialog.hide();
							} else {
								frappe.msgprint(__("Error: ") + r.message.message);
							}
						}
					});
				}
			}
		});
	},

	setup_webcam_integration: function() {
		// Additional webcam setup if needed
	},

	setup_file_upload: function() {
		// Additional file upload setup if needed
	}
};

// Initialize when page loads
$(document).ready(function() {
	document_archiver.scanner.init();
});