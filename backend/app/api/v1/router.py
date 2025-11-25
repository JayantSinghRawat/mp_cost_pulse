from fastapi import APIRouter
from app.api.v1 import rents, groceries, transport, inflation, geospatial, auth, ml, recommendations, scraping

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(rents.router)
api_router.include_router(groceries.router)
api_router.include_router(transport.router)
api_router.include_router(inflation.router)
api_router.include_router(geospatial.router)
api_router.include_router(ml.router)
api_router.include_router(recommendations.router)
api_router.include_router(scraping.router)

