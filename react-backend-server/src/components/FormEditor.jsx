import React, { useState, useEffect } from 'react';
import './FormEditor.css';

function FormEditor({ form, onSave, onCancel }) {
    const [formData, setFormData] = useState(() => {
        if (form.form_data && typeof form.form_data === 'object') {
            return typeof form.form_data === 'string' ? JSON.parse(form.form_data) : form.form_data;
        }
        return {};
    });
    const [jsonView, setJsonView] = useState(false);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);

    const handleFormChange = (field, value) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
        setError(null);
    };

    const handleAddSection = () => {
        setFormData(prev => ({
            ...prev,
            sections: [
                ...(prev.sections || []),
                {
                    name: `Section ${(prev.sections?.length || 0) + 1}`,
                    questions: []
                }
            ]
        }));
    };

    const handleUpdateSection = (index, field, value) => {
        setFormData(prev => {
            const sections = [...prev.sections];
            sections[index] = { ...sections[index], [field]: value };
            return { ...prev, sections };
        });
    };

    const handleRemoveSection = (index) => {
        setFormData(prev => ({
            ...prev,
            sections: prev.sections.filter((_, i) => i !== index)
        }));
    };

    const handleAddQuestion = (sectionIndex) => {
        setFormData(prev => {
            const sections = [...prev.sections];
            sections[sectionIndex].questions = [
                ...(sections[sectionIndex].questions || []),
                {
                    id: `q_${Date.now()}`,
                    label: 'New Question',
                    type: 'text',
                    required: false
                }
            ];
            return { ...prev, sections };
        });
    };

    const handleUpdateQuestion = (sectionIndex, questionIndex, field, value) => {
        setFormData(prev => {
            const sections = [...prev.sections];
            const questions = [...sections[sectionIndex].questions];
            questions[questionIndex] = { ...questions[questionIndex], [field]: value };
            sections[sectionIndex].questions = questions;
            return { ...prev, sections };
        });
    };

    const handleRemoveQuestion = (sectionIndex, questionIndex) => {
        setFormData(prev => {
            const sections = [...prev.sections];
            sections[sectionIndex].questions = sections[sectionIndex].questions.filter((_, i) => i !== questionIndex);
            return { ...prev, sections };
        });
    };

    const handleSaveForm = async () => {
        try {
            setError(null);

            // Validate form
            if (!formData.name || !formData.name.trim()) {
                setError('Form name is required');
                return;
            }

            if (!formData.sections || formData.sections.length === 0) {
                setError('Form must have at least one section');
                return;
            }

            setSaving(true);
            await onSave(formData);
        } catch (err) {
            setError(err.message);
            setSaving(false);
        }
    };

    const handleJsonChange = (json) => {
        try {
            const parsed = JSON.parse(json);
            setFormData(parsed);
            setError(null);
        } catch (err) {
            setError('Invalid JSON: ' + err.message);
        }
    };

    return (
        <div className="form-editor">
            <div className="editor-header">
                <h2>Edit Form: {formData.name || 'Untitled'}</h2>
                <div className="editor-actions">
                    <button
                        className={`view-toggle ${jsonView ? 'active' : ''}`}
                        onClick={() => setJsonView(!jsonView)}
                    >
                        {jsonView ? 'Visual Editor' : 'JSON Editor'}
                    </button>
                </div>
            </div>

            {error && (
                <div className="alert alert-error">
                    {error}
                    <button onClick={() => setError(null)} className="alert-close">&times;</button>
                </div>
            )}

            <div className="editor-container">
                {jsonView ? (
                    <div className="json-editor-panel">
                        <h3>JSON View</h3>
                        <textarea
                            value={JSON.stringify(formData, null, 2)}
                            onChange={(e) => handleJsonChange(e.target.value)}
                            className="json-editor"
                            spellCheck="false"
                        />
                    </div>
                ) : (
                    <div className="visual-editor-panel">
                        <div className="form-basic-info">
                            <h3>Form Information</h3>
                            
                            <div className="form-group">
                                <label>Form Name *</label>
                                <input
                                    type="text"
                                    value={formData.name || ''}
                                    onChange={(e) => handleFormChange('name', e.target.value)}
                                    placeholder="Enter form name"
                                    className="form-input"
                                />
                            </div>

                            <div className="form-group">
                                <label>Description</label>
                                <textarea
                                    value={formData.description || ''}
                                    onChange={(e) => handleFormChange('description', e.target.value)}
                                    placeholder="Enter form description"
                                    className="form-textarea"
                                    rows="3"
                                />
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>UUID</label>
                                    <input
                                        type="text"
                                        value={formData.uuid || ''}
                                        onChange={(e) => handleFormChange('uuid', e.target.value)}
                                        placeholder="Auto-generated if empty"
                                        className="form-input"
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Version</label>
                                    <input
                                        type="text"
                                        value={formData.version || '1.0'}
                                        onChange={(e) => handleFormChange('version', e.target.value)}
                                        className="form-input"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="form-sections">
                            <div className="sections-header">
                                <h3>Form Sections</h3>
                                <button
                                    className="btn btn-secondary btn-sm"
                                    onClick={handleAddSection}
                                >
                                    + Add Section
                                </button>
                            </div>

                            <div className="sections-list">
                                {(formData.sections || []).map((section, sectionIndex) => (
                                    <div key={sectionIndex} className="section-card">
                                        <div className="section-header">
                                            <input
                                                type="text"
                                                value={section.name}
                                                onChange={(e) => handleUpdateSection(sectionIndex, 'name', e.target.value)}
                                                placeholder="Section name"
                                                className="section-name-input"
                                            />
                                            <button
                                                className="btn btn-danger btn-xs"
                                                onClick={() => handleRemoveSection(sectionIndex)}
                                                title="Delete section"
                                            >
                                                ×
                                            </button>
                                        </div>

                                        <div className="questions-list">
                                            {(section.questions || []).map((question, questionIndex) => (
                                                <div key={questionIndex} className="question-card">
                                                    <div className="question-row">
                                                        <input
                                                            type="text"
                                                            value={question.label}
                                                            onChange={(e) => handleUpdateQuestion(sectionIndex, questionIndex, 'label', e.target.value)}
                                                            placeholder="Question label"
                                                            className="question-label-input"
                                                        />
                                                        <select
                                                            value={question.type || 'text'}
                                                            onChange={(e) => handleUpdateQuestion(sectionIndex, questionIndex, 'type', e.target.value)}
                                                            className="question-type-select"
                                                        >
                                                            <option value="text">Text</option>
                                                            <option value="textarea">Textarea</option>
                                                            <option value="number">Number</option>
                                                            <option value="date">Date</option>
                                                            <option value="select">Select</option>
                                                            <option value="checkbox">Checkbox</option>
                                                            <option value="radio">Radio</option>
                                                        </select>
                                                        <label className="checkbox-inline">
                                                            <input
                                                                type="checkbox"
                                                                checked={question.required || false}
                                                                onChange={(e) => handleUpdateQuestion(sectionIndex, questionIndex, 'required', e.target.checked)}
                                                            />
                                                            Required
                                                        </label>
                                                        <button
                                                            className="btn btn-danger btn-xs"
                                                            onClick={() => handleRemoveQuestion(sectionIndex, questionIndex)}
                                                            title="Delete question"
                                                        >
                                                            ×
                                                        </button>
                                                    </div>

                                                    {(question.type === 'select' || question.type === 'radio') && (
                                                        <div className="question-options">
                                                            <label>Options (comma-separated):</label>
                                                            <input
                                                                type="text"
                                                                value={(question.options || []).join(', ')}
                                                                onChange={(e) => {
                                                                    const options = e.target.value.split(',').map(o => o.trim()).filter(Boolean);
                                                                    handleUpdateQuestion(sectionIndex, questionIndex, 'options', options);
                                                                }}
                                                                placeholder="Option1, Option2, Option3"
                                                                className="form-input"
                                                            />
                                                        </div>
                                                    )}

                                                    <input
                                                        type="text"
                                                        value={question.placeholder || ''}
                                                        onChange={(e) => handleUpdateQuestion(sectionIndex, questionIndex, 'placeholder', e.target.value)}
                                                        placeholder="Placeholder text"
                                                        className="form-input"
                                                    />
                                                </div>
                                            ))}
                                        </div>

                                        <button
                                            className="btn btn-secondary btn-sm"
                                            onClick={() => handleAddQuestion(sectionIndex)}
                                        >
                                            + Add Question
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <div className="editor-footer">
                <button
                    className="btn btn-secondary"
                    onClick={onCancel}
                    disabled={saving}
                >
                    Cancel
                </button>
                <button
                    className="btn btn-primary"
                    onClick={handleSaveForm}
                    disabled={saving}
                >
                    {saving ? 'Saving...' : 'Save Changes'}
                </button>
            </div>
        </div>
    );
}

export default FormEditor;
