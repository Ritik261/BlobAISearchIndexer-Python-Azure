from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient, SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataSourceConnection, 
    SearchIndexerDataSourceType,
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile, 
    SearchIndexerSkillset,
    SplitSkill,
    AzureOpenAIEmbeddingSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexerIndexProjection,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    IndexProjectionMode,   
    SearchIndexer,
    FieldMapping,
    )

from app.core.config import settings

credential = AzureKeyCredential(
    settings.azure_search_admin_key
)

# Create Datasource
def create_datasource():
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

# Create Index

def create_index():
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

# Create Skillset

def create_skillset():

    client = SearchIndexerClient(
    endpoint=settings.azure_search_endpoint,
    credential=credential
    )


    # ---------------------------------------------------------
    # 1. TEXT SPLIT SKILL
    # ---------------------------------------------------------

    split_skill = SplitSkill(

        name="split-text",

        description="Split PDF text into smaller chunks",

        text_split_mode="pages",

        maximum_page_length=2000,

        page_overlap_length=200,

        context="/document",

        inputs=[
            InputFieldMappingEntry(
                name="text",
                source="/document/content"
            )
        ],

        outputs=[
            OutputFieldMappingEntry(
                name="textItems",
                target_name="chunks"
            )
        ]
    )


    # ---------------------------------------------------------
    # 2. EMBEDDING SKILL
    # ---------------------------------------------------------

    embedding_skill = AzureOpenAIEmbeddingSkill(

        name="generate-embeddings",

        description="Generate embeddings for document chunks",

        resource_url=settings.azure_openai_endpoint,

        deployment_name=settings.azure_openai_embedding_deployment,

        model_name="text-embedding-3-small",

        dimensions=1536,

        api_key=settings.azure_openai_api_key,

        context="/document/chunks/*",

        inputs=[
            InputFieldMappingEntry(
                name="text",
                source="/document/chunks/*"
            )
        ],

        outputs=[
            OutputFieldMappingEntry(
                name="embedding",
                target_name="embedding"
            )
        ]
    )


    # ---------------------------------------------------------
    # 3. INDEX PROJECTION
    # ---------------------------------------------------------

    index_projection = SearchIndexerIndexProjection(

        selectors=[

            SearchIndexerIndexProjectionSelector(

                # Target search index
                target_index_name=settings.azure_search_index_name,

                # Parent document ID field
                parent_key_field_name="parent_id",

                # Every chunk becomes one search document
                source_context="/document/chunks/*",

                mappings=[

                    # Chunk text
                    InputFieldMappingEntry(
                        name="content",
                        source="/document/chunks/*"
                    ),

                    # Chunk embedding
                    InputFieldMappingEntry(
                        name="content_vector",
                        source="/document/chunks/*/embedding"
                    ),

                    # Original PDF filename
                    InputFieldMappingEntry(
                        name="title",
                        source="/document/metadata_storage_name"
                    ),

                    # Blob path
                    InputFieldMappingEntry(
                        name="filepath",
                        source="/document/metadata_storage_path"
                    ),

                    # Blob URL
                    InputFieldMappingEntry(
                        name="url",
                        source="/document/metadata_storage_path"
                    ),
                ]
            )
        ],

        parameters=SearchIndexerIndexProjectionsParameters(

            projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS

        )
    )


    # ---------------------------------------------------------
    # 4. CREATE SKILLSET
    # ---------------------------------------------------------

    skillset = SearchIndexerSkillset(

        name=settings.azure_search_skillset_name,

        description=(
            "PDF chunking and vectorization skillset"
        ),

        skills=[
            split_skill,
            embedding_skill
        ],

        index_projection=index_projection
    )


    client.create_or_update_skillset(
        skillset
    )


    print(
        f"Skillset '{settings.azure_search_skillset_name}' "
        "created successfully."
    )

def create_indexer():
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