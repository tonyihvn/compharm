"""
UI Package
"""
from .login_window import LoginWindow
from .clients_view import ClientsListView
from .client_details_view import ClientDetailsView
from .form_view import FormView
from .admin_panel import AdminPanel

__all__ = [
    "LoginWindow",
    "ClientsListView", 
    "ClientDetailsView",
    "FormView",
    "AdminPanel"
]
