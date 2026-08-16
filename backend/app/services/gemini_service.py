from google import genai
from google.genai import errors

from app.core.config import settings


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


def generate_answer(question, context):

    print("DEBUG CONTEXT:", context)
    print("DEBUG QUESTION:", question)

    prompt = f"""
You are DocPilot-AI, an AI document assistant.

Answer the user's question using ONLY the provided document context.

If the answer is not available in the context, say:
"I could not find this information in the uploaded document."

Document Context:
{context}

User Question:
{question}

Answer:
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        print("DEBUG GEMINI:", response.text)

        return response.text

    except errors.ClientError as error:

        if error.code == 429:

            print("DEBUG GEMINI QUOTA: Rate limit or quota exceeded")

            return (
                "AI service quota is temporarily exhausted. "
                "Please try again later."
            )

        print("DEBUG GEMINI ERROR:", error)

        return (
            "The AI service is temporarily unavailable. "
            "Please try again later."
        )

    except Exception as error:

        print("DEBUG GEMINI ERROR:", error)

        return (
            "Something went wrong while generating the AI response."
        )