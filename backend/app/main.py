from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import projects, regions, stats

app = FastAPI(title="SocFinder API", version="1.0.0")

# CORS настройки для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(projects.router, prefix="/api/v1")
app.include_router(regions.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "SocFinder API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


