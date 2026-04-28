"""
Discord Bot - ノルマ管理システム
メインロジック実装
"""
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import aiohttp

# 環境変数の読み込み
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))
EDIT_ROLE_ID = int(os.getenv("EDIT_ROLE_ID", 0))
APP_URL = os.getenv("APP_URL", "http://localhost:8000")

# Intents設定
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

# Bot初期化
bot = commands.Bot(command_prefix="!", intents=intents)

# グローバル変数
quota_data = {
    "members": [
        {"name": "メンバーA", "quota": 100},
        {"name": "メンバーB", "quota": 80},
        {"name": "メンバーC", "quota": 120},
    ]
}
last_message_id = None


async def send_quota_embed():
    """ノルマ表をEmbed形式で送信"""
    global last_message_id
    
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"チャンネルID {CHANNEL_ID} が見つかりません")
        return

    # 既存のメッセージを削除
    if last_message_id:
        try:
            msg = await channel.fetch_message(last_message_id)
            await msg.delete()
        except (discord.NotFound, discord.Forbidden):
            pass

    # 新しいEmbed作成
    embed = discord.Embed(
        title="📊 ノルマ管理表",
        description="現在のノルマ状況です",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    # ノルマデータをフィールドとして追加
    for member in quota_data.get("members", []):
        name = member.get("name", "不明")
        quota = member.get("quota", 0)
        embed.add_field(
            name=name,
            value=f"**{quota}** ノルマ",
            inline=False
        )

    # フッター追加
    embed.set_footer(text="編集は /edit_quota コマンドを使用してください")

    # メッセージ送信
    msg = await channel.send(embed=embed)
    last_message_id = msg.id


@bot.event
async def on_ready():
    """Bot起動時の処理"""
    print(f"{bot.user} としてログインしました")
    try:
        synced = await bot.tree.sync()
        print(f"スラッシュコマンド {len(synced)} 件を同期しました")
    except Exception as e:
        print(f"コマンド同期エラー: {e}")
    
    # ノルマ表を初期送信
    await send_quota_embed()
    
    # 自己ポーリングタスク開始
    if not keep_alive.is_running():
        keep_alive.start()


@bot.tree.command(
    name="edit_quota",
    description="ノルマを編集します"
)
@discord.app_commands.describe(
    member_name="メンバー名",
    new_quota="新しいノルマ値（数字）"
)
async def edit_quota(interaction: discord.Interaction, member_name: str, new_quota: str):
    """ノルマ編集コマンド"""
    
    # 権限チェック
    edit_role = interaction.guild.get_role(EDIT_ROLE_ID)
    if not edit_role:
        await interaction.response.send_message(
            "❌ 編集ロールが見つかりません",
            ephemeral=True
        )
        return
    
    if edit_role not in interaction.user.roles:
        await interaction.response.send_message(
            "❌ このコマンドを実行する権限がありません",
            ephemeral=True
        )
        return

    # ノルマ値の検証
    try:
        quota_value = int(new_quota)
        if quota_value < 0:
            raise ValueError("ノルマ値は0以上である必要があります")
    except ValueError:
        await interaction.response.send_message(
            "❌ ノルマ値は正の整数である必要があります",
            ephemeral=True
        )
        return

    # メンバーを検索して更新
    found = False
    for member in quota_data.get("members", []):
        if member["name"].lower() == member_name.lower():
            old_quota = member["quota"]
            member["quota"] = quota_value
            found = True
            break

    if not found:
        await interaction.response.send_message(
            f"❌ メンバー '{member_name}' が見つかりません",
            ephemeral=True
        )
        return

    # 応答（エフェメラル）
    await interaction.response.send_message(
        f"✅ {member_name} のノルマを {old_quota} → {quota_value} に更新しました",
        ephemeral=True
    )

    # ノルマ表を再送信
    await send_quota_embed()


@bot.tree.command(
    name="add_member",
    description="新しいメンバーをノルマ表に追加します"
)
@discord.app_commands.describe(
    member_name="メンバー名",
    quota="ノルマ値（数字）"
)
async def add_member(interaction: discord.Interaction, member_name: str, quota: str):
    """メンバー追加コマンド"""
    
    # 権限チェック
    edit_role = interaction.guild.get_role(EDIT_ROLE_ID)
    if not edit_role or edit_role not in interaction.user.roles:
        await interaction.response.send_message(
            "❌ このコマンドを実行する権限がありません",
            ephemeral=True
        )
        return

    # ノルマ値の検証
    try:
        quota_value = int(quota)
        if quota_value < 0:
            raise ValueError
    except ValueError:
        await interaction.response.send_message(
            "❌ ノルマ値は正の整数である必要があります",
            ephemeral=True
        )
        return

    # メンバーが既に存在するか確認
    for member in quota_data.get("members", []):
        if member["name"].lower() == member_name.lower():
            await interaction.response.send_message(
                f"❌ メンバー '{member_name}' は既に存在します",
                ephemeral=True
            )
            return

    # メンバーを追加
    quota_data["members"].append({"name": member_name, "quota": quota_value})
    
    await interaction.response.send_message(
        f"✅ {member_name} をノルマ表に追加しました（ノルマ: {quota_value}）",
        ephemeral=True
    )

    # ノルマ表を再送信
    await send_quota_embed()


@bot.tree.command(
    name="remove_member",
    description="メンバーをノルマ表から削除します"
)
@discord.app_commands.describe(member_name="削除するメンバー名")
async def remove_member(interaction: discord.Interaction, member_name: str):
    """メンバー削除コマンド"""
    
    # 権限チェック
    edit_role = interaction.guild.get_role(EDIT_ROLE_ID)
    if not edit_role or edit_role not in interaction.user.roles:
        await interaction.response.send_message(
            "❌ このコマンドを実行する権限がありません",
            ephemeral=True
        )
        return

    # メンバーを検索して削除
    found = False
    for i, member in enumerate(quota_data.get("members", [])):
        if member["name"].lower() == member_name.lower():
            quota_data["members"].pop(i)
            found = True
            break

    if not found:
        await interaction.response.send_message(
            f"❌ メンバー '{member_name}' が見つかりません",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"✅ {member_name} をノルマ表から削除しました",
        ephemeral=True
    )

    # ノルマ表を再送信
    await send_quota_embed()


@tasks.loop(minutes=5)
async def keep_alive():
    """Koyeb無料プラン対策: 自己ポーリング"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{APP_URL}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    print(f"[{datetime.now()}] ヘルスチェック成功: {resp.status}")
                else:
                    print(f"[{datetime.now()}] ヘルスチェック警告: {resp.status}")
    except Exception as e:
        print(f"[{datetime.now()}] ポーリングエラー: {e}")


def run_bot():
    """Bot実行"""
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN 環境変数が設定されていません")
    if CHANNEL_ID == 0:
        raise ValueError("CHANNEL_ID 環境変数が設定されていません")
    if EDIT_ROLE_ID == 0:
        raise ValueError("EDIT_ROLE_ID 環境変数が設定されていません")
    
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    run_bot()
