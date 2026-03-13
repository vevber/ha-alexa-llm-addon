from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

class Question(BaseModel):
    question: str

@app.post("/ask")
async def ask(q: Question):

    prompt = f"Beantworte kurz und verständlich: {q.question}"

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response["choices"][0]["message"]["content"]

    return {"answer": answer}