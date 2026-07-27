# データサイエンス勉強会

製薬企業の化学分野の研究者を対象に、予測モデルを「作って終わり」ではなく、意図を持って評価・改善できるようになることを目指す、全15回の勉強会です。

講義だけでなく、毎回Pythonコードを動かし、結果の違いや失敗を5人で共有します。自習は任意です。同期回だけでも次へ進めるよう、Notebookには共通課題と発展課題を用意します。

## まず見る場所

- [全15回の進め方](docs/course-plan.md)
- [各回で使う既存教材候補](docs/resources.md)
- [Windows環境の準備](docs/setup-windows.md)
- [M365 Copilotと一緒にコードを書く](docs/copilot-guide.md)
- [各回の教材](lessons/)

## ローカル環境

Windows、VS Code、Git for Windows、`uv`を標準環境とします。GitHubアカウントは不要です。

```powershell
git clone https://github.com/kazu-dota/data-science-study-group.git
cd data-science-study-group
uv sync
uv run python scripts/check_environment.py
```

Notebookをブラウザで開く場合は、次を実行します。

```powershell
uv run jupyter lab
```

VS Codeを使う場合は、Notebookのカーネルとして `.venv\Scripts\python.exe` を選択します。

## Notebookの目印

- `TRY`：全員で試す
- `CHANGE`：値や列を少し変更する
- `CHALLENGE`：興味のある人向けの自由研究
- `ASK COPILOT`：M365 Copilotへ相談してみる

## 全15回

| 回 | テーマ |
|---:|---|
| 1 | 予測モデルを動かしてみる |
| 2 | Pythonを読み、Copilotと少し変える |
| 3 | pandasで表データに触る |
| 4 | データ探偵：分布・欠損・外れ値 |
| 5 | 何を、いつ、何のために予測するか |
| 6 | モデルは本当に当たっているか |
| 7 | 数値を予測する：回帰 |
| 8 | クラスを予測する：分類 |
| 9 | 前処理をPipelineにまとめる |
| 10 | モデル対決：線形モデル・木・アンサンブル |
| 11 | 化学の知識を特徴量にする |
| 12 | 改善実験を小さく回す |
| 13 | Kaggleに入って最初の提出を作る |
| 14 | Kaggle改善会 |
| 15 | Show & Tellと自社データへの橋渡し |

## 公開リポジトリのルール

このリポジトリには、公開・再配布可能なデータ、合成データ、独自に作成したコード、外部教材へのリンクだけを置きます。自社データ、社内限定資料、実在プロジェクトを推測できる情報、購入教材の転載は置きません。
