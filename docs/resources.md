# 外部資料の学習ガイド

各回のNotebookは実習の中心ですが、それだけでは背景知識を十分に扱えません。
このガイドでは、無料で読める資料の範囲と、読んだ後に確認することを指定します。

## 使い方

- `事前`は勉強会までに読む必須範囲です。各回の合計で80〜120分を目安にします。
- `復習`は勉強会後に読む範囲です。各回の合計で60〜90分を目安にします。
- 「ここから」「ここまで」は資料内の見出し名です。途中の練習問題も実行します。
- 英語資料はコードと図を先に見ます。本文の要点は勉強会で日本語で確認します。
- 外部資料のコードは、まず資料の環境で読み、教材データへの書き換えは復習で行います。

## 全5回のつながり

| 回 | 前の回から進む問い | 修了時に残すもの |
|---:|---|---|
| 1 | データはどんな形で、欠損や偏りはあるか | データ確認メモと集計表 |
| 2 | 何を、いつ、どの列から予測するか | 予測問題の定義とPipeline |
| 3 | どのモデルが、なぜ良いか | 学習・検証性能と時間の比較表 |
| 4 | その性能を信頼してよいか | 指標・分割方法・誤りの評価メモ |
| 5 | 次に何を変えると改善しそうか | 変更を1つずつ記録した実験表 |

各回は、指定範囲を読む、Notebookを動かす、追加演習を行う、修了時に残すものを確認する、
の順に進めます。前の回の成果物を次の回で使うため、5冊を独立した体験にはしません。

章立てとURLは2026年8月7日に確認しました。提供元の更新で見出しが変わった場合は、
同じ名前に近い章を探し、講師が開講前にリンクを確認してください。

## 第1回：Python、pandas、NumPy

### 事前：Pythonの処理の流れを読む（約60分）

資料：[東京大学「Pythonプログラミング入門」](https://utokyo-ipp.github.io/)

1. [1-2. 変数と関数の基礎](https://utokyo-ipp.github.io/1/1-2.html)
   - ここから：`変数`
   - ここまで：`関数の定義と返値`
2. [2-2. リスト](https://utokyo-ipp.github.io/2/2-2.html)
   - ここから：`リストとインデックス`
   - ここまで：`for文による繰り返しとリスト・タプル`
3. [2-3. 条件分岐](https://utokyo-ipp.github.io/2/2-3.html)
   - ここから：`インデントによる構文`
   - ここまで：`if … elif … else による条件分岐`
4. [3-2. 繰り返し](https://utokyo-ipp.github.io/3/3-2.html)
   - ここから：`for文による繰り返し`
   - ここまで：`range`
5. [3-3. 関数](https://utokyo-ipp.github.io/3/3-3.html)
   - ここから：`関数の定義`
   - ここまで：`返値`

確認すること：`=`、インデント、`if`、`for`、`return`の役割を1文ずつ書き、
「値を1つ変える処理」を関数として書きます。

### 事前：NumPyとpandasの表を読む（約45分）

同じ資料の次の範囲を使います。

1. [5-3. NumPyライブラリ](https://utokyo-ipp.github.io/5/5-3.html)
   - ここから：`配列の構築`
   - ここまで：`ユニバーサル関数`
2. [7-1. pandasライブラリ](https://utokyo-ipp.github.io/7/7-1.html)
   - ここから：`シリーズとデータフレーム`
   - ここまで：`データの統計量`

確認すること：リスト、NumPy配列、DataFrameについて、形、データ型、選択方法、
得意な処理の違いを表にします。

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

修了条件：列の型、代表値、ばらつき、欠損数、外れ値候補を確認し、
行の抽出、列の作成、グループ集計を自分で1回ずつ行います。

## 第2回：scikit-learn、分類、回帰

### 事前：予測問題を決める（約40分）

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

### 事前：予測Pipelineと前処理（約70分）

資料：[scikit-learn MOOC「The predictive modeling pipeline」](https://inria.github.io/scikit-learn-mooc/predictive_modeling_pipeline/predictive_modeling_module_intro.html)

1. ここから：`First look at our dataset`
2. ここまで：`Model evaluation using cross-validation`
3. `Exercise M1.01`、`M1.02`、`M1.03`を行い、解答は実行後に確認します。
4. 続けて`Encoding of categorical variables`から
   `Using numerical and categorical variables together`まで読みます。
5. `Exercise M1.04`と`M1.05`を行い、最後に`Wrap-up quiz 1`へ回答します。

確認すること：数値列、カテゴリ列、欠損値へ必要な前処理と、前処理をPipelineへ
含める理由を表にします。

### 復習：線形モデルの予測を読む（約40分）

同じMOOCの`Linear models`を使います。

- ここから：`Intuitions on linear models`
- ここまで：`Linear models for classification`
- `Exercise M4.01`を行い、解答は実行後に確認します。

確認すること：線形回帰とロジスティック回帰について、入力、出力、係数、
予測値または予測確率の関係を図にします。係数の大小を因果関係と解釈しません。

### 復習：過学習とデータリーク（約30分）

1. [scikit-learn MOOC「Selecting the best model」](https://inria.github.io/scikit-learn-mooc/overfit/overfit_module_intro.html)
   - ここから：`Overfitting and underfitting`
   - ここまで：`Cross-validation framework`
2. [scikit-learn「Common pitfalls」](https://scikit-learn.org/stable/common_pitfalls.html)
   - ここから：`Inconsistent preprocessing`
   - ここまで：`How to avoid data leakage`

追加演習：予測時点では分からない列を1つ混ぜてスコアを比較します。
高いスコアが得られても使えない理由と、Pipelineで防げるリーク・防げないリークを書きます。

修了条件：予測対象、予測時点、使える列、成功指標を定義し、数値列とカテゴリ列を
1本のPipelineで処理して、回帰・分類を基準モデルと比較します。

## 第3回：決定木、Random Forest、GBDT

### 事前：1本の決定木を理解する（約45分）

資料：[scikit-learn MOOC「Decision tree models」](https://inria.github.io/scikit-learn-mooc/trees/trees_module_intro.html)

- ここから：`Intuitions on tree-based models`
- ここまで：`Importance of decision tree hyperparameters on generalization`
- 分類の`Exercise M5.01`を行います。回帰の`Exercise M5.02`は復習へ回します。

確認すること：木の深さを増やしたとき、学習データと検証データの成績がどう変わるか書きます。

### 事前：学習曲線と複雑さを読む（約45分）

資料：[scikit-learn MOOC「Selecting the best model」](https://inria.github.io/scikit-learn-mooc/overfit/overfit_module_intro.html)

- ここから：`Validation and learning curves`
- ここまで：`Bias versus variance trade-off`
- `Exercise M2.01`を行い、`Wrap-up quiz 2`へ回答します。

確認すること：学習データと検証データの成績について、木が浅すぎる場合、深すぎる場合、
データを増やした場合の変化を3つの小さな図にします。

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

修了条件：決定木の深さごとに学習F1と検証F1を記録し、過学習・未学習を判断します。
そのうえで、決定木、Random Forest、GBDTから用途に合う1つを、性能と処理時間の両方から選びます。

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

### 事前：グループをまたぐ性能を測る（約35分）

[scikit-learn「Cross-validation」](https://scikit-learn.org/stable/modules/cross_validation.html)の
次の範囲を読みます。

- ここから：`Cross-validation iterators for grouped data`
- ここまで：`Group K-fold`
- 続けて`StratifiedGroupKFold`の説明と最初の例を読みます。

確認すること：患者、装置、店舗、化合物系列のようなまとまりがある場合に、
同じグループを学習側と検証側へ分けない理由を図にします。

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

### 復習：指標から元の行へ戻る（約30分）

Notebookで誤分類表と残差を並べ、次の順に確認します。

1. 最も確信して間違えた分類を5件選ぶ
2. 絶対残差が大きい回帰を5件選ぶ
3. 欠損、外れ値候補、特定グループへの偏りを確認する
4. データ修正、特徴量追加、分割変更のどれを次に試すか1つ選ぶ

正解を知った後で評価対象を除外すると性能を水増しするため、誤りを消す作業にはしません。

### 任意：統計とグラフを補う

[総務省統計局「社会人のためのデータサイエンス入門」](https://www.stat.go.jp/dss/online01.html)の
第2週`統計学の基礎`と第3週`データの見方と表し方`を受講します。
外部サイトへの登録と開講期間の確認が必要なため、本編の必須にはしません。

修了条件：基準モデル、分類・回帰の複数指標、しきい値、交差検証のばらつき、
グループ分割、誤りの元データを確認し、想定利用場面に合う評価方法を1枚にまとめます。

## 第5回：性能を向上させる

### 事前：学習曲線から次の一手を決める（約40分）

第3回でも使った[scikit-learn MOOC「Selecting the best model」](https://inria.github.io/scikit-learn-mooc/overfit/overfit_module_intro.html)を、
改善方法を選ぶ視点で読み直します。

- ここから：`Validation and learning curves`
- ここまで：`Effect of the sample size in cross-validation`
- `Exercise M2.01`は、学習データ量ごとの学習・検証スコアを記録して再実行します。

確認すること：学習側と検証側の差が大きい場合、両方低い場合、データ量とともに検証性能が
伸びている場合について、データ追加、特徴量、モデル複雑度のどれを先に試すか書きます。

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

### 復習：実験記録から判断する（約30分）

次の列を持つ実験表を作ります。

| 列 | 記録する内容 |
|---|---|
| 変更 | 基準から変えた1点 |
| 仮説 | なぜ改善すると考えたか |
| 検証 | 分割方法、指標、乱数 |
| 結果 | 平均、標準偏差、実行時間 |
| 判断 | 採用、保留、不採用と理由 |
| 次 | 次に1つだけ試すこと |

最良スコアだけでなく、悪化した試行も残します。同じ試行の重複と、都合の良い結果だけを選ぶことを防ぎます。

### 発展・任意：学習済みモデルを扱う前の注意（約25分）

[scikit-learn「Model persistence」](https://scikit-learn.org/stable/model_persistence.html)の
`Summary of model persistence methods`から`Workflow Overview`までと、
`Security & Maintainability Limitations`の冒頭を読みます。

確認すること：モデルだけでなく、学習データの参照先、コード、依存パッケージのバージョン、
検証スコアを残す理由と、信頼できないpickle系ファイルを読み込まない理由を書きます。

修了条件：学習曲線から改善方針を立て、特徴量、設定、しきい値を順に比較し、
重要度と誤りを確認します。最終確認用データは最後の1回だけ使い、実験表から採否を説明します。

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
