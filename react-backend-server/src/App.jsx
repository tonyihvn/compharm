import React, { useState, useEffect } from 'react';
import ClientsPage from './components/ClientsPage';
import './App.css';

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if user is authenticated
        const token = localStorage.getItem('token');
        if (token) {
            verifyToken(token);
        } else {
            setLoading(false);
        }
    }, []);

    const verifyToken = async (token) => {
        try {
            const response = await fetch('/api/auth/verify', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                setIsAuthenticated(true);
            } else {
                localStorage.removeItem('token');
                setIsAuthenticated(false);
            }
        } catch (error) {
            console.error('Token verification failed:', error);
            localStorage.removeItem('token');
            setIsAuthenticated(false);
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        setIsAuthenticated(false);
    };

    if (loading) {
        return (
            <div className="app loading">
                <div className="spinner"></div>
                <p>Loading...</p>
            </div>
        );
    }

    if (!isAuthenticated) {
        return (
            <div className="app login-required">
                <div className="login-container">
                    <h1>Authentication Required</h1>
                    <p>Please log in to access the Client Management System.</p>
                    <p><strong>Note:</strong> This dashboard requires a valid authentication token.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="app">
            <header className="app-header">
                <div className="header-content">
                    <h1>Pharmacy Client Management System</h1>
                    <button onClick={handleLogout} className="btn-logout">Logout</button>
                </div>
            </header>

            <main className="app-main">
                <ClientsPage />
            </main>

            <footer className="app-footer">
                <p>&copy; 2024 Pharmacy Management System. All rights reserved.</p>
            </footer>
        </div>
    );
}

export default App;
