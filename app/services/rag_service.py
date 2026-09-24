from app.services.search_service import search_service
from app.services.llm_service import generate_answer


async def answer_question(
    question: str
):

    documents = await search_service.search(
        question=question,
        top_k=5
    )

    if not documents:

        return {
            "answer": "I could not find relevant information in the documents.",
            "sources": []
        }

    context_parts = []

    sources = []

    for document in documents:

        context_parts.append(
            document["content"]
        )

        if document.get("title"):
            sources.append(
                document["title"]
            )

    context = "\n\n---\n\n".join(
        context_parts
    )

    answer = await generate_answer(
        question=question,
        context=context
    )

    return {
        "answer": answer,
        "sources": list(set(sources))
    }