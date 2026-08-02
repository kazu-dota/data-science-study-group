# 各回で使う既存教材候補

## 選定方針

- 受講者が読む主教材は日本語を基本にする
- 主教材は各回1つ、補助教材は1～2つに絞る
- 同期回はこのリポジトリのNotebookを中心に進め、外部教材は必要部分だけ使う
- 無料の公式教材と一次情報を優先する
- 英語教材は原則として講師用とし、受講者に使ってもらう場合は実行するセルや見る節を指定する
- 外部教材はリンクのみ掲載し、本文・画像・動画を転載しない
- リンクと対応バージョンは開講前に再確認する

## 日本語を中心に進める方法

難しい用語をいきなり英語ドキュメントで調べる必要はありません。各回は次の順で進めます。

1. このリポジトリの日本語Notebookと図で、まず動かす
2. 日本語の公開教材で、分からなかった概念を補う
3. APIの細かな仕様だけ、講師が英語の公式ドキュメントで確認する

日本語の共通教材は、次の3つを軸にします。

- [東京大学「Pythonプログラミング入門」](https://utokyo-ipp.github.io/) — Python、pandas、scikit-learnまで日本語で参照できる。第1回〜第3回で必要な節だけ使う。
- [総務省統計局「データサイエンス・オンライン講座」](https://www.stat.go.jp/dss/online_index.html) — 統計の見方とデータ活用の入口。登録型講座は開講時期を確認する。
- [機械学習帳](https://chokkan.github.io/mlnote/) — 回帰・分類・モデル選択を、Pythonの実行例と一緒に学べる。数式は全員の必修にせず、図と実行例を中心に使う。

全5回はそれぞれ3つのパート（第5回だけ4つ）に分かれます。以下は旧15回教材の各回に対応する外部教材の一覧で、各回のパートごとにまとめています。この一覧では、`日本語・受講者向け`と`英語・講師用`を分けて記載します。Kaggle、RDKit、scikit-learnの最新仕様など日本語の一次資料が少ない部分は、リポジトリ内に日本語の橋渡し解説を用意します。

## 第1回：Pythonとデータに触れ、まず予測を動かす

### パート1：予測モデルを動かしてみる

**日本語・受講者向け**

- [GitHub Docs「GitHub アカウントの始め方」](https://docs.github.com/ja/get-started/onboarding/getting-started-with-your-github-account) — README、フォルダ、履歴の画面を怖がらず見られることが目標。アカウント作成や共同開発は必須にしない。

**英語・講師用**

- [uv: Using uv with Jupyter](https://docs.astral.sh/uv/guides/integration/jupyter/) — 講師の環境構築用リファレンス。
- [scikit-learn: Getting Started](https://scikit-learn.org/stable/getting_started.html) — `fit`、`predict`、Pipelineの全体像。受講者はコード例を見るだけでよい。

### パート2：Pythonを読み、Copilotと少し変える

**日本語・受講者向け**

- [東京大学「Pythonプログラミング入門」](https://utokyo-ipp.github.io/) — 「変数と関数の基礎」「リスト」「辞書」「繰り返し」「関数」から、Notebookに出てきた項目だけ読む。
- [Microsoft Support「Microsoft 365 Copilotに優れたプロンプトを書く」](https://support.microsoft.com/ja-jp/microsoft-365-copilot/write-a-great-prompt-in-microsoft-365-copilot) — 目標、コンテキスト、ソース、期待値の4要素を、コード説明の依頼へ置き換えて使う。

**補助・辞書**

- [Python公式チュートリアル](https://docs.python.org/ja/3/tutorial/) — 3章、4章、5章を辞書として使う。プログラミング完全初心者の主教材にはしない。
- [Kaggle Learn: Python](https://www.kaggle.com/learn/python) — 英語。経験者の任意演習としてLesson 1、2、4を使う。

### パート3：pandasで表データに触る

**日本語・受講者向け**

- [東京大学「Pythonプログラミング入門」7-1 pandasライブラリ](https://utokyo-ipp.github.io/) — `DataFrame`、CSV読み込み、参照、条件抽出、統計量を使う。
- [データサイエンス100本ノック（構造化データ加工編）](https://github.com/The-Japan-DataScientist-Society/100knocks-preprocess) — 環境一式は使わず、講師が現在のNotebookへ移した数問を任意演習にする。

**英語・講師用**

- [pandas: 10 minutes to pandas](https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html) — `DataFrame`、選択、欠損、groupby、CSV入出力の公式リファレンス。
- [Kaggle Learn: Pandas](https://www.kaggle.com/learn/pandas) — Lesson 1～3を経験者の任意演習にする。

## 第2回：データを見て、問いを立て、評価を正しく設計する

### パート1：データ探偵

**日本語・受講者向け**

- [東京大学「Pythonプログラミング入門」Matplotlibライブラリ](https://utokyo-ipp.github.io/) — 散布図、棒グラフ、ヒストグラムを、同じデータで描き分ける。
- [総務省統計局「プレゼングラフ作成のポイント」](https://www.stat.go.jp/dss/online_index.html) — グラフを選ぶ目的と、誤解させない見せ方を確認する。

**英語・講師用**

- [Kaggle Learn: Data Visualization](https://www.kaggle.com/learn/data-visualization) — Lesson 1、3、4、5から例を探す。
- [seaborn User Guide and Tutorial](https://seaborn.pydata.org/tutorial.html) — 分布、カテゴリ、変数間関係の図を探す公式リファレンス。
- [pandas User Guide](https://pandas.pydata.org/pandas-docs/stable/user_guide/index.html) — missing dataとplottingの節を講師用に使う。

### パート2：何を、いつ、何のために予測するか

**日本語・受講者向け**

- [東京大学「Pythonプログラミング入門」7-2 scikit-learnライブラリ](https://utokyo-ipp.github.io/) — 教師あり学習、分類、回帰の違いを実行例からつかむ。
- [総務省統計局「社会人のためのデータサイエンス入門」](https://www.stat.go.jp/dss/online_index.html) — データ活用と統計の基礎を補う任意講座。開講時期を確認する。

**英語・講師用**

- [scikit-learn MOOC: Introducing machine-learning concepts](https://inria.github.io/scikit-learn-mooc/) — 機械学習の概念と予測パイプラインを講師が日本語で要約する。
- [Kaggle Learn: Intro to Machine Learning](https://www.kaggle.com/learn/intro-to-machine-learning) — Lesson 1「How Models Work」とLesson 2「Basic Data Exploration」。
- [scikit-learn: Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html) — `DummyClassifier`と`DummyRegressor`を含むベースラインの講師用リファレンス。

### パート3：モデルは本当に当たっているか

**日本語・受講者向け**

- [機械学習帳「モデル選択と正則化」](https://chokkan.github.io/mlnote/regression/03regularization.html) — 訓練誤差と汎化誤差、モデル選択の図を中心に使う。数式の導出は任意。
- [第2回（検証・リークのパート）](../lessons/02-look-frame-validate/README.md) — 学習用・検証用・テスト用の役割と、リークという「近道」を先にイメージで確認する。

**英語・講師用**

- [Kaggle Learn: Intro to Machine Learning](https://www.kaggle.com/learn/intro-to-machine-learning) — Lesson 4「Model Validation」とLesson 5「Underfitting and Overfitting」。
- [scikit-learn: Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html) — inconsistent preprocessingとdata leakage。
- [scikit-learn: Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html) — グループ・時系列・通常のランダム分割の違いを講師が参照する。

## 第3回：回帰・分類・前処理Pipelineでモデルを作る

### パート1：数値を予測する—回帰

**日本語・受講者向け**

- [機械学習帳「単回帰」](https://chokkan.github.io/mlnote/regression/01sra.html) — 実測値、予測値、誤差の関係を図と実行例から読む。
- [東京大学「Pythonプログラミング入門」7-2 scikit-learnライブラリ](https://utokyo-ipp.github.io/) — 「教師あり学習・回帰の例」を短い復習に使う。

**英語・講師用**

- [Kaggle Learn: Intro to Machine Learning](https://www.kaggle.com/learn/intro-to-machine-learning) — Lesson 3「Your First Machine Learning Model」とLesson 6「Random Forests」。
- [scikit-learn: Linear Models](https://scikit-learn.org/stable/modules/linear_model.html) — 線形回帰、Ridgeの講師用リファレンス。
- [scikit-learn: Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics) — MAE、MSE、R²の定義を確認する。

### パート2：クラスを予測する—分類

**日本語・受講者向け**

- [機械学習帳「線形二値分類」](https://chokkan.github.io/mlnote/classification/01binary.html) — スコア、確率、判定の関係を実行例で見る。数式の導出は任意。
- [東京大学「Pythonプログラミング入門」7-2 scikit-learnライブラリ](https://utokyo-ipp.github.io/) — 「教師あり学習・分類の例」を短い復習に使う。

**英語・講師用**

- [scikit-learn: Classification metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics) — 混同行列、適合率、再現率、F1の定義を確認する。
- [scikit-learn MOOC](https://inria.github.io/scikit-learn-mooc/) — Evaluating model performanceのClassification節。
- [scikit-learn: Linear Models](https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression) — ロジスティック回帰の講師用リファレンス。

### パート3：前処理をPipelineにまとめる

**日本語・受講者向け**

- このリポジトリの第3回パート3のNotebookを主教材にする。数値列とカテゴリ列が別々の入口を通り、最後に1つのモデルへ合流する流れを日本語図で確認してからコードを読む。
- [『Pythonによるあたらしいデータ分析の教科書 第3版』](https://www.shoeisha.co.jp/book/detail/9784798192291) — scikit-learnを使う章から、前処理とモデル構築の部分を参考にする。購入は任意。

**英語・講師用**

- [Kaggle Learn: Intermediate Machine Learning](https://www.kaggle.com/learn/intermediate-machine-learning) — Missing Values、Categorical Variables、Pipelinesを抜粋する。
- [scikit-learn: Getting Started](https://scikit-learn.org/stable/getting_started.html) — Pipelineが前処理と予測器をまとめ、リーク防止に役立つ例。
- [scikit-learn: Pipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html) — API確認用。

## 第4回：モデルを比較し、特徴量と実験で改善する

### パート1：モデル対決

**日本語・受講者向け**

- このリポジトリのモデル比較表と日本語図解を主教材にする。「同じ分割・同じ指標」で比べることを先に固定し、モデルの名前は後から確認する。
- [機械学習帳](https://chokkan.github.io/mlnote/) — 線形モデルの仕組みを深めたい人向け。全員での通読はしない。

**英語・講師用**

- [scikit-learn MOOC](https://inria.github.io/scikit-learn-mooc/) — Linear models、Decision tree models、Ensemble of modelsの動画を各1本候補とする。
- [scikit-learn: Ensemble methods](https://scikit-learn.org/stable/modules/ensemble.html) — Random ForestとGradient Boostingの講師用リファレンス。
- [Kaggle Learn: Intermediate Machine Learning](https://www.kaggle.com/learn/intermediate-machine-learning) — XGBoostは発展課題として扱い、本編の必須にはしない。

### パート2：化学の知識を特徴量にする

**日本語・受講者向け**

- このリポジトリの第4回パート2のNotebookを主教材にする。SMILESや記述子は日本語の注釈付きスターターコードで扱い、受講者が英語APIを読み解くことは前提にしない。
- [『Pythonによるあたらしいデータ分析の教科書 第3版』](https://www.shoeisha.co.jp/book/detail/9784798192291) — 特徴量の表をpandasとscikit-learnへ渡す部分の参考書として使う。購入は任意。

**英語・講師用**

- [RDKit: Getting Started with the RDKit in Python](https://www.rdkit.org/docs/GettingStartedInPython.html) — SMILES、分子描画、分子量、LogP、TPSA、記述子計算の必要部分だけ使う。
- [Kaggle Learn: Feature Engineering](https://www.kaggle.com/learn/feature-engineering) — 特徴量を作って同じ検証条件で比較する考え方。
- [RDKit Cookbook](https://www.rdkit.org/docs/Cookbook.html) — 講師が化学系の追加例を探すためのリファレンス。

**注意**

RDKitは初心者全員の必須操作にはしない。講師が計算済みの記述子表も用意し、環境トラブルで本題が止まらないようにする。

### パート3：改善実験を小さく回す

**日本語・受講者向け**

- [全5回の進め方「改善実験を小さく回す」](course-plan.md#パート3改善実験を小さく回す) — 「1つ変える→同じ条件で評価→記録する」の日本語図を実験の型として使う。
- [機械学習帳「モデル選択と正則化」](https://chokkan.github.io/mlnote/regression/03regularization.html) — 検証データによるモデル選択の考え方を補う。数式の導出は任意。

**英語・講師用**

- [scikit-learn: Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html) — `cross_val_score`と、分割によるスコアのばらつき。
- [Kaggle Learn: Machine Learning Explainability](https://www.kaggle.com/learn/machine-learning-explainability) — Lesson 1「Use Cases」とLesson 2「Permutation Importance」。SHAPは発展扱い。
- [scikit-learn: Model selection and evaluation](https://scikit-learn.org/stable/model_selection.html) — チューニング、評価指標、validation curveの講師用リファレンス。

## 第5回：提出から運用・監視・再学習（MLOps）へ

### パート1：Kaggleに入って最初の提出を作る

**日本語・受講者向け**

- このリポジトリの第5回パート1のNotebookと日本語チェックリストを主教材にする。問題文、列の意味、評価指標、提出形式を1画面ずつ日本語で案内する。
- [Kaggle: Titanic — Machine Learning from Disaster](https://www.kaggle.com/competitions/titanic) — 英語画面だが、`Overview`、`Data`、`Submit Predictions`の3か所だけを講師と一緒に見る。

**英語・任意**

- [Kaggle Learn: Intro to Machine Learning](https://www.kaggle.com/learn/intro-to-machine-learning) — Lesson 7「Machine Learning Competitions」。
- [Kaggle: House Prices](https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques) — 参加者が回帰を強く希望した場合の代替候補。列数と欠損が多いため、Titanicより難しい。

### パート2：Kaggle改善会

**日本語・受講者向け**

- このリポジトリの第5回パート2の「実験ログ」を主教材にする。5人が日本語で変更点、検証結果、気づきを1行ずつ残す。
- [『Kaggleで勝つデータ分析の技術』](https://gihyo.jp/book/2019/978-4-297-10843-4) — バリデーションと特徴量の考え方を深めたい人向け。購入は任意で、コードは現行Notebookを使う。

**英語・任意**

- [Kaggle: Titanic Code](https://www.kaggle.com/competitions/titanic/code) — 他者のNotebookは、まず自分たちのベースラインを作った後で読む。
- [Kaggle Learn: Feature Engineering](https://www.kaggle.com/learn/feature-engineering) — 特徴量案を探す。
- [Kaggle Learn: Machine Learning Explainability](https://www.kaggle.com/learn/machine-learning-explainability) — 重要度と個別予測の確認に使う。

### パート3：Show & Tellと自社データへの橋渡し

**日本語・受講者向け**

- このリポジトリの「自社テーマ1枚シート」を主教材にする。目的、予測時点、使える列、評価方法、利用場面を日本語で埋める。
- [総務省統計局「出来る人のビジネス活用術」](https://www.stat.go.jp/dss/online_index.html) — 分析を業務で使う視点を広げる任意資料。

**英語・講師用**

- [scikit-learn MOOC: Concluding remarks](https://inria.github.io/scikit-learn-mooc/concluding_remarks.html) — 機械学習は課題解決全体の一部である、というまとめに使う。
- [scikit-learn: Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) — 自社データで再発しやすいリーク、前処理、乱数の確認表として使う。

## 書籍候補

### 参加者向けの共通参考書候補

- [『Pythonによるあたらしいデータ分析の教科書 第3版』](https://www.shoeisha.co.jp/book/detail/9784798192291) — Python、NumPy、pandas、Matplotlib、scikit-learnまで日本語で一通り参照できる。2025年刊。全員の必読ではなく、手元に置く参考書候補。

### pandasを深く使いたい人向け

- [『Pythonによるデータ分析入門 第3版』](https://www.oreilly.co.jp/books/9784814400195/) — pandas開発者による詳細な解説。600ページを超えるため、通読課題にはせず、第3～4回の発展資料とする。

### Kaggle・講師向け

- [『Kaggleで勝つデータ分析の技術』](https://gihyo.jp/book/2019/978-4-297-10843-4) — バリデーション、特徴量、チューニングの考え方を参照する。2019年刊のため、コードやライブラリ仕様は現行公式ドキュメントで確認する。

## 任意の発展ライブラリ

一部の`DEEP DIVE`は、次の任意ライブラリがあれば追加で試せます。未導入でもscikit-learnの代替で本編は完走できます。

- 使う場合のみ `uv sync --extra advanced` を実行する（`xgboost`、`optuna`）。
- [XGBoost Documentation](https://xgboost.readthedocs.io/) — 第4回パート1のモデル比較で、勾配ブースティング専用実装を任意で追加する。
- [Optuna Documentation](https://optuna.readthedocs.io/) — 第4回パート3の改善サイクルで、ランダム探索の代わりにベイズ的な探索を任意で試す。
- [scikit-learn: HistGradientBoosting](https://scikit-learn.org/stable/modules/ensemble.html#histogram-based-gradient-boosting) — 上記が無い環境の標準的な代替。

## Udemyの扱い

現時点では特定コースを必須指定しません。5人のPython経験差が大きく、同期回とKaggle Learnで基礎を揃えられるためです。希望者が多い場合のみ、次の条件で1コースを選びます。

- 日本語
- Windows＋JupyterまたはVS Code対応
- pandas、scikit-learn、モデル評価を含む
- Python文法だけで全体の半分を使わない
- 更新日とQ&Aの最近の活動を確認できる
- 深層学習を主目的としていない

候補の選定は開講時点の内容、価格、更新状況を見て行います。
