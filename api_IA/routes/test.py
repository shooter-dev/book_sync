from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/test")
def get_test(user_age: int, user_genre: str, genre_preference: str, category_preference: str):
    print("✅ Requête reçue dans /test")
    return JSONResponse(content={
        "message": "Requête reçue avec succès",
        "user_age": user_age,
        "user_genre": user_genre,
        "genre_preference": genre_preference,
        "category_preference": category_preference
    })