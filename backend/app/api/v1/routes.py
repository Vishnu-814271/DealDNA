from fastapi import APIRouter

from app.api.v1.endpoints import agent, customers, deals, health, memory, recommendations

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(customers.router)
api_router.include_router(deals.router)
api_router.include_router(agent.router)
api_router.include_router(memory.router)
api_router.include_router(recommendations.router)
