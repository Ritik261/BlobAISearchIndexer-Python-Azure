from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.aio import SearchIndexerClient

from app.core.config import settings


search_indexer_client = SearchIndexerClient(
    endpoint=settings.azure_search_endpoint,
    credential=AzureKeyCredential(
        settings.azure_search_admin_key
    )
)