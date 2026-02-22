# Python Dev Container Template

* Python開発用のDev Containerテンプレート

## 概要
* Image
    * mcr.microsoft.com/devcontainers/python:3
* Features
    * Claude Code
    * GitHub CLI
    * Node.js（Claude Codeのインストールに必要）
* Extensions
    * Python (ms-python.python)
    * Ruff (charliermarsh.ruff)
    * indent-rainbow (oderwat.indent-rainbow)
    * Rainbow CSV (mechatroner.rainbow-csv)
* Python Library
    * Ruff

## 備考
* git、GitHub CLI、Claude Codeの認証をコンテナ内でスムーズに使うため、以下が必要
    * WSLでSSHエージェントの起動（gitのSSHキーをフォワード）
    * WSLでGitHub CLIとClaude Codeの認証（configファイルをコンテナにマウント）
