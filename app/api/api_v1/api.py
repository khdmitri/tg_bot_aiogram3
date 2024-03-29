from fastapi import APIRouter

from app.api.api_v1.endpoints import practises, docs, web, ukassa_payment, blog

api_router = APIRouter()

api_router.include_router(practises.router, prefix="/practises", tags=["practises"])
api_router.include_router(docs.router, prefix="/document", tags=["document"])
api_router.include_router(web.router, prefix="/web", tags=["web"])
api_router.include_router(ukassa_payment.router, prefix="/payment", tags=["payment"])
api_router.include_router(blog.router, prefix="/blog", tags=["blog"])
