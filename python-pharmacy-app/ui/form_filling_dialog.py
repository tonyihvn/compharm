"""
Form Filling Dialog - Wraps FormView with submission and sync capabilities
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
import logging
import json
import requests

logger = logging.getLogger(__name__)


class FormSubmissionWorker(QThread):
    """Background worker for form submission"""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, api_url, form_submission_data, auth_token):
        super().__init__()
        self.api_url = api_url
        self.form_submission_data = form_submission_data
        self.auth_token = auth_token
    
    def run(self):
        """Submit form to backend server"""
        try:
            self.progress.emit("Submitting form to server...")
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.auth_token}' if self.auth_token else ''
            }
            
            # Submit to backend
            response = requests.post(
                f"{self.api_url}/api/form-submissions",
                json=self.form_submission_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                self.progress.emit("Form submitted successfully!")
                self.finished.emit(True, "Form submitted and synced to server")
            else:
                error_msg = response.json().get('message', f'Server returned {response.status_code}')
                self.progress.emit(f"Submission failed: {error_msg}")
                self.finished.emit(False, error_msg)
        
        except Exception as e:
            error_msg = f"Error submitting form: {str(e)}"
            logger.error(error_msg)
            self.progress.emit(error_msg)
            # Don't fail if offline - form is saved locally
            self.finished.emit(False, "Form saved locally (offline mode)")


class FormFillingDialog(QDialog):
    """Dialog for filling and submitting forms"""
    
    form_submitted = pyqtSignal(dict)  # Emit submission data
    
    def __init__(self, form_definition, client_data, api_url, db_manager, auth_token=None, parent=None):
        super().__init__(parent)
        self.form_definition = form_definition
        self.client_data = client_data
        self.api_url = api_url
        self.db_manager = db_manager
        self.auth_token = auth_token
        self.form_submission_data = None
        self.submission_worker = None
        
        self.setWindowTitle(f"Fill Form: {form_definition.get('name', 'Form')}")
        self.setGeometry(50, 50, 900, 700)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Import FormView here to avoid circular imports
        from ui.form_view import FormView
        
        # Create form view
        self.form_view = FormView(self.form_definition, self.client_data, self.api_url)
        self.form_view.form_submitted.connect(self.on_form_submitted)
        layout.addWidget(self.form_view)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save as Draft")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        save_btn.clicked.connect(self.on_save_draft)
        button_layout.addWidget(save_btn)
        
        submit_btn = QPushButton("Submit & Sync")
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        submit_btn.clicked.connect(self.on_submit_form)
        button_layout.addWidget(submit_btn)
        
        cancel_btn = QPushButton("Close")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def on_save_draft(self):
        """Save form as draft"""
        try:
            # Collect form data
            form_data = self.form_view.collect_form_data()
            
            if not form_data:
                QMessageBox.warning(self, "Warning", "No form data to save")
                return
            
            # Save to database
            client_id = self.client_data.get('id')
            form_uuid = self.form_definition.get('uuid')
            
            submission_id = self.db_manager.add_form_submission(
                form_uuid=form_uuid,
                client_id=client_id,
                submission_data=form_data,
                status='draft'
            )
            
            QMessageBox.information(
                self,
                "Success",
                f"Form saved as draft (ID: {submission_id})\n\n"
                "You can submit it later from the Submissions tab."
            )
            logger.info(f"Form saved as draft: {submission_id}")
        
        except Exception as e:
            logger.error(f"Error saving draft: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to save draft: {str(e)}")
    
    def on_submit_form(self):
        """Submit form and sync to server"""
        try:
            # Collect form data
            form_data = self.form_view.collect_form_data()
            
            if not form_data:
                QMessageBox.warning(self, "Warning", "Please fill in the form first")
                return
            
            # Prepare submission data
            client_id = self.client_data.get('id')
            form_uuid = self.form_definition.get('uuid')
            
            self.form_submission_data = {
                'form_uuid': form_uuid,
                'client_id': client_id,
                'data': form_data,
                'status': 'submitted'
            }
            
            # Save to database first
            submission_id = self.db_manager.add_form_submission(
                form_uuid=form_uuid,
                client_id=client_id,
                submission_data=form_data,
                status='submitted'
            )
            
            logger.info(f"Form submission saved locally: {submission_id}")
            
            # Show progress dialog
            progress = QProgressDialog(
                "Submitting form to server...",
                None,
                0,
                0,
                self
            )
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()
            
            # Start background submission
            self.submission_worker = FormSubmissionWorker(
                self.api_url,
                self.form_submission_data,
                self.auth_token
            )
            self.submission_worker.progress.connect(progress.setLabelText)
            self.submission_worker.finished.connect(
                lambda success, msg: self.on_submission_complete(success, msg, progress, submission_id)
            )
            self.submission_worker.start()
        
        except Exception as e:
            logger.error(f"Error submitting form: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to submit form: {str(e)}")
    
    def on_submission_complete(self, success, message, progress_dialog, submission_id):
        """Handle form submission completion"""
        progress_dialog.close()
        
        if success:
            # Mark as synced in database
            try:
                self.db_manager.mark_submission_synced(submission_id)
                QMessageBox.information(
                    self,
                    "Success",
                    message
                )
                self.form_submitted.emit(self.form_submission_data)
                self.accept()
            except Exception as e:
                logger.error(f"Error marking submission as synced: {str(e)}")
                QMessageBox.warning(self, "Warning", f"{message}\n\nNote: {str(e)}")
        else:
            # Form saved locally, will sync later
            QMessageBox.information(
                self,
                "Saved Locally",
                message + "\n\nThe form has been saved locally and will be synced when server is available."
            )
    
    def on_form_submitted(self, form_data):
        """Handle form submission signal from FormView"""
        # FormView has its own submission handling
        # This is a fallback or alternative submission path
        pass
