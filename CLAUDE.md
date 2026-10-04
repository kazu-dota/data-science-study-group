# CLAUDE.md

このリポジトリは、機械学習を初めて学ぶ人向けの日本語Jupyter教材です。
完成物はQuickstart、全5回のNotebook、3つのAppendixです。

## 教材の順序

1. `quickstart.ipynb`：最初に完成形を動かす
2. `lessons/01-python-pandas-numpy/lesson.ipynb`
3. `lessons/02-machine-learning-basics/lesson.ipynb`
4. `lessons/03-advanced-models/lesson.ipynb`
5. `lessons/04-model-evaluation/lesson.ipynb`
6. `lessons/05-performance-improvement/lesson.ipynb`
7. `appendix/*.ipynb`：画像、音声、自然言語処理

## Notebookの編集方法

Notebookの元になる内容は`scripts/course_content/`に分割されています。
生成先と順序は`scripts/generate_course.py`だけに記載します。
生成済みの`.ipynb`を直接直さず、対応するPythonファイルを直して再生成してください。

```powershell
uv run python scripts/generate_course.py
uv run python scripts/validate_materials.py --execute
```

`data/compound_experiments.csv`は生成対象ではありません。
教材用の固定データとして扱い、データを変える意図がない修正では変更しません。

## 検証

```powershell
uv sync
uv run ruff check scripts
uv run python scripts/check_environment.py
uv run python scripts/validate_materials.py
uv run python scripts/validate_materials.py --execute
```

`validate_materials.py --execute`はQuickstart、全5回、全Appendixを空の出力から実行します。
任意依存を入れなくても全Notebookが完走する状態を保ちます。

XGBoostを試す場合だけ、次の追加依存を使います。

```powershell
uv sync --extra advanced
```

## 教材を書くとき

- 学習者向けの文章は日本語にする
- 必要になる前に専門用語を並べない
- 説明の直後に、短く実行できるコードを置く
- 入力、処理、出力の順に説明する
- 値を1つ変えて結果を比べられるようにする
- 比喩や独自の呼び名を増やさず、一般的な用語を使う
- `CORE`、`DEEP DIVE`など、学習に不要なラベルを付けない
- 外部API、アカウント、GPUを本編の必須条件にしない
- XGBoostは`ImportError`を処理し、未導入でも先へ進めるようにする

## 構成を保つためのルール

- 共通のNotebook組み立て処理は`scripts/course_content/builder.py`に置く
- 各回の内容は対応する1ファイルへ置き、別の回へコピーしない
- 同じデータ分割や前処理を比べる場合は条件をそろえる
- `archive/`は退避済みの作業なので、明示的な依頼なしに変更しない
- 参加者が編集するNotebookは`workspace/`へコピーする

## 同期して更新する資料

教材の順序や名前を変えた場合は、次も確認します。

- `README.md`
- `lessons/README.md`
- `docs/course-plan.md`
- `docs/instructor-guide.md`
- `docs/resources.md`
- `data/README.md`
