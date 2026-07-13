# import pandas as pd
# import folium

# print("파이썬 환경 세팅 완료!")
# print(f"Pandas 버전: {pd.__version__}")


from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
