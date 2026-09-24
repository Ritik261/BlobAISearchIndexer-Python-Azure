from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Blob Storage
    azure_storage_connection_str: str
    azure_storage_container: str

    # Azure AI Search
    azure_search_endpoint: str
    azure_search_admin_key : str

    azure_search_index_name: str = "documents-index"
    azure_search_datasource_name: str = "documents-datasource"
    azure_search_indexer_name: str = "documents-indexer"
    azure_search_skillset_name: str = "documents-skillset"

    #Azure OpenAI

    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_api_version: str

    azure_openai_chat_deployment: str
    azure_openai_embedding_deployment: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive= False
    )
settings = Settings()