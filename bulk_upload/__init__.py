# Bulk Upload Package
# This package contains all bulk upload functionality for the Sunrise Education Centre

from .routes import bulk_upload_bp
from .bulk_upload_handler import BulkUploadHandler

bulk_upload_handler = BulkUploadHandler()
bulk_upload_handler.create_queries_table()

__all__ = ['bulk_upload_bp', 'BulkUploadHandler'] 