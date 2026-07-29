import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import parks_map

load_dotenv()


app = FastAPI(
    title="DangShinNaGae API",
    description="반려견 맞춤 산책 공원 추천 API",
    version="1.0.0",
)


cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173",
).split(",")


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(parks_map.router)
