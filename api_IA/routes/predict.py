from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json

router = APIRouter()


@router.get("/predict")
def get_prediction(request: Request):
    data={}
    genre_list=["homme","femme","nonbinaire"]
    user_age = request.query_params.get("user_age")
    user_genre = request.query_params.get("user_genre")
    genre_preference = request.query_params.get("genre_preference")
    category_preference = request.query_params.get("category_preference")

    if not isinstance(user_age, int):
        user_age=int(user_age)

    user_genre=user_genre.lower().strip()
    if user_genre not in genre_list:
        raise HTTPException(status_code=422, detail="Item format error for genre")

    genre_preference:list=genre_preference.replace(" ", "").split(",")

    category_preference:list = category_preference.replace(" ", "").split(",")

    data = {
        "user_age": user_age,
        "user_genre": user_genre,
        "genre_preference": list(genre_preference),
        "category_preference": list(category_preference),
    }

    return JSONResponse(content={"prediction":data})
