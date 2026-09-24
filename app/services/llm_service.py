from openai import AsyncAzureOpenAI

from app.core.config import settings


client = AsyncAzureOpenAI(
    azure_endpoint=settings.azure_openai_endpoint,
    api_key=settings.azure_openai_api_key,
    api_version=settings.azure_openai_api_version
)


async def generate_answer(
    question: str,
    context: str
) -> str:

    response = await client.chat.completions.create(

        model=settings.azure_openai_chat_deployment,

        messages=[
            {
                "role": "system",
                "content": """
You are a document question-answering assistant.

Answer the user's question using only the provided
document context.

If the answer is not present in the context,
say that the information is not available in the
provided documents.

Do not invent information.
"""
            },

            {
                "role": "user",
                "content": f"""
Document context:

{context}

Question:

{question}
"""
            }
        ],

        temperature=1
    )

    return response.choices[0].message.content