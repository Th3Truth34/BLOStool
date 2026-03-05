from fastapi import APIRouter

from app.api import auth, leads, contacts, activities, dashboard, scraping

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(leads.router)
api_router.include_router(contacts.router)
api_router.include_router(activities.router)
api_router.include_router(dashboard.router)
api_router.include_router(scraping.router)
