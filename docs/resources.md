# 参考資料

このリポジトリのNotebookが主教材です。外部資料は、分からない項目を調べるときだけ使います。
最初から全て読む必要はありません。

## 第1回：Python、pandas、NumPy

- [東京大学「Pythonプログラミング入門」](https://utokyo-ipp.github.io/)
  - 変数、リスト、繰り返し、関数を日本語で確認できます。
- [Python公式チュートリアル](https://docs.python.org/ja/3/tutorial/)
  - Pythonの書き方を調べる辞書として使います。
- [NumPy Learn](https://numpy.org/learn/)
  - 配列の作り方や計算の公式案内です。
- [pandas User Guide](https://pandas.pydata.org/docs/user_guide/)
  - 表の選択、集計、欠損値処理を調べる公式資料です。

## 第2回：scikit-learnと機械学習

- [東京大学「Pythonプログラミング入門」7-2 scikit-learn](https://utokyo-ipp.github.io/)
  - 分類と回帰の短い実行例があります。
- [scikit-learn Getting Started](https://scikit-learn.org/stable/getting_started.html)
  - `fit`と`predict`の基本的な使い方を確認できます。
- [scikit-learn MOOC](https://inria.github.io/scikit-learn-mooc/)
  - さらに練習したい人向けの無料教材です。

## 第3回：GBDTなどの予測モデル

- [scikit-learn Ensemble methods](https://scikit-learn.org/stable/modules/ensemble.html)
  - Random ForestとGradient Boostingの公式解説です。
- [XGBoost Python API](https://xgboost.readthedocs.io/en/stable/python/python_api.html)
  - 任意課題でXGBoostを使う場合だけ参照します。

XGBoostは第3回の必須ではありません。試す場合だけ次を実行します。

```powershell
uv sync --extra advanced
```

## 第4回：モデル評価

- [scikit-learn Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html)
  - 分類・回帰の評価指標を調べる公式資料です。
- [scikit-learn Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
  - 交差検証の方法と使い分けを確認できます。
- [機械学習帳](https://chokkan.github.io/mlnote/)
  - 回帰、分類、モデル選択を日本語で学べます。

## 第5回：性能改善

- [scikit-learn Tuning hyper-parameters](https://scikit-learn.org/stable/modules/grid_search.html)
  - 設定探索の公式解説です。
- [scikit-learn Permutation importance](https://scikit-learn.org/stable/modules/permutation_importance.html)
  - 特徴量を並べ替えて影響を測る方法を確認できます。

## Appendix

- [scikit-learn Digits dataset](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html)
  - 画像認識編で使う手書き数字データです。
- [scikit-learn Text feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction)
  - 自然言語処理編で使うTF-IDFの公式解説です。
- [NumPy Discrete Fourier Transform](https://numpy.org/doc/stable/reference/routines.fft.html)
  - 音声認識編で使う周波数分析の公式資料です。
