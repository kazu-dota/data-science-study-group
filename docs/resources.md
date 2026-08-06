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
