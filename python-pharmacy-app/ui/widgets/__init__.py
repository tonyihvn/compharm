"""UI widgets package - Re-exports from parent ui module."""

from ..clients_view import ClientsListView
from ..client_details_view import ClientDetailsView
from ..client_full_details_view import ClientDetailsView as EnhancedClientDetailsView
from ..form_view import FormView
from ..admin_panel import AdminPanel
from .sync_worker import SyncWorker
from .enhanced_client_list import EnhancedClientListView

# Compatibility aliases
ClientListView = ClientsListView
ClientDetailView = ClientDetailsView
FormViewer = FormView

__all__ = [
    'ClientListView',
    'ClientsListView',
    'ClientDetailView',
    'ClientDetailsView',
    'EnhancedClientDetailsView',
    'EnhancedClientListView',
    'FormViewer',
    'FormView',
    'AdminPanel',
    'SyncWorker',
]
