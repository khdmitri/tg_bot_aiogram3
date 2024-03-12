from fastapi import APIRouter

from app.api.api_v1.endpoints import practises, docs

api_router = APIRouter()

api_router.include_router(practises.router, prefix="/practises", tags=["practises"])
api_router.include_router(docs.router, prefix="/document", tags=["document"])
