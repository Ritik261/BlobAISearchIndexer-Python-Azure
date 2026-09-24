from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.blob_service import blob_service
from app.services.indexer_start import search_indexer_client
from app.core.config import settings

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

@router.post("/upload")
async def upload_documents(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF's are supported"
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Empty File"
        )  
    blob_url = await blob_service.upload_pdf(
        filename=file.filename,
        content=content
    )

    await search_indexer_client.run_indexer(
        settings.azure_search_indexer_name
    )

    return {
        "message":"PDF Upload Success",
        "filename": file.filename,
        "blob_url": blob_url
    }