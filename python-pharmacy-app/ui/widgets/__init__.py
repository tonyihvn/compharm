"""UI widgets package - Re-exports from parent ui module."""

from ..clients_view import ClientsListView
from ..client_details_view import ClientDetailsView
from ..form_view import FormView
from ..admin_panel import AdminPanel
from .sync_worker import SyncWorker

# Compatibility aliases
ClientListView = ClientsListView
ClientDetailView = ClientDetailsView
FormViewer = FormView

__all__ = [
    'ClientListView',
    'ClientsListView',
    'ClientDetailView',
    'ClientDetailsView',
    'FormViewer',
    'FormView',
    'AdminPanel',
    'SyncWorker',
]
