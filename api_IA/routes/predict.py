from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/predict")
def get_prediction():
    print("Requête reçue dans FastAPI")
    return JSONResponse(content={"prediction": "résultat fictif  depuis django"})


