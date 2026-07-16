# 가볍고 표준적인 파이썬 3.10 버전을 베이스로 사용합니다.
FROM python:3.10-slim

# TA-Lib 컴파일을 위한 C/C++ 빌드 도구와 wget을 설치합니다.
RUN apt-get update && \
    apt-get install -y build-essential wget && \
    rm -rf /var/lib/apt/lists/*

# TA-Lib 소스 다운로드 및 컴파일 (이미지 안에 영구 내장됨)
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && make install && \
    cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# 작업 디렉토리 설정
WORKDIR /app

# 파이썬 패키지 먼저 복사 및 설치 (캐시 활용을 위해 분리)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 봇의 나머지 모든 소스코드 복사
COPY . .

# 차트 이미지가 저장될 resource 폴더 생성
RUN mkdir -p resource

# 실행 명령어 (이전에 언급하신 bitgetboy.py 혹은 myramid.py 등 실제 구동 파일명으로 맞춰주세요)
CMD ["python3", "myramid.py"]