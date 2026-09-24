from azure.core.credentials import AzureKeyCredential

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)

from app.core.config import settings


credential = AzureKeyCredential(
    settings.azure_search_admin_key
)

client = SearchIndexClient(
    endpoint=settings.azure_search_endpoint,
    credential=credential
)


fields = [

    # Unique key for every chunk
    SearchField(
        name="chunk_id",
        type=SearchFieldDataType.String,
        key=True,
        filterable=True,
        searchable=True,
        # Index projections require the target index key to use the
        # keyword analyzer. This keeps the chunk ID as one exact token.
        analyzer_name="keyword"
    ),

    # Parent PDF/blob identifier
    SimpleField(
        name="parent_id",
        type=SearchFieldDataType.String,
        filterable=True
    ),

    # Chunk text
    SearchableField(
        name="content",
        type=SearchFieldDataType.String
    ),

    # PDF filename
    SearchableField(
        name="title",
        type=SearchFieldDataType.String,
        filterable=True
    ),

    # Blob path
    SimpleField(
        name="filepath",
        type=SearchFieldDataType.String,
        filterable=True
    ),

    # Blob URL
    SimpleField(
        name="url",
        type=SearchFieldDataType.String
    ),

    # Embedding vector
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(
            SearchFieldDataType.Single
        ),
        searchable=True,
        vector_search_dimensions=1536,
        vector_search_profile_name="vector-profile"
    )
]


vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(
            name="hnsw-config"
        )
    ],

    profiles=[
        VectorSearchProfile(
            name="vector-profile",
            algorithm_configuration_name="hnsw-config"
        )
    ]
)


index = SearchIndex(
    name=settings.azure_search_index_name,
    fields=fields,
    vector_search=vector_search
)


client.create_or_update_index(index)

print(
    f"Search index '{settings.azure_search_index_name}' "
    "created successfully."
)
