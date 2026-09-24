from azure.storage.blob.aio import BlobServiceClient
from app.core.config import settings

class BlobService:
    def __init__(self):
        self.client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_str
        )
        self.container_client = self.client.get_container_client(
            settings.azure_storage_container
        )
    async def upload_pdf(
            self,
            filename: str,
            content: bytes
    ) -> str:
        blob_client = self.container_client.get_blob_client(filename)  
        await blob_client.upload_blob(
            content,
            overwrite=True
        )

        return blob_client.url
    
    async def close(self):
        await self.client.close()
        
blob_service = BlobService()