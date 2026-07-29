from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import parks_map

app = FastAPI(
    title="DangShinNaGae API",
    description="반려견 맞춤 산책 공원 추천 API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parks_map.router)
