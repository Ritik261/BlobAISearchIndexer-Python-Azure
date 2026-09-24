from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="question to ask uploaded docs"
    )

class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []