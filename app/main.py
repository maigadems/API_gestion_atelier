from fastapi import FastAPI

from app.routers import clients

app = FastAPI(title="API Atelier de couture")

app.include_router(clients.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
