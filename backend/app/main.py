import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import park, parks, parks_map, search_parks

load_dotenv()


def get_cors_origins() -> list[str]:
    return [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]


app = FastAPI(
    title="DangShinNaGae API",
    description="반려견과 함께 산책할 수 있는 서울시 공원 정보 API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(parks_map.router)
app.include_router(search_parks.router)
app.include_router(parks.router)
app.include_router(park.router)
