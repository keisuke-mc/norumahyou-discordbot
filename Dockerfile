# Koyebデプロイ用 Dockerfile
FROM python:3.11-slim

WORKDIR /app

# システムパッケージ更新
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Pythonパッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコピー
COPY main.py .
COPY server.py .
COPY run.py .

# ポート公開
EXPOSE 8000

# アプリケーション実行
CMD ["python", "run.py"]
