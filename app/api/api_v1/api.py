from fastapi import APIRouter

from app.api.api_v1.endpoints import practises

api_router = APIRouter()

api_router.include_router(practises.router, prefix="/practises", tags=["practises"])
