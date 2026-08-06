# 外部資料の学習ガイド

各回のNotebookは実習の中心ですが、それだけでは背景知識を十分に扱えません。
このガイドでは、無料で読める資料の範囲と、読んだ後に確認することを指定します。

## 使い方

- `事前`は勉強会までに読む範囲です。45〜60分を目安にします。
- `復習`は勉強会後に読む範囲です。30〜60分を目安にします。
- 「ここから」「ここまで」は資料内の見出し名です。途中の練習問題も実行します。
- 英語資料はコードと図を先に見ます。本文の要点は勉強会で日本語で確認します。
- 外部資料のコードは、まず資料の環境で読み、教材データへの書き換えは復習で行います。

章立てとURLは2026年8月7日に確認しました。提供元の更新で見出しが変わった場合は、
同じ名前に近い章を探し、講師が開講前にリンクを確認してください。

## 第1回：Python、pandas、NumPy

### 事前：Pythonのコードを読む（約30分）

資料：[東京大学「Pythonプログラミング入門」](https://utokyo-ipp.github.io/)

1. [1-2. 変数と関数の基礎](https://utokyo-ipp.github.io/1/1-2.html)
   - ここから：`変数`
   - ここまで：`関数の定義と返値`
2. [2-2. リスト](https://utokyo-ipp.github.io/2/2-2.html)
   - ここから：`リストとインデックス`
   - ここまで：`for文による繰り返しとリスト・タプル`

確認すること：`=`、`return`、0から始まるインデックス、`for`の役割を1文ずつ書きます。

### 事前：NumPyとpandasの表を読む（約30分）

同じ資料の次の範囲を使います。

1. [5-3. NumPyライブラリ](https://utokyo-ipp.github.io/5/5-3.html)
   - ここから：`配列の構築`
   - ここまで：`要素毎の演算`
2. [7-1. pandasライブラリ](https://utokyo-ipp.github.io/7/7-1.html)
   - ここから：`シリーズとデータフレーム`
   - ここまで：`データの統計量`

確認すること：リスト、NumPy配列、DataFrameの形と、得意な処理の違いを表にします。

### 復習：データ確認とグラフ（約45分）

1. [pandas Getting started tutorials](https://pandas.pydata.org/docs/getting_started/intro_tutorials/)
   - ここから：`What kind of data does pandas handle?`
   - ここまで：`How to calculate summary statistics`
   - `How do I create plots in pandas?`も含めます。
2. [東京大学「簡単なデータの可視化」](https://utokyo-ipp.github.io/appendix/3-visualization.html)
   - ここから：`matplotlib`
   - ここまで：`棒グラフ`

追加演習：`compound_experiments.csv`から数値列を1つ選び、ヒストグラムと
カテゴリ別の平均を作ります。グラフから言える事実と、まだ言えないことを1つずつ書きます。

## 第2回：scikit-learn、分類、回帰

### 事前：予測問題を決める（約30分）

資料：[Google「Problem Framing」](https://developers.google.com/machine-learning/problem-framing/problem-framing)

- ここから：`Overview`
- ここまで：`Framing an ML problem`の`Define success metrics`
- 順番：`Overview` → `Understand the problem` → `Framing an ML problem`

確認すること：自分の題材について「理想の結果」「モデルの出力」「成功の測り方」
「予測する時点で使える列」を1行ずつ書きます。モデルの評価指標と、利用上の成功指標は分けます。

### 事前：分類と回帰を動かす（約30分）

資料：[東京大学「7-2. scikit-learnライブラリ」](https://utokyo-ipp.github.io/7/7-2.html)

- ここから：`機械学習について`
- ここまで：`教師あり学習・回帰の例`
- `教師なし学習`の詳細と、その後のクラスタリング・次元削減は今回は読み飛ばします。

確認すること：特徴量`X`、目的変数`y`、`fit`、`predict`を、分類例と回帰例から探します。

### 復習：予測Pipelineと前処理（約60分）

資料：[scikit-learn MOOC「The predictive modeling pipeline」](https://inria.github.io/scikit-learn-mooc/predictive_modeling_pipeline/predictive_modeling_module_intro.html)

1. ここから：`First look at our dataset`
2. ここまで：`Model evaluation using cross-validation`
3. `Exercise M1.01`と`Exercise M1.02`を行い、解答は実行後に確認します。
4. 続けて`Encoding of categorical variables`から
   `Using numerical and categorical variables together`まで読みます。

確認すること：数値列、カテゴリ列、欠損値へ必要な前処理と、前処理をPipelineへ
含める理由を表にします。

### 復習：過学習とデータリーク（約30分）

1. [scikit-learn MOOC「Selecting the best model」](https://inria.github.io/scikit-learn-mooc/overfit/overfit_module_intro.html)
   - ここから：`Overfitting and underfitting`
   - ここまで：`Cross-validation framework`
2. [scikit-learn「Common pitfalls」](https://scikit-learn.org/stable/common_pitfalls.html)
   - ここから：`Inconsistent preprocessing`
   - ここまで：`How to avoid data leakage`

追加演習：予測時点では分からない列を1つ混ぜてスコアを比較します。
高いスコアが得られても使えない理由と、Pipelineで防げるリーク・防げないリークを書きます。

## 第3回：決定木、Random Forest、GBDT

### 事前：1本の決定木を理解する（約45分）

資料：[scikit-learn MOOC「Decision tree models」](https://inria.github.io/scikit-learn-mooc/trees/trees_module_intro.html)

- ここから：`Intuitions on tree-based models`
- ここまで：`Importance of decision tree hyperparameters on generalization`
- 分類の`Exercise M5.01`を行います。回帰の`Exercise M5.02`は復習へ回します。

確認すること：木の深さを増やしたとき、学習データと検証データの成績がどう変わるか書きます。

### 事前：木を組み合わせる（約60分）

資料：[scikit-learn MOOC「Ensemble of models」](https://inria.github.io/scikit-learn-mooc/ensemble/ensemble_module_intro.html)

1. ここから：`Introductory example to ensemble models`
2. `Bagging`を読み、`Random forests`と`Exercise M6.02`まで進みます。
3. ここから：`Intuitions on ensemble models: boosting`
4. ここまで：`Speeding-up gradient-boosting`
5. AdaBoostの数式と`Exercise M6.03`の解答は復習へ回します。

確認すること：Random ForestとGBDTについて、木を作る順番、前の木との関係、
並列化のしやすさを比較します。

### 復習：モデル選択の判断材料（約45分）

同じMOOCの次の範囲を読みます。

- `Decision tree for regression`から`Exercise M5.02`まで
- `Hyperparameter tuning with ensemble methods`から`Exercise M6.04`まで

追加演習：決定木、Random Forest、GBDTを、F1だけでなく学習時間、予測時間、
設定項目の数、結果の説明しやすさでも比較します。

### 任意：XGBoostの仕組み（約30分）

[XGBoost「Introduction to Boosted Trees」](https://xgboost.readthedocs.io/en/stable/tutorials/model.html)の
`Elements of Supervised Learning`から`Decision Tree Ensembles`までを読みます。
数式の導出は必須ではありません。損失とモデルの複雑さを同時に考える点を確認します。

## 第4回：予測モデルの評価

### 事前：比較の基準とデータ分割（約60分）

資料：[scikit-learn MOOC「Evaluating model performance」](https://inria.github.io/scikit-learn-mooc/evaluation/evaluation_module_intro.html)

1. ここから：`Comparing model performance with a simple baseline`
2. `Exercise M7.01`まで行います。
3. ここから：`Stratification`
4. ここまで：`Non i.i.d. data`
5. `Nested cross-validation`は第5回の復習へ回します。

確認すること：ランダム分割、層化分割、グループ分割、時系列を意識した分割について、
同じ個体・系列・未来の情報が検証側から学習側へ入らないかを確認します。

### 事前：分類と回帰の指標（約60分）

同じ資料の次の範囲を使います。

- `Classification`から`Exercise M7.02`まで
- `Regression`から`Exercise M7.03`まで

確認すること：accuracy、precision、recall、F1、MAE、RMSE、R²について、
値が良くなる向き、単位、大きな誤りへの反応、使う場面を表にします。

### 復習：しきい値とクラス不均衡（約70分）

[Google Machine Learning Crash Course「Classification」](https://developers.google.com/machine-learning/crash-course/classification)を、
`Thresholds and the confusion matrix`から`ROC and AUC`まで進めます。
各ページの`Check Your Understanding`にも回答します。

追加演習：偽陰性を偽陽性の5倍重く扱うと仮定し、しきい値ごとの合計損失を計算します。
F1が最大のしきい値と、損失が最小のしきい値が一致するか確認します。

### 任意：統計とグラフを補う

[総務省統計局「社会人のためのデータサイエンス入門」](https://www.stat.go.jp/dss/online01.html)の
第2週`統計学の基礎`と第3週`データの見方と表し方`を受講します。
外部サイトへの登録と開講期間の確認が必要なため、本編の必須にはしません。

## 第5回：性能を向上させる

### 事前：特徴量を見直す（約60分）

資料：[Google Machine Learning Crash Course「Working with numerical data」](https://developers.google.com/machine-learning/crash-course/numerical-data)

- ここから：`How a model ingests data using feature vectors`
- ここまで：`Qualities of good numerical features`
- `Normalization`、`Binning`、`Missing data`を含めます。
- 各ページの`Check your understanding`へ回答します。

確認すること：欠損補完、外れ値処理、標準化、対数変換、区間化について、
必要になるデータの形と、木モデル・線形モデルへの影響を整理します。

### 事前：設定探索を正しく評価する（約60分）

資料：[scikit-learn MOOC「Hyperparameter tuning」](https://inria.github.io/scikit-learn-mooc/tuning/parameter_tuning_module_intro.html)

1. ここから：`Set and get hyperparameters in scikit-learn`
2. `Exercise M3.01`を行います。
3. ここから：`Hyperparameter tuning by grid-search`
4. ここまで：`Evaluation and hyperparameter tuning`
5. `Exercise M3.02`を行い、解答は実行後に確認します。

確認すること：モデルのパラメータとハイパーパラメータ、Grid SearchとRandomized Search、
探索用スコアと最終確認用スコアの違いを書きます。

### 復習：探索と評価を分ける（約30分）

[scikit-learn MOOC「Evaluating model performance」](https://inria.github.io/scikit-learn-mooc/evaluation/evaluation_module_intro.html)の
`Nested cross-validation`から`Quiz M7.03`までを読みます。

追加演習：同じ検証データで設定を10通り、100通り試した結果を比べます。
試行回数が増えるほど、最良スコアをそのまま最終性能と見なせない理由を説明します。

### 復習：重要度と再現性（約45分）

1. [scikit-learn「Permutation feature importance」](https://scikit-learn.org/stable/modules/permutation_importance.html)
   - ここから：`Outline of the permutation importance algorithm`
   - ここまで：`Misleading values on strongly correlated features`
2. [scikit-learn「Common pitfalls」](https://scikit-learn.org/stable/common_pitfalls.html)
   - ここから：`Controlling randomness`
   - ここまで：冒頭の`Recommendation summary`

追加演習：変更内容、乱数、交差検証、平均F1、標準偏差、実行時間を1行にした実験表を作ります。
重要度が低い列を「原因ではない」と断定できない理由も書きます。

## Appendix：表データ以外を手元で試す

Appendixは全5回の終了後に、興味のあるものを1つ選びます。外部APIやGPUは使いません。

### 画像認識

[scikit-learn「load_digits」](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html)の
`Parameters`から`Examples`までを読みます。`images`と`data`の形を比べ、8×8の画像が64個の数値へ変わることを確認してから、
[画像認識Notebook](../appendix/image-recognition.ipynb)を実行します。

確認すること：画像1枚、1行の特徴量、1個の正解ラベルがどのように対応しているか説明します。

### 音声認識の入口

[NumPy「Discrete Fourier Transform」](https://numpy.org/doc/stable/reference/routines.fft.html)の
`Background information`から`Implementation details`までを読み、
[音声認識Notebook](../appendix/audio-recognition.ipynb)を実行します。数式の導出は追わず、時間方向の波形を周波数ごとの強さへ変える目的をつかみます。

確認すること：音の高さを変えたとき、最も強い周波数がどちらへ動くか予想してからコードを動かします。

### 自然言語処理

[scikit-learn「Text feature extraction」](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction)の
`The Bag of Words representation`から`Tf–idf term weighting`までを読み、
[自然言語処理Notebook](../appendix/nlp.ipynb)を実行します。

確認すること：文章をそのままモデルへ渡せない理由と、単語の出現回数を数値にする利点・弱点を1つずつ書きます。
