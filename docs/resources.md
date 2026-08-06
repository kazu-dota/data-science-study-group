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
