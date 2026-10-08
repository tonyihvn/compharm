import { useState, useCallback } from 'react';

/**
 * Custom hook for making API calls with authentication
 * @param {string} url - The API endpoint URL
 * @returns {Object} - { data, loading, error, execute }
 */
export const useApi = (url) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const execute = useCallback(async (options = {}) => {
        try {
            setLoading(true);
            setError(null);

            const token = localStorage.getItem('token');
            const response = await fetch(url, {
                method: options.method || 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                body: options.body ? JSON.stringify(options.body) : undefined
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP ${response.status}`);
            }

            const result = await response.json();
            setData(result);
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [url]);

    return { data, loading, error, execute };
};

/**
 * Custom hook for fetching custom fields
 * @returns {Object} - { fields, loading, error, refetch }
 */
export const useCustomFields = () => {
    const [fields, setFields] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const refetch = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

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
            setFields(data.fields || []);
        } catch (err) {
            setError(err.message);
            console.error('Error fetching custom fields:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    // Fetch on mount
    useCallback(() => {
        refetch();
    }, [refetch])();

    return { fields, loading, error, refetch };
};

/**
 * Custom hook for managing form state
 * @param {Object} initialValues - Initial form values
 * @returns {Object} - { values, errors, setFieldValue, setFieldError, resetForm }
 */
export const useForm = (initialValues = {}) => {
    const [values, setValues] = useState(initialValues);
    const [errors, setErrors] = useState({});

    const setFieldValue = useCallback((field, value) => {
        setValues(prev => ({
            ...prev,
            [field]: value
        }));
        // Clear error when field is modified
        if (errors[field]) {
            setErrors(prev => ({
                ...prev,
                [field]: ''
            }));
        }
    }, [errors]);

    const setFieldError = useCallback((field, error) => {
        setErrors(prev => ({
            ...prev,
            [field]: error
        }));
    }, []);

    const setErrors_ = useCallback((newErrors) => {
        setErrors(newErrors);
    }, []);

    const resetForm = useCallback(() => {
        setValues(initialValues);
        setErrors({});
    }, [initialValues]);

    return {
        values,
        errors,
        setFieldValue,
        setFieldError,
        setErrors: setErrors_,
        resetForm
    };
};

/**
 * Custom hook for creating clients
 * @returns {Object} - { createClient, loading, error }
 */
export const useCreateClient = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const createClient = useCallback(async (clientData) => {
        try {
            setLoading(true);
            setError(null);

            const token = localStorage.getItem('token');
            const response = await fetch('/api/clients', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(clientData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to create client');
            }

            return await response.json();
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    return { createClient, loading, error };
};

/**
 * Field validation utilities
 */
export const fieldValidation = {
    isEmail: (value) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(value);
    },

    isPhone: (value) => {
        const phoneRegex = /^[\d\s\-\+\(\)]{7,}$/;
        return phoneRegex.test(value);
    },

    isDate: (value) => {
        const date = new Date(value);
        return !isNaN(date.getTime());
    },

    isNumber: (value) => {
        return !isNaN(parseFloat(value)) && isFinite(value);
    },

    required: (value) => {
        return value && value.toString().trim().length > 0;
    }
};

/**
 * Validate a field based on its type and rules
 * @param {Object} field - Field configuration
 * @param {*} value - Field value
 * @returns {string} - Error message or empty string
 */
export const validateField = (field, value) => {
    if (field.required && !fieldValidation.required(value)) {
        return `${field.name} is required`;
    }

    if (!value) return ''; // Skip type validation if empty and not required

    switch (field.field_type) {
        case 'email':
            if (!fieldValidation.isEmail(value)) {
                return 'Invalid email address';
            }
            break;
        case 'tel':
            if (!fieldValidation.isPhone(value)) {
                return 'Invalid phone number';
            }
            break;
        case 'date':
            if (!fieldValidation.isDate(value)) {
                return 'Invalid date';
            }
            break;
        case 'number':
            if (!fieldValidation.isNumber(value)) {
                return 'Must be a number';
            }
            break;
        default:
            break;
    }

    return '';
};
