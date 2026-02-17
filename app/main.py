from fastapi import FastAPI
from app.routes.analytics import router

app = FastAPI(title="Amazon Analytics API")

app.include_router(router)
