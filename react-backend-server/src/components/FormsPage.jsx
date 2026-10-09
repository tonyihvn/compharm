import React, { useState, useEffect } from 'react';
import './FormsPage.css';
import FormEditor from './FormEditor';
import FormPreview from './FormPreview';

function FormsPage() {
    const [forms, setForms] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [showEditor, setShowEditor] = useState(false);
    const [showPreview, setShowPreview] = useState(false);
    const [selectedForm, setSelectedForm] = useState(null);
    const [editingForm, setEditingForm] = useState(null);
    const [uploadError, setUploadError] = useState(null);
    const [uploadSuccess, setUploadSuccess] = useState(false);

    useEffect(() => {
        loadForms();
    }, []);

    const loadForms = async () => {
        try {
            setLoading(true);
            setError(null);
            const token = localStorage.getItem('token');
            
            const response = await fetch('/api/forms', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load forms');
            }

            const result = await response.json();
            setForms(result.data || []);
        } catch (err) {
            setError(err.message);
            console.error('Error loading forms:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleUploadForm = async (formData) => {
        try {
            setUploadError(null);
            setUploadSuccess(false);
            const token = localStorage.getItem('token');

            const response = await fetch('/api/forms/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to upload form');
            }

            const result = await response.json();
            setUploadSuccess(true);
            setShowUploadModal(false);
            
            // Reload forms list
            await loadForms();

            // Clear success message after 3 seconds
            setTimeout(() => setUploadSuccess(false), 3000);
        } catch (err) {
            setUploadError(err.message);
            console.error('Error uploading form:', err);
        }
    };

    const handleEditForm = (form) => {
        setEditingForm(form);
        setShowEditor(true);
    };

    const handleSaveForm = async (updatedFormData) => {
        try {
            setError(null);
            const token = localStorage.getItem('token');

            const response = await fetch(`/api/forms/${editingForm.id}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updatedFormData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to update form');
            }

            setShowEditor(false);
            setEditingForm(null);
            
            // Reload forms list
            await loadForms();
        } catch (err) {
            setError(err.message);
            console.error('Error updating form:', err);
        }
    };

    const handleDeleteForm = async (formId) => {
        if (!window.confirm('Are you sure you want to delete this form? This action cannot be undone.')) {
            return;
        }

        try {
            setError(null);
            const token = localStorage.getItem('token');

            const response = await fetch(`/api/forms/${formId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to delete form');
            }

            // Reload forms list
            await loadForms();
        } catch (err) {
            setError(err.message);
            console.error('Error deleting form:', err);
        }
    };

    const handleDeactivateForm = async (formId) => {
        try {
            setError(null);
            const token = localStorage.getItem('token');

            const response = await fetch(`/api/forms/${formId}/deactivate`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to deactivate form');
            }

            // Reload forms list
            await loadForms();
        } catch (err) {
            setError(err.message);
            console.error('Error deactivating form:', err);
        }
    };

    const handleDownloadForm = (form) => {
        const dataStr = JSON.stringify(form.form_data || form, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${form.form_name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    const filteredForms = forms.filter(form =>
        form.form_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (form.description && form.description.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    if (showEditor && editingForm) {
        return (
            <FormEditor
                form={editingForm}
                onSave={handleSaveForm}
                onCancel={() => {
                    setShowEditor(false);
                    setEditingForm(null);
                }}
            />
        );
    }

    if (showPreview && selectedForm) {
        return (
            <FormPreview
                form={selectedForm}
                onClose={() => {
                    setShowPreview(false);
                    setSelectedForm(null);
                }}
            />
        );
    }

    return (
        <div className="forms-page">
            <div className="forms-header">
                <h2>Forms Management</h2>
                <button 
                    className="btn btn-primary"
                    onClick={() => setShowUploadModal(true)}
                >
                    + Upload New Form
                </button>
            </div>

            {error && (
                <div className="alert alert-error">
                    {error}
                    <button onClick={() => setError(null)} className="alert-close">&times;</button>
                </div>
            )}

            {uploadSuccess && (
                <div className="alert alert-success">
                    Form uploaded successfully!
                    <button onClick={() => setUploadSuccess(false)} className="alert-close">&times;</button>
                </div>
            )}

            <div className="forms-search">
                <input
                    type="text"
                    placeholder="Search forms by name or description..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="search-input"
                />
            </div>

            {loading ? (
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p>Loading forms...</p>
                </div>
            ) : filteredForms.length === 0 ? (
                <div className="empty-state">
                    <p>No forms found. {forms.length === 0 ? 'Upload your first form to get started.' : 'Try adjusting your search.'}</p>
                </div>
            ) : (
                <div className="forms-grid">
                    {filteredForms.map(form => (
                        <div key={form.id} className="form-card">
                            <div className="form-card-header">
                                <h3>{form.form_name}</h3>
                                <span className={`badge ${form.is_active ? 'badge-active' : 'badge-inactive'}`}>
                                    {form.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </div>

                            <div className="form-card-body">
                                {form.description && (
                                    <p className="form-description">{form.description}</p>
                                )}
                                
                                <div className="form-meta">
                                    <div className="meta-item">
                                        <span className="meta-label">Version:</span>
                                        <span className="meta-value">v{form.version || 1}</span>
                                    </div>
                                    <div className="meta-item">
                                        <span className="meta-label">UUID:</span>
                                        <span className="meta-value" title={form.form_uuid}>
                                            {form.form_uuid?.substring(0, 8)}...
                                        </span>
                                    </div>
                                    <div className="meta-item">
                                        <span className="meta-label">Created:</span>
                                        <span className="meta-value">
                                            {new Date(form.createdAt).toLocaleDateString()}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div className="form-card-actions">
                                <button
                                    className="btn btn-secondary btn-sm"
                                    onClick={() => {
                                        setSelectedForm(form);
                                        setShowPreview(true);
                                    }}
                                    title="Preview form"
                                >
                                    👁️ Preview
                                </button>
                                <button
                                    className="btn btn-secondary btn-sm"
                                    onClick={() => handleEditForm(form)}
                                    title="Edit form"
                                >
                                    ✏️ Edit
                                </button>
                                <button
                                    className="btn btn-secondary btn-sm"
                                    onClick={() => handleDownloadForm(form)}
                                    title="Download as JSON"
                                >
                                    ⬇️ Download
                                </button>
                                <button
                                    className="btn btn-warning btn-sm"
                                    onClick={() => handleDeactivateForm(form.id)}
                                    title="Deactivate form"
                                    disabled={!form.is_active}
                                >
                                    🚫 Deactivate
                                </button>
                                <button
                                    className="btn btn-danger btn-sm"
                                    onClick={() => handleDeleteForm(form.id)}
                                    title="Delete form permanently"
                                >
                                    🗑️ Delete
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {showUploadModal && (
                <div className="modal-overlay">
                    <div className="modal">
                        <div className="modal-header">
                            <h3>Upload New Form</h3>
                            <button
                                className="modal-close"
                                onClick={() => {
                                    setShowUploadModal(false);
                                    setUploadError(null);
                                }}
                            >
                                ×
                            </button>
                        </div>

                        <div className="modal-body">
                            {uploadError && (
                                <div className="alert alert-error">
                                    {uploadError}
                                </div>
                            )}

                            <UploadFormModal
                                onUpload={handleUploadForm}
                                onCancel={() => {
                                    setShowUploadModal(false);
                                    setUploadError(null);
                                }}
                            />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

// Upload Form Modal Component
function UploadFormModal({ onUpload, onCancel }) {
    const [uploadMethod, setUploadMethod] = useState('file');
    const [formJSON, setFormJSON] = useState('');
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const jsonData = JSON.parse(event.target.result);
                    setFormJSON(JSON.stringify(jsonData, null, 2));
                    setFile(selectedFile);
                } catch (error) {
                    alert('Invalid JSON file');
                    setFile(null);
                }
            };
            reader.readAsText(selectedFile);
        }
    };

    const handleUpload = async () => {
        try {
            if (!formJSON.trim()) {
                alert('Please provide form JSON');
                return;
            }

            const formData = JSON.parse(formJSON);

            // Validate form structure
            if (!formData.name) {
                alert('Form must have a "name" property');
                return;
            }

            if (!formData.sections || formData.sections.length === 0) {
                alert('Form must have at least one section with "sections" property');
                return;
            }

            setUploading(true);
            await onUpload(formData);
            setFormJSON('');
            setFile(null);
        } catch (error) {
            alert('Invalid JSON format: ' + error.message);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="upload-form">
            <div className="upload-tabs">
                <button
                    className={`tab-btn ${uploadMethod === 'file' ? 'active' : ''}`}
                    onClick={() => setUploadMethod('file')}
                >
                    Upload JSON File
                </button>
                <button
                    className={`tab-btn ${uploadMethod === 'paste' ? 'active' : ''}`}
                    onClick={() => setUploadMethod('paste')}
                >
                    Paste JSON
                </button>
            </div>

            <div className="upload-content">
                {uploadMethod === 'file' && (
                    <div className="file-upload">
                        <input
                            type="file"
                            accept=".json"
                            onChange={handleFileChange}
                            id="form-file-input"
                            style={{ display: 'none' }}
                        />
                        <label htmlFor="form-file-input" className="file-input-label">
                            <div className="file-input-box">
                                <span className="file-icon">📄</span>
                                <p>Click to select a JSON file or drag and drop</p>
                                {file && <p className="file-name">{file.name}</p>}
                            </div>
                        </label>
                    </div>
                )}

                {uploadMethod === 'paste' && (
                    <textarea
                        value={formJSON}
                        onChange={(e) => setFormJSON(e.target.value)}
                        placeholder="Paste your form JSON here..."
                        className="json-textarea"
                    />
                )}

                <div className="json-preview">
                    <h4>JSON Preview:</h4>
                    <pre className="json-code">
                        {formJSON ? JSON.stringify(JSON.parse(formJSON), null, 2) : '(Form JSON will appear here)'}
                    </pre>
                </div>
            </div>

            <div className="modal-footer">
                <button
                    className="btn btn-secondary"
                    onClick={onCancel}
                    disabled={uploading}
                >
                    Cancel
                </button>
                <button
                    className="btn btn-primary"
                    onClick={handleUpload}
                    disabled={uploading || !formJSON.trim()}
                >
                    {uploading ? 'Uploading...' : 'Upload Form'}
                </button>
            </div>
        </div>
    );
}

export default FormsPage;
