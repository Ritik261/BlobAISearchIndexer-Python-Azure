from azure.core.credentials import AzureKeyCredential

from azure.search.documents.indexes import SearchIndexerClient

from azure.search.documents.indexes.models import (
    SearchIndexerSkillset,
    SplitSkill,
    AzureOpenAIEmbeddingSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexerIndexProjection,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    IndexProjectionMode,
)

from app.core.config import settings


credential = AzureKeyCredential(
    settings.azure_search_admin_key
)


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