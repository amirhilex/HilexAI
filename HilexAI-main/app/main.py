import os
from fastapi import FastAPI
from .adapters.api.routers.scrape import router as scrape_router
from .adapters.api.routers.queries import router as queries_router
from .config import init_models

def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI Hex Scraper", version="0.1.0")

    # Include routers
    app.include_router(scrape_router)
    app.include_router(queries_router)

    @app.on_event("startup")
    async def startup():
        await init_models()

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok"}

    return app

app = create_app()

