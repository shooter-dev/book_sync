from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import json, sys
import os
import django
from typing import Dict, List

router = APIRouter()

class PredictionRequest(BaseModel):
    user_id: str
    user_age: int
    user_genre: str
    genre_preference: str
    category_preference: str
    user_comment: str
    prediction_type: str
    collection:str
    read:str



@router.get("/predict/result", response_class=JSONResponse)
async def show_result(request: Request):
    params = dict(request.query_params)

    # Nettoyage des listes encodées en chaînes
    genre_pref = params.get("genre_preference", "").split(",")
    category_pref = params.get("category_preference", "").split(",")


    result = {
        "user_id": params.get("user_id", None),
        "user_age": params.get("user_age", None),
        "user_genre": params.get("user_genre", None),
        "genre_preference": genre_pref,
        "category_preference": category_pref,
        "user_comment": params.get("user_comment", None),
        "prediction_type": params.get("prediction_type", None),
        "collection":params.get("collection", None),
        "read":params.get("read", None),
        "message": "✅ Prédiction reçue"
    }

    return JSONResponse(content=result)


    # @router.post("/predict")
    # async def predict(data: PredictionRequest):
    #     return {"message": "Prédiction reçue", "data": data.dict()}
    # genre_list=["homme","femme","nonbinaire"]
    # user_age = request.query_params.get("user_age")
    # user_genre = request.query_params.get("user_genre")
    # genre_preference = request.query_params.get("genre_preference")
    # category_preference = request.query_params.get("category_preference")
    #
    # if not isinstance(user_age, int):
    #     user_age=int(user_age)
    #
    # user_genre=user_genre.lower().strip()
    # if user_genre not in genre_list:
    #     raise HTTPException(status_code=422, detail="Item format error for genre")
    #
    # genre_preference:list=genre_preference.replace(" ", "").split(",")
    #
    # category_preference:list = category_preference.replace(" ", "").split(",")
    #
    # data = {
    #     "user_age": user_age,
    #     "user_genre": user_genre,
    #     "genre_preference": list(genre_preference),
    #     "category_preference": list(category_preference),
    # }
    #
    # return JSONResponse(content={"prediction":data})
