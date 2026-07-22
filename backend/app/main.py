from fastapi import FastAPI

from app.api import parks

app = FastAPI(
    title="DangShinNaGae API",
    description="반려견 맞춤 산책 공원 추천 API",
    version="1.0.0",
)

app.include_router(parks.router)
