import os
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)


def ask_ai(question):

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful NEET preparation tutor. "
                    "Explain concepts clearly in simple Hinglish. "
                    "Focus on Physics, Chemistry and Biology. "
                    "Do not invent PYQs or claim an unverified question "
                    "is an official NEET PYQ."
                )
            },
            {
                "role": "user",
                "content": question
            }
        ],
        temperature=0.4,
        max_tokens=700
    )

    return response.choices[0].message.content
