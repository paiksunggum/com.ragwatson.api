# 1. 파이썬 기본 이미지 선택
FROM python:3.13-slim

# 2. 컨테이너 내부 작업 디렉토리 설정
WORKDIR /app

# 3. LightGBM / XGBoost 가 필요로 하는 OpenMP 런타임 + OpenCV(YOLO)가 필요로 하는 라이브러리 설치
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# 4. 종속성 파일 복사 및 설치
COPY requirements.txt .
RUN python -m venv /venv && /venv/bin/pip install --no-cache-dir -r requirements.txt

# 4. 나머지 소스 코드 복사
COPY . .

ENV PATH="/venv/bin:$PATH"
ENV ENABLE_API_DOCS=1
CMD ["sh", "-c", "python apps/vision2/tests/yolo_tsets.py; exec uvicorn main:app --host 0.0.0.0 --port 8000"]
