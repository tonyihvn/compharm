import React, { useState, useEffect } from 'react';
import AddClientModal from '../components/AddClientModal';
import './ClientsPage.css';

const ClientsPage = () => {
    const [clients, setClients] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showAddModal, setShowAddModal] = useState(false);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [facilityId, setFacilityId] = useState('');
    const [pharmacyId, setPharmacyId] = useState('');
    const [facilities, setFacilities] = useState([]);
    const [pharmacies, setPharmacies] = useState([]);

    useEffect(() => {
        fetchFacilities();
        fetchPharmacies();
        if (facilityId || pharmacyId) {
            fetchClients();
        }
    }, [page, facilityId, pharmacyId]);

    const fetchFacilities = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/facilities', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setFacilities(data.facilities || []);
            }
        } catch (error) {
            console.error('Error fetching facilities:', error);
        }
    };

    const fetchPharmacies = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/pharmacies', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setPharmacies(data.pharmacies || []);
            }
        } catch (error) {
            console.error('Error fetching pharmacies:', error);
        }
    };

    const fetchClients = async () => {
        try {
            setLoading(true);
            setError(null);
            const token = localStorage.getItem('token');

            let url = `/api/clients?page=${page}&limit=20`;
            if (facilityId) url += `&facilityId=${facilityId}`;
            if (pharmacyId) url += `&pharmacyId=${pharmacyId}`;

            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch clients');
            }

            const data = await response.json();
            setClients(data.clients || []);
            setTotalPages(data.pages || 1);
        } catch (err) {
            setError(err.message || 'Error loading clients');
            console.error('Error fetching clients:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleClientAdded = () => {
        setPage(1);
        fetchClients();
    };

    return (
        <div className="clients-page">
            <div className="page-header">
                <h1>Manage Clients</h1>
                <button
                    className="btn-add-client"
                    onClick={() => setShowAddModal(true)}
                    disabled={!facilityId || !pharmacyId}
                    title={!facilityId || !pharmacyId ? 'Select facility and pharmacy first' : 'Add new client'}
                >
                    + Add Client
                </button>
            </div>

            <div className="filters-section">
                <div className="filter-group">
                    <label htmlFor="facility-select">Facility:</label>
                    <select
                        id="facility-select"
                        value={facilityId}
                        onChange={(e) => {
                            setFacilityId(e.target.value);
                            setPage(1);
                        }}
                    >
                        <option value="">Select a facility</option>
                        {facilities.map(facility => (
                            <option key={facility.id} value={facility.id}>
                                {facility.facility_name} ({facility.facility_code})
                            </option>
                        ))}
                    </select>
                </div>

                <div className="filter-group">
                    <label htmlFor="pharmacy-select">Pharmacy:</label>
                    <select
                        id="pharmacy-select"
                        value={pharmacyId}
                        onChange={(e) => {
                            setPharmacyId(e.target.value);
                            setPage(1);
                        }}
                    >
                        <option value="">Select a pharmacy</option>
                        {pharmacies.map(pharmacy => (
                            <option key={pharmacy.id} value={pharmacy.id}>
                                {pharmacy.pharmacy_name} ({pharmacy.pharmacy_code})
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}

            {loading ? (
                <div className="loading">Loading clients...</div>
            ) : clients.length === 0 ? (
                <div className="empty-state">
                    <p>No clients found. {!facilityId || !pharmacyId ? 'Select a facility and pharmacy to view clients.' : 'Click "Add Client" to create one.'}</p>
                </div>
            ) : (
                <>
                    <div className="clients-table-container">
                        <table className="clients-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>PEPFAR ID</th>
                                    <th>Phone</th>
                                    <th>Email</th>
                                    <th>Age</th>
                                    <th>Gender</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {clients.map(client => (
                                    <tr key={client.id}>
                                        <td>{client.name}</td>
                                        <td className="pepfar-id">{client.pepfarId}</td>
                                        <td>{client.phone || '-'}</td>
                                        <td>{client.email || '-'}</td>
                                        <td>{client.age || '-'}</td>
                                        <td>{client.gender || '-'}</td>
                                        <td className="actions">
                                            <button className="btn-view" title="View details">View</button>
                                            <button className="btn-edit" title="Edit client">Edit</button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {totalPages > 1 && (
                        <div className="pagination">
                            <button
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                                className="btn-pagination"
                            >
                                ← Previous
                            </button>
                            <span className="page-info">
                                Page {page} of {totalPages}
                            </span>
                            <button
                                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                                disabled={page === totalPages}
                                className="btn-pagination"
                            >
                                Next →
                            </button>
                        </div>
                    )}
                </>
            )}

            <AddClientModal
                isOpen={showAddModal}
                onClose={() => setShowAddModal(false)}
                onClientAdded={handleClientAdded}
                facilityId={facilityId}
                pharmacyId={pharmacyId}
            />
        </div>
    );
};

export default ClientsPage;
