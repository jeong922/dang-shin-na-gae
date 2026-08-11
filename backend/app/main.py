import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import parks_map, parks, park, search_parks

load_dotenv()


app = FastAPI(
    title="DangShinNaGae API",
    description="반려견 맞춤 산책 공원 추천 API",
    version="1.0.0",
)


cors_origins = os.getenv("CORS_ORIGINS", "").split(",")


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(parks_map.router)
app.include_router(search_parks.router)

app.include_router(parks.router)
app.include_router(park.router)
