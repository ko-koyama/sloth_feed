# sloth feed

テック系のニュースや記事を定期取得してDiscordに投稿するBot

## 機能

- テック系サイトの新着記事を定期取得
  - Zenn
- 1日2回（9:00 / 18:00 JST）Discordフォーラムチャンネルに自動投稿

## 技術スタック

- Python 3
- discord.py
- httpx

## セットアップ

### 環境変数

`.env` ファイルを作成し、以下を設定する。

```
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_CHANNEL_ID_ZENN=your_channel_id
```

### インストール・実行

```bash
pip install -r requirements.txt
python main.py
```

## ディレクトリ構成

```
├── main.py          # エントリーポイント
├── controller/      # 処理フロー制御
├── service/         # ビジネスロジック
├── interface/       # 抽象(ABC)
├── model/           # データモデル
└── tests/           # テスト
```
