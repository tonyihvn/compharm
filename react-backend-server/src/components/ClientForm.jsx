import React, { useState, useEffect } from 'react';
import './ClientForm.css';

const ClientForm = ({ onSuccess, onCancel, facilityId, pharmacyId }) => {
    const [customFields, setCustomFields] = useState([]);
    const [formData, setFormData] = useState({});
    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });

    const standardFields = [
        { name: 'Full Name', field_name: 'full_name', field_type: 'text', required: true, section: 'Personal Information' },
        { name: 'PEPFAR ID', field_name: 'pepfar_id', field_type: 'text', required: true, section: 'Personal Information' },
        { name: 'Date of Birth', field_name: 'date_of_birth', field_type: 'date', required: false, section: 'Personal Information' },
        { name: 'Gender', field_name: 'gender', field_type: 'select', required: false, section: 'Personal Information', options: ['Male', 'Female', 'Other'] },
        { name: 'Phone Number', field_name: 'phone_number', field_type: 'tel', required: false, section: 'Personal Information' },
        { name: 'Email', field_name: 'email', field_type: 'email', required: false, section: 'Personal Information' },
        { name: 'Address', field_name: 'address', field_type: 'text', required: false, section: 'Personal Information' }
    ];

    // Fetch custom fields on component mount
    useEffect(() => {
        fetchCustomFields();
    }, []);

    const fetchCustomFields = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('token');
            
            const response = await fetch('/api/fields', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch custom fields');
            }

            const data = await response.json();
            const fields = data.fields || [];
            
            // Mark custom fields and assign to section
            const customFieldsWithSection = fields.map((field, index) => ({
                ...field,
                section: field.category || 'Additional Information',
                order: field.order_index || index
            }));

            setCustomFields(customFieldsWithSection);
        } catch (error) {
            console.error('Error fetching custom fields:', error);
            setMessage({ type: 'error', text: 'Failed to load custom fields' });
        } finally {
            setLoading(false);
        }
    };

    const handleFieldChange = (fieldName, value) => {
        setFormData(prev => ({
            ...prev,
            [fieldName]: value
        }));
        
        // Clear error for this field when user starts typing
        if (errors[fieldName]) {
            setErrors(prev => ({
                ...prev,
                [fieldName]: ''
            }));
        }
    };

    const validateForm = () => {
        const newErrors = {};
        const allFields = [...standardFields, ...customFields];

        allFields.forEach(field => {
            if (field.required && !formData[field.field_name]) {
                newErrors[field.field_name] = `${field.name} is required`;
            }

            // Email validation
            if (field.field_type === 'email' && formData[field.field_name]) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(formData[field.field_name])) {
                    newErrors[field.field_name] = 'Invalid email address';
                }
            }

            // Phone validation (basic)
            if (field.field_type === 'tel' && formData[field.field_name]) {
                const phoneRegex = /^[\d\s\-\+\(\)]{7,}$/;
                if (!phoneRegex.test(formData[field.field_name])) {
                    newErrors[field.field_name] = 'Invalid phone number';
                }
            }

            // Date validation
            if (field.field_type === 'date' && formData[field.field_name]) {
                const date = new Date(formData[field.field_name]);
                if (isNaN(date.getTime())) {
                    newErrors[field.field_name] = 'Invalid date';
                }
            }

            // Number validation
            if (field.field_type === 'number' && formData[field.field_name]) {
                if (isNaN(formData[field.field_name])) {
                    newErrors[field.field_name] = 'Must be a number';
                }
            }
        });

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            setMessage({ type: 'error', text: 'Please fix the errors below' });
            return;
        }

        try {
            setSubmitting(true);
            const token = localStorage.getItem('token');

            const clientPayload = {
                name: formData.full_name,
                pepfar_id: formData.pepfar_id,
                facility_id: facilityId,
                pharmacy_id: pharmacyId,
                age: formData.date_of_birth ? calculateAge(formData.date_of_birth) : undefined,
                gender: formData.gender,
                phone: formData.phone_number,
                email: formData.email,
                address: formData.address,
                // Include custom fields
                ...Object.keys(formData).reduce((acc, key) => {
                    if (!standardFields.some(f => f.field_name === key)) {
                        acc[key] = formData[key];
                    }
                    return acc;
                }, {})
            };

            const response = await fetch('/api/clients', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(clientPayload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to create client');
            }

            setMessage({ type: 'success', text: 'Client created successfully!' });
            
            // Reset form
            setFormData({});
            setErrors({});

            // Call success callback after brief delay
            setTimeout(() => {
                onSuccess();
            }, 1500);

        } catch (error) {
            console.error('Error creating client:', error);
            setMessage({ type: 'error', text: error.message || 'Error creating client' });
        } finally {
            setSubmitting(false);
        }
    };

    const calculateAge = (dateString) => {
        const today = new Date();
        const birthDate = new Date(dateString);
        let age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        
        return age;
    };

    const groupedFields = {
        'Personal Information': standardFields,
        'Additional Information': customFields.filter(f => f.section === 'Additional Information'),
        'Medical History': customFields.filter(f => f.section === 'Medical History'),
        'Other': customFields.filter(f => !f.section || (f.section !== 'Additional Information' && f.section !== 'Medical History'))
    };

    const renderField = (field) => {
        const fieldKey = field.field_name;
        const value = formData[fieldKey] || '';
        const error = errors[fieldKey];

        return (
            <div key={fieldKey} className="form-group">
                <label htmlFor={fieldKey}>
                    {field.name}
                    {field.required && <span className="required">*</span>}
                </label>

                {field.field_type === 'text' && (
                    <input
                        type="text"
                        id={fieldKey}
                        value={value}
                        onChange={(e) => handleFieldChange(fieldKey, e.target.value)}
                        placeholder={`Enter ${field.name.toLowerCase()}`}
                        disabled={submitting}
                        className={error ? 'error' : ''}
                    />
                )}

                {field.field_type === 'email' && (
                    <input
                        type="email"
                        id={fieldKey}
                        value={value}
                        onChange={(e) => handleFieldChange(fieldKey, e.target.value)}
                        placeholder="name@example.com"
                        disabled={submitting}
                        className={error ? 'error' : ''}
                    />
                )}

                {field.field_type === 'tel' && (
                    <input
                        type="tel"
                        id={fieldKey}
                        value={value}
                        onChange={(e) => handleFieldChange(fieldKey, e.target.value)}
                        placeholder="Phone number"
                        disabled={submitting}
                        className={error ? 'error' : ''}
                    />
                )}

                {field.field_type === 'date' && (
                    <input
                        type="date"
                        id={fieldKey}
                        value={value}
                        onChange={(e) => handleFieldChange(fieldKey, e.target.value)}
                        disabled={submitting}
                        className={error ? 'error' : ''}
                    />
                )}

                {field.field_type === 'number' && (
                    <input
                        type="number"
                        id={fieldKey}
                        value={value}
                        onChange={(e) => handleFieldChange(fieldKey, e.target.value)}
                        placeholder="Enter number"
                        disabled={submitting}
                        className={error ? 'error' : ''}
                    />
                )}

                {field.field_type === 'select' && (
                    <select
                        id={fieldKey}
                        value={value}
                        onChange={(e) => handleFieldChange(fieldKey, e.target.value)}
                        disabled={submitting}
                        className={error ? 'error' : ''}
                    >
                        <option value="">Select {field.name.toLowerCase()}</option>
                        {field.options && field.options.map((option, idx) => (
                            <option key={idx} value={option}>{option}</option>
                        ))}
                    </select>
                )}

                {field.field_type === 'textarea' && (
                    <textarea
                        id={fieldKey}
                        value={value}
                        onChange={(e) => handleFieldChange(fieldKey, e.target.value)}
                        placeholder={`Enter ${field.name.toLowerCase()}`}
                        rows="4"
                        disabled={submitting}
                        className={error ? 'error' : ''}
                    />
                )}

                {error && <span className="error-message">{error}</span>}
            </div>
        );
    };

    if (loading) {
        return <div className="loading-spinner">Loading fields...</div>;
    }

    return (
        <form className="client-form" onSubmit={handleSubmit}>
            {message.text && (
                <div className={`message ${message.type}`}>
                    {message.text}
                </div>
            )}

            {Object.entries(groupedFields).map(([section, fields]) => (
                fields && fields.length > 0 && (
                    <div key={section} className="form-section">
                        <h3 className="section-title">{section}</h3>
                        <div className="fields-grid">
                            {fields
                                .sort((a, b) => (a.order || 999) - (b.order || 999))
                                .map(field => renderField(field))
                            }
                        </div>
                    </div>
                )
            ))}

            <div className="form-actions">
                <button
                    type="button"
                    className="btn-secondary"
                    onClick={onCancel}
                    disabled={submitting}
                >
                    Cancel
                </button>
                <button
                    type="submit"
                    className="btn-primary"
                    disabled={submitting}
                >
                    {submitting ? 'Creating...' : 'Create Client'}
                </button>
            </div>
        </form>
    );
};

export default ClientForm;
