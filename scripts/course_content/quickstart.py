"""最初に動かす全体像Notebook。"""

from course_content.builder import code, markdown

TITLE = "まず動かす：5回分のコード全体像"
SUMMARY = "化合物の実験条件から活性を予測します。細部は後で学ぶので、まず結果が出る楽しさを体験してください。"

CELLS = [
    markdown(
        """
        ## このNotebookで試すこと

        1. pandasとNumPyでデータを用意する
        2. scikit-learnで分類モデルを学習する
        3. GBDTで予測する
        4. F1と混同行列で評価する
        5. 判定のしきい値を変えて性能を調整する

        分からない行があっても問題ありません。まずは全セルを動かします。
        """
    ),
    code(
        """
        import numpy as np
        import pandas as pd
        from sklearn.ensemble import HistGradientBoostingClassifier
        from sklearn.impute import SimpleImputer
        from sklearn.metrics import ConfusionMatrixDisplay, f1_score
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import make_pipeline

        data = pd.read_csv(DATA / "compound_experiments.csv")
        features = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
        data[features + ["active"]].head()
        """
    ),
    markdown("## 5回で理解する完成コード\n\n番号付きコメントが各回に対応します。"),
    code(
        """
        # 1. pandasで説明変数Xと正解yを用意する
        X = data[features]
        y = data["active"]

        # 2. 未知データで確かめるため、学習用と検証用に分ける
        X_train, X_valid, y_train, y_valid = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )

        # 3. 欠損補完とGBDTをまとめて学習する
        model = make_pipeline(
            SimpleImputer(strategy="median"),
            HistGradientBoostingClassifier(max_iter=150, learning_rate=0.08, random_state=42),
        )
        model.fit(X_train, y_train)

        # 4. 確率とクラスを予測し、F1で評価する
        probability = model.predict_proba(X_valid)[:, 1]
        prediction = (probability >= 0.5).astype(int)
        print("F1:", round(f1_score(y_valid, prediction), 3))

        # 5. しきい値を変え、見逃しと空振りのバランスを調整する
        tuned_prediction = (probability >= 0.35).astype(int)
        print("しきい値0.35のF1:", round(f1_score(y_valid, tuned_prediction), 3))
        """
    ),
    markdown("## 予測結果を見る\n\n混同行列では、正解と予測の組み合わせを件数で確認できます。"),
    code(
        """
        ConfusionMatrixDisplay.from_predictions(
            y_valid, tuned_prediction, display_labels=["非活性", "活性"], cmap="Blues"
        )
        """
    ),
    markdown("## 自分で1か所変える\n\nしきい値を0.20、0.50、0.70に変え、F1がどう動くか確認します。"),
    code(
        """
        for threshold in [0.20, 0.35, 0.50, 0.70]:
            pred = (probability >= threshold).astype(int)
            print(f"しきい値={threshold:.2f}  F1={f1_score(y_valid, pred):.3f}  活性予測={pred.sum()}件")
        """
    ),
    markdown("## 新しい1件を予測する\n\n入力値を変えると予測確率も変わります。"),
    code(
        """
        new_condition = pd.DataFrame([{
            "temperature_c": 78.0,
            "reaction_time_h": 8.0,
            "concentration_m": 0.8,
            "molecular_weight": 310.0,
            "logp": 2.1,
            "tpsa": 65.0,
        }])
        active_probability = model.predict_proba(new_condition)[0, 1]
        print(f"この条件が活性になる予測確率: {active_probability:.1%}")
        """
    ),
    markdown("次の5回では、このコードを前半から順に分解し、自分で書き換えられるようにします。"),
]
