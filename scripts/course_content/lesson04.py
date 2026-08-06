"""第4回：予測モデルの評価。"""

from course_content.builder import code, markdown


TITLE = "第4回：予測モデルを評価する"
SUMMARY = "未知データで性能を測り、分類と回帰の指標を目的に合わせて読みます。"

CELLS = [
    markdown("## 評価で確認すること\n\n学習データの成績ではなく、学習に使っていないデータの成績を見ます。数値1つだけでなく、どんな間違いがあるかも確認します。"),
    code(
        """
        import matplotlib.pyplot as plt
        import numpy as np
        import pandas as pd
        from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
        from sklearn.impute import SimpleImputer
        from sklearn.metrics import (
            ConfusionMatrixDisplay,
            accuracy_score,
            f1_score,
            mean_absolute_error,
            mean_squared_error,
            precision_score,
            r2_score,
            recall_score,
        )
        from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
        from sklearn.pipeline import make_pipeline

        data = pd.read_csv(DATA / "compound_experiments.csv")
        features = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
        X = data[features]
        """
    ),
    markdown("## 分類を評価する\n\naccuracyだけでは、活性試料の見逃しが分かりません。混同行列と3つの指標を並べます。"),
    code(
        """
        X_train, X_valid, y_train, y_valid = train_test_split(
            X, data["active"], test_size=0.25, random_state=42, stratify=data["active"]
        )
        classifier = make_pipeline(
            SimpleImputer(strategy="median"),
            HistGradientBoostingClassifier(max_iter=150, random_state=42),
        ).fit(X_train, y_train)
        probability = classifier.predict_proba(X_valid)[:, 1]
        prediction = (probability >= 0.5).astype(int)

        print("accuracy:", round(accuracy_score(y_valid, prediction), 3))
        print("precision:", round(precision_score(y_valid, prediction), 3))
        print("recall:", round(recall_score(y_valid, prediction), 3))
        print("F1:", round(f1_score(y_valid, prediction), 3))
        """
    ),
    code(
        """
        ConfusionMatrixDisplay.from_predictions(
            y_valid, prediction, display_labels=["非活性", "活性"], cmap="Blues"
        )
        """
    ),
    markdown("## 判定のしきい値を変える\n\nしきい値を下げると活性を拾いやすくなりますが、空振りも増えます。"),
    code(
        """
        rows = []
        for threshold in np.arange(0.2, 0.81, 0.1):
            pred = (probability >= threshold).astype(int)
            rows.append({
                "しきい値": threshold,
                "precision": precision_score(y_valid, pred, zero_division=0),
                "recall": recall_score(y_valid, pred),
                "F1": f1_score(y_valid, pred),
            })
        pd.DataFrame(rows).round(3)
        """
    ),
    markdown("## 交差検証で分割の偶然を減らす\n\n5通りの分割で評価し、平均とばらつきを確認します。"),
    code(
        """
        cv = StratifiedKFold(5, shuffle=True, random_state=42)
        scores = cross_val_score(classifier, X, data["active"], cv=cv, scoring="f1")
        print("各分割のF1:", scores.round(3))
        print(f"平均={scores.mean():.3f}, 標準偏差={scores.std():.3f}")
        """
    ),
    markdown("## 回帰を評価する\n\nMAEは平均の外れ幅、RMSEは大きな外れをより重く扱い、R²は平均予測からの改善度を示します。"),
    code(
        """
        X_train, X_valid, y_train, y_valid = train_test_split(
            X, data["yield_pct"], test_size=0.25, random_state=42
        )
        regressor = make_pipeline(
            SimpleImputer(strategy="median"),
            HistGradientBoostingRegressor(max_iter=150, random_state=42),
        ).fit(X_train, y_train)
        prediction = regressor.predict(X_valid)
        print("MAE:", round(mean_absolute_error(y_valid, prediction), 2))
        print("RMSE:", round(mean_squared_error(y_valid, prediction) ** 0.5, 2))
        print("R²:", round(r2_score(y_valid, prediction), 3))
        """
    ),
    markdown("## 残差を見る\n\n残差に模様があれば、モデルが捉えていない関係が残っている可能性があります。"),
    code(
        """
        residual = y_valid - prediction
        plt.scatter(prediction, residual, alpha=0.7)
        plt.axhline(0, color="black", linestyle="--")
        plt.xlabel("予測収率")
        plt.ylabel("残差（実測 - 予測）")
        """
    ),
    markdown("## 演習\n\n見逃しを減らしたい場合のしきい値を1つ選び、そのときのprecisionとrecallを記録してください。"),
    markdown("## 振り返り\n\n1. 学習に使っていないデータで評価する理由は何か\n2. precisionとrecallのどちらを重視するかは何で決まるか\n3. MAEとRMSEは大きな誤差をどう扱うか"),
]
