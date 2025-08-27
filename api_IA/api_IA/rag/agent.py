import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from typing import List

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2023-07-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def ask_openai(question: str, documents: List[str]) -> str:
    context = "\n\n".join(documents)
    prompt = f"""
Tu es un expert en BD. Voici des extraits :
{context}

Question : {question}
Réponds de manière claire et précise.
"""

    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content
