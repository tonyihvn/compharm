import React, { useState, useEffect } from 'react';
import ClientForm from './ClientForm';
import './AddClientModal.css';

const AddClientModal = ({ isOpen, onClose, onClientAdded, facilityId, pharmacyId }) => {
    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Add New Client</h2>
                    <button className="close-button" onClick={onClose}>&times;</button>
                </div>
                <div className="modal-body">
                    <ClientForm 
                        onSuccess={() => {
                            onClientAdded();
                            onClose();
                        }}
                        onCancel={onClose}
                        facilityId={facilityId}
                        pharmacyId={pharmacyId}
                    />
                </div>
            </div>
        </div>
    );
};

export default AddClientModal;
