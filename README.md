# 🐶 댕 신나개

반려동물과 함께 산책할 수 있는 서울시 공원 정보를 제공하고, 공원의 면적·고도·경사도 등을 기반으로 산책 난이도를 제공하는 지도 서비스

## 🚀 배포

### [Frontend - Vercel](https://dang-shin-na-gae.vercel.app)

### [Backend - Render](https://dang-shin-na-gae-api.onrender.com)

## ▶️ 실행 방법

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
python -m venv venv
pip install -r requirements.txt

cd backend
fastapi dev
```

## ⚙️ 기술

### Frontend

![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white)
![React Router](https://img.shields.io/badge/React_Router-CA4245?logo=reactrouter&logoColor=white)
![TanStack Query](https://img.shields.io/badge/TanStack_Query-FF4154?logo=reactquery&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss&logoColor=white)
![Motion](https://img.shields.io/badge/Motion-FFF312?logo=framer&logoColor=black)
![MapLibre GL JS](https://img.shields.io/badge/MapLibre_GL_JS-396CB2?logo=maplibre&logoColor=white)

### Backend

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)

### Data & Geospatial

![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-139C5A?logo=geopandas&logoColor=white)
![Shapely](https://img.shields.io/badge/Shapely-3A76AF?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white)

### Deployment

![Vercel](https://img.shields.io/badge/Vercel-000000?logo=vercel&logoColor=white)
![Render](https://img.shields.io/badge/Render-000000?logo=render&logoColor=white)

## 💡 기획 배경

공공데이터를 직접 수집·가공하고 지도 위에 시각화하는 과정을 경험하기 위해 시작한 프로젝트이다. 서울시 공원 데이터와 공간 데이터를 전처리하고, 지도에 공원 위치와 정보를 표시하며 데이터 분석이 필요한 과정은 Python 기반의 백엔드와 데이터 처리 파이프라인으로 구현했다.

처음에는 대형견을 위한 산책 공원 추천 서비스를 기획했지만, 실제 데이터를 조사하면서 반려견 출입 여부를 명확하게 확인할 수 있는 공원이 제한적이라는 점을 확인했다. 이에 특정 견종이나 크기에 한정하지 않고, 반려동물과 산책할 공원을 찾는 데 도움이 되는 서비스로 범위를 확장했다.

## 📂 프로젝트 구조

```text
dang-shin-na-gae/
├── frontend/                    # React 기반 프론트엔드
├── backend/
│   └── app/                     # FastAPI 애플리케이션
│
├── scripts/                     # 데이터 처리 및 분석 스크립트
│   ├── pipeline/                # 공간 데이터 매칭·가공 파이프라인
│   ├── analysis/                # 데이터 분석 및 검증
│   ├── archive/                 # 이전 분석·처리 스크립트
│   ├── calculate_difficulty.py  # 산책 난이도 산정
│   ├── calculate_elevation.py   # 고도·경사 데이터 생성
│   ├── calculate_pet_status.py  # 반려동물 관련 데이터 가공
│   └── preprocess.py            # 서울시 공원 데이터 전처리
│
├── data/
│   ├── raw/                     # 원본 데이터
│   ├── processed/               # 전처리·공간정보 가공 데이터
│   └── features/                # 고도·난이도 등 파생 데이터
│
└── requirements.txt             # Python 의존성
```

## 📜 설계

### ⚙️ 기능 목록

### 🏗️ 시스템 구조

### 📃 API 문서

FastAPI에서 제공하는 Swagger UI를 통해 API 명세를 확인하고 직접 요청을 테스트할 수 있다.

### [Swagger UI](https://dang-shin-na-gae-api.onrender.com/docs)

## 🗺️ 데이터 구축

### 공원 데이터 수집 및 전처리

### 공원 Polygon 매칭

### 공원 면적 산정

### 고도 데이터 수집

### 산책 난이도 산정

## 🖥️ 화면 및 기능

### 지도

### 공원 검색

### 공원 필터

### 공원 목록

### 공원 상세

## 🛠️ 성능 최적화 및 문제 해결

### 1. 지도 마커 렌더링 최적화

### 2. 공원 Polygon 매칭

### 3. 공원 데이터 정제 및 보정

### 4. 검색 및 필터링 최적화

### 데이터 검증

## 📚 데이터 출처

### 서울시 공공데이터

- **서울시 주요 공원현황**
  - 서울시 공원의 기본 정보, 위치, 면적, 주요 시설 등의 데이터로 활용
  - 제공: 서울특별시 · 서울열린데이터광장
  - 공공누리 제1유형

- **서울시 생활권계획 시설(공원) 공간정보**
  - 공원 경계 Polygon 구축을 위한 공간정보로 활용
  - 제공: 서울특별시 · 서울열린데이터광장
  - 공공누리 제1유형

### OpenStreetMap

- 서울시 공간정보만으로 적절한 공원 경계를 구성하기 어려운 일부 공원의 Polygon 보완 및 대체에 활용
- © OpenStreetMap contributors
- Open Database License (ODbL)

### Google Maps Platform

- **Elevation API**
  - 공원 주변 표본 지점의 고도 데이터를 수집하고 고도차 및 평균 경사도를 계산하는 데 활용
