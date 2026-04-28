"""
Bot と Webサーバーを並行実行するエントリーポイント
"""
import asyncio
import os
import sys
from threading import Thread
import uvicorn
from main import bot, DISCORD_TOKEN


def run_server():
    """FastAPIサーバーをスレッド内で実行"""
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )


def run_bot():
    """Discord Botを実行"""
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"Botエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # FastAPIサーバーをバックグラウンドスレッドで実行
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    print("FastAPI サーバーを起動しました...")
    
    # メインスレッドでBotを実行
    print("Discord Bot を起動しています...")
    run_bot()
