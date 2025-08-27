from fastapi import APIRouter, Request, HTTPException,Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import json, sys
import os
import django
from typing import Dict, List

router = APIRouter()

class VolumeBlock(BaseModel):
    volumes: Dict[str, str]  # numéro du volume → id du volume
    id_series: str           # id de la série

class PredictionRequest(BaseModel):
    user_age: int
    user_genre: str
    genre_preference: List[str]
    category_preference: List[str]
    user_comment: str
    prediction_type: str
    collection: Dict[str, VolumeBlock]
    read: Dict[str, VolumeBlock]
    csrfmiddlewaretoken:str


@router.post("/predict/")
async def predict(
    user_age: str = Form(...),
    user_genre: str = Form(...),
    genre_preference: str = Form(...),
    category_preference: str = Form(...),
    user_comment: str = Form(...),
    prediction_type: str = Form(...),
    collection: str = Form(""),
    read: str = Form(""),
    csrfmiddlewaretoken:  str = Form(""),
):
    try:
        collection_data = json.loads(collection) if collection else {}
        read_data = json.loads(read) if read else {}

        genre_pref = genre_preference.split(",")
        category_pref = category_preference.split(",")

    except json.JSONDecodeError as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"❌ JSON invalide: {str(e)}", "collection": collection, "read": read}
        )

    return {
        "user_age": user_age,
        "user_genre": user_genre,
        "genre_preference": genre_pref,
        "category_preference": category_pref,
        "user_comment": user_comment,
        "prediction_type": prediction_type,
        "collection": collection_data,
        "read": read_data,
        "message": "✅ JSON bien décodé"
    }