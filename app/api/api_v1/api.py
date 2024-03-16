from fastapi import APIRouter

from app.api.api_v1.endpoints import practises, docs, web

api_router = APIRouter()

api_router.include_router(practises.router, prefix="/practises", tags=["practises"])
api_router.include_router(docs.router, prefix="/document", tags=["document"])
api_router.include_router(web.router, prefix="/web", tags=["web"])
