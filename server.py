"""
FastAPI Webサーバー
Koyeb ヘルスチェック対応
"""
import asyncio
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# グローバル変数（Botインスタンスと同期するため）
app_state = {"bot_ready": False}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションの起動・シャットダウン処理"""
    print("FastAPI サーバー起動")
    app_state["bot_ready"] = True
    yield
    print("FastAPI サーバーシャットダウン")


# FastApp初期化
app = FastAPI(title="Discord Bot - Koyeb", lifespan=lifespan)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return JSONResponse({
        "status": "ok",
        "service": "Discord Bot - Quota Management System",
        "timestamp": datetime.now().isoformat()
    })


@app.get("/health")
async def health():
    """ヘルスチェックエンドポイント（Koyeb向け）"""
    return JSONResponse({
        "status": "healthy",
        "bot_ready": app_state["bot_ready"],
        "timestamp": datetime.now().isoformat()
    })


@app.get("/status")
async def status():
    """ステータスエンドポイント"""
    return JSONResponse({
        "status": "running",
        "bot_ready": app_state["bot_ready"],
        "uptime": "N/A",
        "timestamp": datetime.now().isoformat()
    })


@app.post("/health")
async def health_post():
    """POSTでのヘルスチェック"""
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    import uvicorn
    
    # ポート設定（Koyebは8000または8080推奨）
    port = int(os.getenv("PORT", 8000))
    
    # uvicorn起動
    uvicorn.run(app, host="0.0.0.0", port=port)
