# Discord Bot - ノルマ管理システム

ノルマ表を特定のDiscordチャンネルに表示し、権限を持つユーザーが即座に更新できるBotです。

## 🎯 主な機能

- **ノルマ表の表示**: Embed形式で見やすくノルマを表示
- **編集機能**: スラッシュコマンドで即座にノルマを更新（古いメッセージは自動削除）
- **権限管理**: ロールベースのアクセス制御
  - **閲覧制限**: 指定ロール保有者のみ表示
  - **編集制限**: 別の編集ロールのみコマンド実行可能
- **Koyeb 24時間稼働対応**:
  - FastAPI + Uvicorn でWebサーバー並行実行
  - 自動ポーリングによるスリープ防止

## 📋 必要な環境

- **Python**: 3.8以上
- **Discord**: アプリケーション/ボットの作成済み
- **Koyeb**: デプロイ先（無料プランでもOK）
- **GitHub**: ソースコード管理・CI/CD連携用

## ⚙️ セットアップ

### 1. ローカル環境での実行

```bash
# リポジトリクローン
git clone https://github.com/your-username/discordbot.git
cd discordbot

# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .env ファイルを編集して実際の値を入力

# サーバーの起動
python run.py
```

### 2. 環境変数の設定

`.env` ファイルに以下を設定してください：

```
DISCORD_TOKEN=your_bot_token_here
CHANNEL_ID=123456789
EDIT_ROLE_ID=987654321
APP_URL=http://localhost:8000
```

| 変数 | 説明 |
|------|------|
| `DISCORD_TOKEN` | Discord Developer Portal から取得したBot トークン |
| `CHANNEL_ID` | ノルマ表を表示するチャンネルID |
| `EDIT_ROLE_ID` | コマンド実行権限を持つロールID |
| `APP_URL` | Koyebデプロイ後のアプリケーションURL（スリープ防止用） |

#### IDの取得方法

- **チャンネルID**: Discordで右クリック → "IDをコピー"
- **ロールID**: サーバー設定 → ロール → 対象ロール右クリック → "IDをコピー"

### 3. Koyeb でのデプロイ

#### ステップ1: GitHub リポジトリにプッシュ

```bash
git init
git add .
git commit -m "Initial commit: Discord Bot"
git remote add origin https://github.com/your-username/discordbot.git
git push -u origin main
```

#### ステップ2: Koyeb ダッシュボードでアプリケーション作成

1. [Koyeb](https://www.koyeb.com) にログイン
2. **Create Service** → **GitHub** を選択
3. リポジトリを接続
4. **Dockerfile** を選択（自動検出）
5. **Environment Variables** で以下を設定:
   - `DISCORD_TOKEN`
   - `CHANNEL_ID`
   - `EDIT_ROLE_ID`
   - `APP_URL` （Koyeb割り当てのURL）

#### ステップ3: デプロイ

- **Deploy** をクリック
- 数分でデプロイ完了
- サービスは24時間稼働

## 🎮 スラッシュコマンド

### `/edit_quota <メンバー名> <新しいノルマ値>`

既存メンバーのノルマを更新します。

```
/edit_quota メンバーA 150
```

**権限**: 編集ロール必須

---

### `/add_member <メンバー名> <ノルマ値>`

新しいメンバーをノルマ表に追加します。

```
/add_member メンバーD 110
```

**権限**: 編集ロール必須

---

### `/remove_member <メンバー名>`

メンバーをノルマ表から削除します。

```
/remove_member メンバーA
```

**権限**: 編集ロール必須

## 📁 ファイル構成

```
discordbot/
├── main.py              # Bot メインロジック
├── server.py            # FastAPI Webサーバー
├── run.py               # エントリーポイント（Bot + サーバー並行実行）
├── requirements.txt     # Python依存パッケージ
├── Dockerfile           # Koyeb デプロイ用
├── .env.example         # 環境変数テンプレート
├── .gitignore           # Git管理除外ファイル
└── README.md            # このファイル
```

## 🔐 セキュリティ上の注意

- **`.env` ファイルは Git にプッシュしないでください** （`.gitignore` で管理）
- **Koyeb の Environment Variables** で機密情報を管理
- **ロール制限** を適切に設定して、誰でも編集できない構成に

## 🐛 トラブルシューティング

### Bot がオンラインにならない

- `DISCORD_TOKEN` が正しいか確認
- Bot に必要な権限があるか確認：
  - メッセージ送信
  - Embed メッセージ送信
  - メッセージ削除

### コマンドが表示されない

- スラッシュコマンド同期に時間がかかる場合がある（最大1時間）
- Bot を再起動してみる

### Koyeb でスリープする

- `APP_URL` が正しく設定されているか確認
- ポーリング間隔（デフォルト5分）を短くしたい場合は `main.py` の `@tasks.loop()` を編集

## 📚 参考リンク

- [Discord.py 公式ドキュメント](https://discordpy.readthedocs.io/)
- [FastAPI 公式ドキュメント](https://fastapi.tiangolo.com/)
- [Koyeb ドキュメント](https://www.koyeb.com/docs)

## 📝 ライセンス

MIT License

## 🤝 サポート

問題や質問がある場合は、GitHub Issues で報告してください。

---

**最終更新**: 2026年4月28日
