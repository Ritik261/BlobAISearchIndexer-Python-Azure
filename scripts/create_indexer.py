from azure.core.credentials import AzureKeyCredential

from azure.search.documents.indexes import SearchIndexerClient

from azure.search.documents.indexes.models import (
    SearchIndexer,
    FieldMapping,
)

from app.core.config import settings


credential = AzureKeyCredential(
    settings.azure_search_admin_key
)


client = SearchIndexerClient(
    endpoint=settings.azure_search_endpoint,
    credential=credential
)


indexer = SearchIndexer(

    name=settings.azure_search_indexer_name,
    data_source_name=settings.azure_search_datasource_name,
    target_index_name=settings.azure_search_index_name,
    skillset_name=settings.azure_search_skillset_name,
    field_mappings=[
        # Blob filename → title
        FieldMapping(
            source_field_name="metadata_storage_name",
            target_field_name="title"
        ),

        # Blob path → filepath
        FieldMapping(
            source_field_name="metadata_storage_path",
            target_field_name="filepath"
        )
    ]
)


client.create_or_update_indexer(
    indexer
)


print(
    f"Indexer '{settings.azure_search_indexer_name}' "
    "created successfully."
)