from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient

from app.core.config import settings


class SearchService:

    def __init__(self):

        self.client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index_name,
            credential=AzureKeyCredential(
                settings.azure_search_admin_key
            )
        )

    async def search(
        self,
        question: str,
        top_k: int = 5
    ):

        results = await self.client.search(
            search_text=question,
            top=top_k
        )

        documents = []

        async for result in results:

            documents.append({
                "content": result.get("content", ""),
                "title": result.get("title"),
                "filepath": result.get("filepath")
            })

        return documents

    async def close(self):
        await self.client.close()


search_service = SearchService()