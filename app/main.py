from fastapi import FastAPI

from app.api.upload import router as upload_router
from app.api.chat import router as chat_router
from app.services.aisearchConfig import create_datasource, create_index, create_indexer, create_skillset
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.core.exceptions import ResourceNotFoundError
from app.core.config import settings

credentials = AzureKeyCredential(
    settings.azure_search_admin_key
)

client = SearchIndexerClient(
    endpoint=settings.azure_search_endpoint,
    credential=credentials
)
indexerName = settings.azure_search_indexer_name
try:
    indexer = client.get_indexer(indexerName)
    print(f"Idexer found , {indexer.name}")

except ResourceNotFoundError:
    print("Indexer not found , creating azure ai search resources")
    create_index()
    create_datasource()
    create_skillset()
    create_indexer() 
    print("Resource created successfully") 

app = FastAPI(
    title="Azure Document RAG API",
    version="1.0.0"
)


app.include_router(
    upload_router
)

app.include_router(
    chat_router
)


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }