from fastapi import APIRouter

from app.model.chat import (
    ChatRequest,
    ChatResponse
)

from app.services.rag_service import answer_question


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post(
    "",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest
):

    result = await answer_question(
        request.question
    )

    return result