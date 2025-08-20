from fastapi import APIRouter, HTTPException
from api.schemas import PredictionRequest, DynamicPredictionRequest
from api.services.model_services import ModelService

router = APIRouter(
    prefix="/models",
    tags=["models"]
)

model_services = ModelService()

@router.post("/predict/book", summary="recommandation du prochain livre")
async def predict_lille(request: PredictionRequest):
    return model_services.get_predict_lille(request)