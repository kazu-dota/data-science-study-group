"""第4回：予測モデルの評価。"""

from course_content.builder import code, external_study, markdown

TITLE = "第4回：予測モデルを評価する"
SUMMARY = "学習に使っていないデータで性能を測り、分類と回帰の指標を目的に合わせて読みます。"

CELLS = [
    external_study(4),
    markdown("## 学習の流れ\n\n1. 単純な基準と比べる\n2. 分類の混同行列・指標・しきい値を読む\n3. ランダム分割とグループ分割を比べる\n4. 回帰の指標と残差を読む\n5. 誤った行を確認して次の改善案を作る"),
    code(
        """
        import matplotlib.pyplot as plt
        import numpy as np
        import pandas as pd
        from sklearn.dummy import DummyClassifier
        from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
        from sklearn.impute import SimpleImputer
        from sklearn.metrics import (
            ConfusionMatrixDisplay,
            accuracy_score,
            average_precision_score,
            f1_score,
            mean_absolute_error,
            mean_squared_error,
            precision_score,
            r2_score,
            recall_score,
            roc_auc_score,
        )
        from sklearn.model_selection import GroupKFold, StratifiedKFold, cross_val_score, train_test_split
        from sklearn.pipeline import make_pipeline

        data = pd.read_csv(DATA / "compound_experiments.csv")
        features = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
        X = data[features]
        """
    ),
    markdown("## 分類を評価する\n\n多数派だけを答える基準と比べます。accuracyだけでなく、混同行列と複数の指標を並べます。"),
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
        baseline = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)

        print("多数派だけのaccuracy:", round(accuracy_score(y_valid, baseline.predict(X_valid)), 3))
        print("accuracy:", round(accuracy_score(y_valid, prediction), 3))
        print("precision:", round(precision_score(y_valid, prediction), 3))
        print("recall:", round(recall_score(y_valid, prediction), 3))
        print("F1:", round(f1_score(y_valid, prediction), 3))
        print("ROC AUC:", round(roc_auc_score(y_valid, probability), 3))
        print("Average Precision:", round(average_precision_score(y_valid, probability), 3))
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
    markdown("## 誤った行を見る\n\n指標は誤りを要約した数値です。どの行を間違えたか確認し、共通点を探します。"),
    code(
        """
        error_table = data.loc[X_valid.index, ["sample_id", "scaffold_group", "solvent"]].copy()
        error_table["正解"] = y_valid
        error_table["予測確率"] = probability
        error_table["予測"] = prediction
        error_table.loc[error_table["正解"] != error_table["予測"]].sort_values("予測確率")
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
    markdown("## グループをまたいで評価する\n\n同じ化合物系列が学習側と検証側に入ると簡単すぎる場合があります。系列ごと分けた結果と比べます。"),
    code(
        """
        group_cv = GroupKFold(5)
        group_scores = cross_val_score(
            classifier, X, data["active"], groups=data["scaffold_group"], cv=group_cv, scoring="f1"
        )
        print(f"層化5分割: {scores.mean():.3f} ± {scores.std():.3f}")
        print(f"系列別5分割: {group_scores.mean():.3f} ± {group_scores.std():.3f}")
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
    markdown("## 演習\n\n見逃しを減らすしきい値を1つ選び、precisionとrecallを記録します。次に、層化分割と系列別分割の差から、どちらが想定する利用場面に近いか説明してください。"),
    markdown("## 到達確認\n\n1. 基準モデルより良いか確認できるか\n2. precision・recall・F1・ROC AUCを用途に応じて読めるか\n3. データの関係に合わせて分割方法を選べるか\n4. MAE・RMSE・R²と残差を組み合わせて読めるか\n5. 誤った行から次の仮説を作れるか"),
]
