# 各回で使う既存教材候補

## 選定方針

- 主教材は各回1つ、補助教材は1～2つに絞る
- 同期回はこのリポジトリのNotebookを中心に進め、外部教材は必要部分だけ使う
- 無料の公式教材と一次情報を優先する
- 英語教材は、実行するセルや見る節を講師が指定する
- 外部教材はリンクのみ掲載し、本文・画像・動画を転載しない
- リンクと対応バージョンは開講前に再確認する

## 第1回：予測モデルを動かしてみる

**主教材候補**

- [GitHub Docs: What is GitHub?](https://docs.github.com/en/get-started/start-your-journey/what-is-github) — リポジトリ、Git、GitHubの違いを画面で確認する。読むのは冒頭と「GitHub and Git」だけ。

**補助教材候補**

- [uv: Using uv with Jupyter](https://docs.astral.sh/uv/guides/integration/jupyter/) — 講師の環境構築用リファレンス。
- [scikit-learn: Getting Started](https://scikit-learn.org/stable/getting_started.html) — `fit`、`predict`、Pipelineの全体像。受講者はコード例を見るだけでよい。

## 第2回：Pythonを読み、Copilotと少し変える

**主教材候補**

- [Kaggle Learn: Python](https://www.kaggle.com/learn/python) — Lesson 1「Hello, Python」、Lesson 2「Functions」、Lesson 4「Lists」を抜粋する。全コースは約5時間なので必修にはしない。

**補助教材候補**

- [Python公式チュートリアル](https://docs.python.org/ja/3/tutorial/) — 3章、4章、5章を辞書として使う。プログラミング完全初心者の主教材にはしない。
- [Microsoft Learn: Copilot Chat (Basic)の効果的なプロンプト](https://learn.microsoft.com/en-us/training/modules/write-effective-prompts-do-more-prompting/) — 目的、背景、情報源、期待する出力の4要素を扱う。

## 第3回：pandasで表データに触る

**主教材候補**

- [Kaggle Learn: Pandas](https://www.kaggle.com/learn/pandas) — Lesson 1～3を中心に、読み込み、選択、集計を使う。

**補助教材候補**

- [pandas: 10 minutes to pandas](https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html) — `DataFrame`、選択、欠損、groupby、CSV入出力の公式リファレンス。

## 第4回：データ探偵

**主教材候補**

- [Kaggle Learn: Data Visualization](https://www.kaggle.com/learn/data-visualization) — Lesson 1、3、4、5から、棒グラフ、散布図、分布を使う。

**補助教材候補**

- [seaborn User Guide and Tutorial](https://seaborn.pydata.org/tutorial.html) — 分布、カテゴリ、変数間関係の図を探す公式リファレンス。
- [pandas User Guide](https://pandas.pydata.org/pandas-docs/stable/user_guide/index.html) — missing dataとplottingの節を講師用に使う。

## 第5回：何を、いつ、何のために予測するか

**主教材候補**

- [scikit-learn MOOC: Introducing machine-learning concepts](https://inria.github.io/scikit-learn-mooc/) — 機械学習の概念と予測パイプラインを講師が日本語で要約する。

**補助教材候補**

- [Kaggle Learn: Intro to Machine Learning](https://www.kaggle.com/learn/intro-to-machine-learning) — Lesson 1「How Models Work」とLesson 2「Basic Data Exploration」。
- [scikit-learn: Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html) — `DummyClassifier`と`DummyRegressor`を含むベースラインの講師用リファレンス。

## 第6回：モデルは本当に当たっているか

**主教材候補**

- [Kaggle Learn: Intro to Machine Learning](https://www.kaggle.com/learn/intro-to-machine-learning) — Lesson 4「Model Validation」とLesson 5「Underfitting and Overfitting」。

**補助教材候補**

- [scikit-learn: Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html) — inconsistent preprocessingとdata leakage。
- [scikit-learn: Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html) — グループ・時系列・通常のランダム分割の違いを講師が参照する。

## 第7回：数値を予測する—回帰

**主教材候補**

- [Kaggle Learn: Intro to Machine Learning](https://www.kaggle.com/learn/intro-to-machine-learning) — Lesson 3「Your First Machine Learning Model」とLesson 6「Random Forests」。

**補助教材候補**

- [scikit-learn: Linear Models](https://scikit-learn.org/stable/modules/linear_model.html) — 線形回帰、Ridgeの講師用リファレンス。
- [scikit-learn: Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics) — MAE、MSE、R²の定義を確認する。

## 第8回：クラスを予測する—分類

**主教材候補**

- [scikit-learn: Classification metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics) — 混同行列、適合率、再現率、F1の公式説明。

**補助教材候補**

- [scikit-learn MOOC](https://inria.github.io/scikit-learn-mooc/) — Evaluating model performanceのClassification節。
- [scikit-learn: Linear Models](https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression) — ロジスティック回帰の講師用リファレンス。

## 第9回：前処理をPipelineにまとめる

**主教材候補**

- [Kaggle Learn: Intermediate Machine Learning](https://www.kaggle.com/learn/intermediate-machine-learning) — Missing Values、Categorical Variables、Pipelinesを抜粋する。

**補助教材候補**

- [scikit-learn: Getting Started](https://scikit-learn.org/stable/getting_started.html) — Pipelineが前処理と予測器をまとめ、リーク防止に役立つ例。
- [scikit-learn: Pipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html) — API確認用。

## 第10回：モデル対決

**主教材候補**

- [scikit-learn MOOC](https://inria.github.io/scikit-learn-mooc/) — Linear models、Decision tree models、Ensemble of modelsの動画を各1本候補とする。

**補助教材候補**

- [scikit-learn: Ensemble methods](https://scikit-learn.org/stable/modules/ensemble.html) — Random ForestとGradient Boostingの講師用リファレンス。
- [Kaggle Learn: Intermediate Machine Learning](https://www.kaggle.com/learn/intermediate-machine-learning) — XGBoostは発展課題として扱い、本編の必須にはしない。

## 第11回：化学の知識を特徴量にする

**主教材候補**

- [RDKit: Getting Started with the RDKit in Python](https://www.rdkit.org/docs/GettingStartedInPython.html) — SMILES、分子描画、分子量、LogP、TPSA、記述子計算の必要部分だけ使う。

**補助教材候補**

- [Kaggle Learn: Feature Engineering](https://www.kaggle.com/learn/feature-engineering) — 特徴量を作って同じ検証条件で比較する考え方。
- [RDKit Cookbook](https://www.rdkit.org/docs/Cookbook.html) — 講師が化学系の追加例を探すためのリファレンス。

**注意**

RDKitは初心者全員の必須操作にはしない。講師が計算済みの記述子表も用意し、環境トラブルで本題が止まらないようにする。

## 第12回：改善実験を小さく回す

**主教材候補**

- [scikit-learn: Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html) — `cross_val_score`と、分割によるスコアのばらつき。

**補助教材候補**

- [Kaggle Learn: Machine Learning Explainability](https://www.kaggle.com/learn/machine-learning-explainability) — Lesson 1「Use Cases」とLesson 2「Permutation Importance」。SHAPは発展扱い。
- [scikit-learn: Model selection and evaluation](https://scikit-learn.org/stable/model_selection.html) — チューニング、評価指標、validation curveの講師用リファレンス。

## 第13回：Kaggleに入って最初の提出を作る

**主教材候補**

- [Kaggle: Titanic — Machine Learning from Disaster](https://www.kaggle.com/competitions/titanic) — 分類、欠損、カテゴリ、特徴量、提出までを体験しやすい第一候補。

**補助教材候補**

- [Kaggle Learn: Intro to Machine Learning](https://www.kaggle.com/learn/intro-to-machine-learning) — Lesson 7「Machine Learning Competitions」。
- [Kaggle: House Prices](https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques) — 参加者が回帰を強く希望した場合の代替候補。列数と欠損が多いため、Titanicより難しい。

## 第14回：Kaggle改善会

**主教材候補**

- [Kaggle: Titanic Code](https://www.kaggle.com/competitions/titanic/code) — 他者のNotebookは、まず自分たちのベースラインを作った後で読む。

**補助教材候補**

- [Kaggle Learn: Feature Engineering](https://www.kaggle.com/learn/feature-engineering) — 特徴量案を探す。
- [Kaggle Learn: Machine Learning Explainability](https://www.kaggle.com/learn/machine-learning-explainability) — 重要度と個別予測の確認に使う。

## 第15回：Show & Tellと自社データへの橋渡し

**主教材候補**

- [scikit-learn MOOC: Concluding remarks](https://inria.github.io/scikit-learn-mooc/concluding_remarks.html) — 機械学習は課題解決全体の一部である、というまとめに使う。

**補助教材候補**

- [scikit-learn: Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) — 自社データで再発しやすいリーク、前処理、乱数の確認表として使う。

## 書籍候補

### 参加者向けの共通参考書候補

- [『Pythonによるあたらしいデータ分析の教科書 第3版』](https://www.shoeisha.co.jp/book/detail/9784798192291) — Python、NumPy、pandas、Matplotlib、scikit-learnまで日本語で一通り参照できる。2025年刊。全員の必読ではなく、手元に置く参考書候補。

### pandasを深く使いたい人向け

- [『Pythonによるデータ分析入門 第3版』](https://www.oreilly.co.jp/books/9784814400195/) — pandas開発者による詳細な解説。600ページを超えるため、通読課題にはせず、第3～4回の発展資料とする。

### Kaggle・講師向け

- [『Kaggleで勝つデータ分析の技術』](https://gihyo.jp/book/2019/978-4-297-10843-4) — バリデーション、特徴量、チューニングの考え方を参照する。2019年刊のため、コードやライブラリ仕様は現行公式ドキュメントで確認する。

## Udemyの扱い

現時点では特定コースを必須指定しません。5人のPython経験差が大きく、同期回とKaggle Learnで基礎を揃えられるためです。希望者が多い場合のみ、次の条件で1コースを選びます。

- 日本語
- Windows＋JupyterまたはVS Code対応
- pandas、scikit-learn、モデル評価を含む
- Python文法だけで全体の半分を使わない
- 更新日とQ&Aの最近の活動を確認できる
- 深層学習を主目的としていない

候補の選定は開講時点の内容、価格、更新状況を見て行います。
