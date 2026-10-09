import React, { useState } from 'react';
import './FormPreview.css';

function FormPreview({ form, onClose }) {
    const [formResponse, setFormResponse] = useState({});
    const [submitting, setSubmitting] = useState(false);
    const [showJson, setShowJson] = useState(false);

    const formData = form.form_data && typeof form.form_data === 'object'
        ? typeof form.form_data === 'string' ? JSON.parse(form.form_data) : form.form_data
        : {};

    const handleInputChange = (fieldId, value) => {
        setFormResponse(prev => ({
            ...prev,
            [fieldId]: value
        }));
    };

    const handleSubmitPreview = async () => {
        try {
            setSubmitting(true);
            
            // This is just a preview, so we'll show a success message
            alert('Form preview submitted successfully!\n\nThis is a preview-only action.\nForms submitted by clients through the Python app will be synced to this server.');
            
            // Reset form
            setFormResponse({});
        } catch (error) {
            alert('Error submitting preview: ' + error.message);
        } finally {
            setSubmitting(false);
        }
    };

    const handleResetForm = () => {
        setFormResponse({});
    };

    return (
        <div className="form-preview">
            <div className="preview-header">
                <div className="preview-title">
                    <button className="back-btn" onClick={onClose} title="Back to forms">←</button>
                    <div>
                        <h2>{formData.name || 'Untitled Form'}</h2>
                        <p className="form-meta">
                            Version {form.version || 1} • UUID: {form.form_uuid?.substring(0, 12)}...
                        </p>
                    </div>
                </div>
                <div className="preview-actions">
                    <button
                        className={`view-toggle ${showJson ? 'active' : ''}`}
                        onClick={() => setShowJson(!showJson)}
                    >
                        {showJson ? 'Form View' : 'JSON View'}
                    </button>
                </div>
            </div>

            {formData.description && (
                <div className="form-description-box">
                    <p>{formData.description}</p>
                </div>
            )}

            <div className="preview-content">
                {showJson ? (
                    <div className="json-view">
                        <h3>Form Definition (JSON)</h3>
                        <pre className="json-code">
                            {JSON.stringify(formData, null, 2)}
                        </pre>
                    </div>
                ) : (
                    <div className="form-view">
                        <form className="preview-form">
                            {(formData.sections || []).map((section, sectionIndex) => (
                                <div key={sectionIndex} className="form-section">
                                    <h3 className="section-title">{section.name}</h3>
                                    <div className="section-divider"></div>

                                    {(section.questions || []).map((question, questionIndex) => (
                                        <div key={questionIndex} className="form-field">
                                            <label className="field-label">
                                                {question.label}
                                                {question.required && <span className="required">*</span>}
                                            </label>

                                            {question.type === 'text' && (
                                                <input
                                                    type="text"
                                                    placeholder={question.placeholder}
                                                    value={formResponse[question.id] || ''}
                                                    onChange={(e) => handleInputChange(question.id, e.target.value)}
                                                    className="form-input"
                                                />
                                            )}

                                            {question.type === 'textarea' && (
                                                <textarea
                                                    placeholder={question.placeholder}
                                                    value={formResponse[question.id] || ''}
                                                    onChange={(e) => handleInputChange(question.id, e.target.value)}
                                                    className="form-textarea"
                                                    rows="4"
                                                />
                                            )}

                                            {question.type === 'number' && (
                                                <input
                                                    type="number"
                                                    placeholder={question.placeholder}
                                                    value={formResponse[question.id] || ''}
                                                    onChange={(e) => handleInputChange(question.id, e.target.value)}
                                                    className="form-input"
                                                />
                                            )}

                                            {question.type === 'date' && (
                                                <input
                                                    type="date"
                                                    value={formResponse[question.id] || ''}
                                                    onChange={(e) => handleInputChange(question.id, e.target.value)}
                                                    className="form-input"
                                                />
                                            )}

                                            {question.type === 'select' && (
                                                <select
                                                    value={formResponse[question.id] || ''}
                                                    onChange={(e) => handleInputChange(question.id, e.target.value)}
                                                    className="form-select"
                                                >
                                                    <option value="">-- Select --</option>
                                                    {(question.options || []).map((option, optIndex) => (
                                                        <option key={optIndex} value={option}>
                                                            {option}
                                                        </option>
                                                    ))}
                                                </select>
                                            )}

                                            {question.type === 'radio' && (
                                                <div className="radio-group">
                                                    {(question.options || []).map((option, optIndex) => (
                                                        <label key={optIndex} className="radio-label">
                                                            <input
                                                                type="radio"
                                                                name={question.id}
                                                                value={option}
                                                                checked={formResponse[question.id] === option}
                                                                onChange={(e) => handleInputChange(question.id, e.target.value)}
                                                            />
                                                            {option}
                                                        </label>
                                                    ))}
                                                </div>
                                            )}

                                            {question.type === 'checkbox' && (
                                                <label className="checkbox-label">
                                                    <input
                                                        type="checkbox"
                                                        checked={formResponse[question.id] || false}
                                                        onChange={(e) => handleInputChange(question.id, e.target.checked)}
                                                    />
                                                    {question.label}
                                                </label>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            ))}
                        </form>

                        <div className="form-actions">
                            <button
                                className="btn btn-secondary"
                                onClick={handleResetForm}
                                disabled={submitting}
                            >
                                Reset Form
                            </button>
                            <button
                                className="btn btn-primary"
                                onClick={handleSubmitPreview}
                                disabled={submitting}
                            >
                                {submitting ? 'Submitting...' : 'Submit Preview'}
                            </button>
                        </div>

                        <div className="form-response-preview">
                            <h4>Preview Response Data</h4>
                            <pre className="json-code">
                                {JSON.stringify(formResponse, null, 2)}
                            </pre>
                        </div>
                    </div>
                )}
            </div>

            <div className="preview-footer">
                <p className="info-text">
                    This is a preview of how the form will appear to users in the Python Pharmacy App.
                    Actual client submissions will be synced back to this server.
                </p>
                <button className="btn btn-secondary" onClick={onClose}>
                    Close Preview
                </button>
            </div>
        </div>
    );
}

export default FormPreview;
