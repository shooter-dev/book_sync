from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import FastAPI
from pydantic import BaseModel
from vectorizer import encode_text
from retriever import retrieve_similar_documents
from agent import ask_openai

class QuestionRequest(BaseModel):
    question: str
router = APIRouter()

@app.post("/predict")
def predict(payload: QuestionRequest):
    embedding = encode_text(payload.question)
    docs = retrieve_similar_documents(embedding)
    contents = [doc.content for doc in docs]
    answer = ask_openai(payload.question, contents)
    return {"answer": answer}


