from fastapi import FastAPI
from app.routes.dashboard import router as dashboard_router

app = FastAPI()

app.include_router(dashboard_router)
