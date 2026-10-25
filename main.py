
from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="Klinik Queue API",
    description="REST API untuk sistem antrian klinik",
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "Klinik Queue API berjalan",
        "documentation": "/docs",
    }
