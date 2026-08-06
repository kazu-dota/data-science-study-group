# データサイエンス勉強会

製薬企業の化学分野の研究者を対象に、予測モデルを「作って終わり」ではなく、意図を持って評価・改善し、運用まで見据えられるようになることを目指す、全5回の勉強会です（各回は長め・自己完結で、1回で全部を終える必要はありません）。

講義だけでなく、毎回Pythonコードを動かし、結果の違いや失敗を全体で共有します。自習は任意です。同期だけでも次へ進めるよう、Notebookには共通課題と発展課題を用意します。

![化学研究からデータ、モデル、予測へ進む5人の学習イメージ](assets/images/course-journey.png)

教材と進行は日本語を基本にします。外部の英語公式ドキュメントは、講師が必要箇所を確認するための参考資料として扱います。概念は文章だけでなく、図、Notebookの出力、身近な化学研究の例を組み合わせて説明します。

## まず見る場所

- [全5回の進め方](docs/course-plan.md)
- [各回で使う既存教材候補](docs/resources.md)
- [Windows環境の準備](docs/setup-windows.md)
- [M365 Copilotと一緒にコードを書く](docs/copilot-guide.md)
- [講師用進行ガイド](docs/instructor-guide.md)
- [Kaggle Titanic 日本語ガイド](docs/kaggle-titanic-guide.md)
- [各回の教材](lessons/)
- [教材データの説明](data/README.md)

## ローカル環境

Windows、VS Code、`uv`を標準環境とします。GitHubアカウントとGitのインストールは不要です。それぞれ何なのかを簡単に説明します。

- **Windows**：このパソコンを動かしている基本のソフト（OS）です。普段使っているパソコンそのものだと考えて構いません。
- **VS Code**：プログラムのコードを書いたり編集したりするための無料アプリです。Microsoftが作っていて、文章を書くときのメモ帳やWordのような役割を、プログラミング用に強化したものです。
- **uv**：Pythonの実行環境と、必要な部品（ライブラリ）を自動でそろえてくれる道具です。誰のパソコンで実行しても同じ結果になるように、環境を統一する役目を持ちます。

この教材のNotebookを自分のパソコンで動かせるようにするため、最初に一度だけ次の準備をします（一度実行すれば、以降は繰り返す必要はありません）。

1. GitHub画面右上の緑色の`Code`を押す
2. `Download ZIP`を選ぶ
3. ZIPを展開し、展開したフォルダをVS Codeで開く
4. VS Codeのターミナルで次を実行する

```powershell
uv sync
uv run python scripts/check_environment.py
```

Notebookをブラウザで開く場合は、次を実行します。

```powershell
uv run jupyter lab
```

VS Codeで`lesson.ipynb`のようなNotebookファイルを開くと、画面右上に「カーネルの選択」というボタンが表示されます。カーネルとは、そのNotebookのコードを実際に動かすPython本体のことです。ここで、先ほどの`uv sync`によって用意された `.venv\Scripts\python.exe` を選んでください。これを選ばないと、この教材に必要な部品（ライブラリ）が入っていない別のPythonでコードが実行され、エラーになることがあります。

各回のフォルダにある`lesson.ipynb`を`workspace`へコピーし、コピーした方を上から順に実行します。

## Notebookの進め方

各Notebookは「説明 → コード → 出力の読み方」の順に進みます。初めて出るAPIや用語は、
使うセルで説明します。最初に専門用語を覚える必要はありません。

まず「基本」と「演習」を上から順に進めてください。「補足」は必要に応じて読みます。
「発展（任意）」「追加演習（任意）」「自由課題（任意）」は経験者や自習向けなので、
初学者は飛ばして構いません。一部でXGBoostやOptunaを使う場合だけ、`uv sync --extra advanced`を実行します。

## 図の読み方

- 雰囲気や全体像をつかむ場面では、オリジナルのイラストを使います
- 手順や用語を正確に区別する場面では、日本語ラベル付きの図を使います
- 図だけで結論を決めず、実際のデータとNotebookの結果で確かめます

## 全5回

各回は**パート1〜3**（第5回はパート4まで）で構成されます。「フォルダ」を押すと、その回の教材（`README.md`と`lesson.ipynb`）へ直接移動できます。

| 回 | テーマ | 含むパート | フォルダ | Notebook |
|---:|---|---|---|---|
| 1 | Pythonとデータに触れ、まず予測を動かす | 予測を動かす／Python／pandas | [01-python-and-data](lessons/01-python-and-data/) | [開く](lessons/01-python-and-data/lesson.ipynb) |
| 2 | データを見て、問いを立て、評価を設計する | EDA／問題設定／検証・リーク | [02-look-frame-validate](lessons/02-look-frame-validate/) | [開く](lessons/02-look-frame-validate/lesson.ipynb) |
| 3 | 回帰・分類・前処理Pipelineでモデルを作る | 回帰／分類／Pipeline | [03-build-models](lessons/03-build-models/) | [開く](lessons/03-build-models/lesson.ipynb) |
| 4 | モデルを比較し、特徴量と実験で改善する | モデル比較／特徴量／実験サイクル | [04-compare-and-improve](lessons/04-compare-and-improve/) | [開く](lessons/04-compare-and-improve/lesson.ipynb) |
| 5 | 提出から運用・監視・再学習（MLOps）へ | 模擬コンペ提出／改善会／Show&Tell／MLOps | [05-ship-and-operate](lessons/05-ship-and-operate/) | [開く](lessons/05-ship-and-operate/lesson.ipynb) |

## 公開リポジトリのルール

このリポジトリには、公開・再配布可能なデータ、合成データ、独自に作成したコード、外部教材へのリンクだけを置きます。自社データ、社内限定資料、実在プロジェクトを推測できる情報、購入教材の転載は置きません。
