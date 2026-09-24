from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (SearchIndexerDataSourceConnection, SearchIndexerDataSourceType)

from app.core.config import settings

credential = AzureKeyCredential(
    settings.azure_search_admin_key
)

client = SearchIndexerClient(
    endpoint=settings.azure_search_endpoint,
    credential=credential
)

data_source = SearchIndexerDataSourceConnection(
    name=settings.azure_search_datasource_name,
    type=SearchIndexerDataSourceType.AZURE_BLOB,
    connection_string=settings.azure_storage_connection_str,
    container={
        "name":settings.azure_storage_container
    }
)

client.create_or_update_data_source_connection(data_source)

print("Data Source Created Successfully")