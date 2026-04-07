from fastapi import FastAPI
from app.api.identify import router as identify_router

app = FastAPI(title="LookUp API", version="0.1.0")
app.include_router(identify_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
