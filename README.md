# データサイエンス勉強会

Pythonを初めて使う人が、表データの確認から予測モデルの改善までを5回で体験する教材です。
説明を読むだけでなく、Jupyter Notebookのコードを上から順に動かして進めます。

## 最初の10分で予測を動かす

細かい説明に入る前に、[quickstart.ipynb](quickstart.ipynb)を開いてください。
このNotebookには、全5回で学ぶ次の流れを1本のコードにまとめています。

1. pandasとNumPyでデータを用意する
2. scikit-learnで分類モデルを学習する
3. GBDTで予測する
4. F1と混同行列で評価する
5. 判定のしきい値を変えて性能を調整する

分からない行は飛ばして構いません。まず全セルを実行し、予測結果が変わる様子を試します。

## 準備

Windows、VS Code、`uv`を標準環境とします。教材をZIPでダウンロードして展開し、
そのフォルダをVS Codeで開いてください。ターミナルで次を一度だけ実行します。

```powershell
uv sync
uv run python scripts/check_environment.py
uv run jupyter lab
```

ブラウザにJupyterLabが開いたら、`quickstart.ipynb`を選びます。
VS Code上でNotebookを開く場合は、右上の「カーネルの選択」から
`.venv\Scripts\python.exe`を選んでください。

詳しい準備は[Windows環境の準備](docs/setup-windows.md)にあります。

## 全5回

| 回 | 学ぶこと | Notebook |
|---:|---|---|
| 1 | Pythonの基礎とpandas・NumPy | [開く](lessons/01-python-pandas-numpy/lesson.ipynb) |
| 2 | scikit-learnと機械学習、分類・回帰 | [開く](lessons/02-machine-learning-basics/lesson.ipynb) |
| 3 | GBDTなどの高度な予測モデル | [開く](lessons/03-advanced-models/lesson.ipynb) |
| 4 | 予測モデルの評価 | [開く](lessons/04-model-evaluation/lesson.ipynb) |
| 5 | 性能を向上させるテクニック | [開く](lessons/05-performance-improvement/lesson.ipynb) |

各回は前の回の内容を短く使いながら、1つ新しい考え方を加えます。
用語の暗記よりも、コードを変更したときに結果がどう変わるかを確かめます。

## Appendix

学習した仕組みが表データ以外にも使えることを、手元のPCだけで試します。
外部API、アカウント、GPUは必要ありません。

| テーマ | 試すこと | Notebook |
|---|---|---|
| 画像認識 | 手書き数字を0〜9に分類する | [開く](appendix/image-recognition.ipynb) |
| 音声認識の入口 | 合成した音の高さを分類する | [開く](appendix/audio-recognition.ipynb) |
| 自然言語処理 | 日本語の短文をカテゴリ分けする | [開く](appendix/nlp.ipynb) |

## Notebookの進め方

- 上から順にセルを実行する
- 出力を確認してから、指定された値を1つだけ変える
- エラーが出たら、直前まで順番に実行したか確認する
- 元に戻せるよう、自分の実験用コピーを`workspace`に置く

全て理解してから進む必要はありません。動いた結果を見て疑問を持ち、
次の回で仕組みを少しずつ理解する構成です。

## 補助資料

- [全5回の進め方](docs/course-plan.md)
- [講師用進行ガイド](docs/instructor-guide.md)
- [参考資料](docs/resources.md)
- [教材データの説明](data/README.md)

## 教材を変更したとき

Notebookの生成と検証は次のコマンドで行います。

```powershell
uv run python scripts/generate_course.py
uv run python scripts/validate_materials.py --execute
```

## 公開リポジトリのルール

公開・再配布できるデータ、合成データ、独自コード、外部教材へのリンクだけを置きます。
自社データ、社内限定資料、実在プロジェクトを推測できる情報は置きません。
