# sloth feed
* Pythonで構築するスクレイピング+Discord通知Botアプリ

## アーキテクチャ
* オニオンアーキテクチャベースの層構造を採用する
    * Controller → IService(Interface層) ← Service → IRepository(Interface層) ← Repository
* ControllerからRepositoryを直接呼ばない。必ずServiceを経由する
* すべてのService・Repositoryに対応するInterfaceを原則作成する

## ディレクトリ構成
```
project_root/
├── main.py                       # エントリーポイント、DIの注入
├── controller/                   # 処理フローの制御、エントリーポイントは run()、1コマンド1Controller
├── service/                      # ビジネスロジック、Interface層の抽象を実装
├── repository/                   # データソース(DB,S3,外部API等)との入出力、Interface層の抽象を実装
├── interface/                    # Service・Repositoryの抽象(ABC)
└── model/                        # エンティティ・値オブジェクト(dataclass)、必要になった時点で追加
```

## 命名規則
| レイヤー | ファイル名パターン | クラス名例 |
|---------|-------------------|-----------|
| Controller | `{機能名}_controller.py` | `ScrapeController` |
| Service | `{技術名}_{データ名}_service.py` | `OpenaiSummaryService` |
| Repository | `{技術名}_{データ名}_repository.py` | `S3NewsRepository` |
| Interface | `i_{データ名}_{層名}.py` | `INewsRepository`, `INewsService` |
| Model | `{モデル名}.py` | `Article` |

## ブランチ戦略
* GitHubフローベース
* mainブランチは常にデプロイ可能な状態を保つ

### ブランチ命名規則
* `プレフィックス/簡潔な説明`(例: `feature/add-search`)
    * `feature/` — 新機能・改善
    * `fix/` — バグ修正
    * `chore/` — リファクタ、ドキュメントなど、その他の変更

### ワークフロー
1. mainからブランチを切る
2. 作業してPRを出す
3. レビュー後にmainへマージ

### コミットメッセージ
* `絵文字 簡単な説明`(例: `✨ 検索機能を追加`)
    * ✨ 新機能
    * 🐛 バグ修正
    * ♻️ リファクタ
    * 📝 ドキュメント
    * 🔧 その他の変更