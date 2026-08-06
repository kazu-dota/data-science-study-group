"""第5回：予測性能を向上させる。"""

from course_content.builder import code, markdown


TITLE = "第5回：性能を向上させるテクニック"
SUMMARY = "比較条件を固定し、特徴量、モデル設定、しきい値を1つずつ改善します。"

CELLS = [
    markdown("## 改善のルール\n\n1. 比較条件を固定する\n2. 変更は1つにする\n3. 良化も悪化も記録する\n4. 最後に未使用データで確認する"),
    code(
        """
        import numpy as np
        import pandas as pd
        from sklearn.ensemble import HistGradientBoostingClassifier
        from sklearn.impute import SimpleImputer
        from sklearn.inspection import permutation_importance
        from sklearn.metrics import f1_score
        from sklearn.model_selection import (
            RandomizedSearchCV,
            StratifiedKFold,
            cross_val_predict,
            cross_val_score,
            train_test_split,
        )
        from sklearn.pipeline import make_pipeline

        data = pd.read_csv(DATA / "compound_experiments.csv")
        base_features = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
        cv = StratifiedKFold(5, shuffle=True, random_state=42)
        """
    ),
    markdown("## 基準となるモデル\n\n以降の変更は、すべて同じ5分割交差検証のF1で比べます。"),
    code(
        """
        base_model = make_pipeline(
            SimpleImputer(strategy="median"),
            HistGradientBoostingClassifier(max_iter=150, random_state=42),
        )
        base_scores = cross_val_score(base_model, data[base_features], data["active"], cv=cv, scoring="f1")
        print(f"基準F1: {base_scores.mean():.3f} ± {base_scores.std():.3f}")
        """
    ),
    markdown("## 1. 知識から特徴量を作る\n\n温度78℃からの距離と、濃度×反応時間を追加します。元の列は残したまま効果を比べます。"),
    code(
        """
        improved = data.copy()
        improved["temperature_distance"] = (improved["temperature_c"] - 78).abs()
        improved["concentration_time"] = improved["concentration_m"] * improved["reaction_time_h"]
        improved_features = [*base_features, "temperature_distance", "concentration_time"]

        feature_scores = cross_val_score(
            base_model, improved[improved_features], improved["active"], cv=cv, scoring="f1"
        )
        print(f"特徴量追加後: {feature_scores.mean():.3f} ± {feature_scores.std():.3f}")
        """
    ),
    markdown("## 2. モデル設定を探索する\n\n候補を限定し、交差検証の内側で良い設定を探します。"),
    code(
        """
        search = RandomizedSearchCV(
            base_model,
            param_distributions={
                "histgradientboostingclassifier__learning_rate": [0.03, 0.05, 0.08, 0.12],
                "histgradientboostingclassifier__max_leaf_nodes": [7, 15, 31, 63],
                "histgradientboostingclassifier__l2_regularization": [0.0, 0.1, 1.0],
            },
            n_iter=8,
            scoring="f1",
            cv=cv,
            random_state=42,
        )
        search.fit(improved[improved_features], improved["active"])
        print("探索後F1:", round(search.best_score_, 3))
        print("設定:", search.best_params_)
        """
    ),
    markdown("## 3. しきい値を調整する\n\n交差検証の検証側だけを集めたOOF確率で、F1が最大になるしきい値を探します。"),
    code(
        """
        oof_probability = cross_val_predict(
            search.best_estimator_, improved[improved_features], improved["active"],
            cv=cv, method="predict_proba"
        )[:, 1]
        thresholds = np.arange(0.20, 0.81, 0.02)
        threshold_scores = [f1_score(improved["active"], oof_probability >= value) for value in thresholds]
        best_threshold = thresholds[int(np.argmax(threshold_scores))]
        print(f"最良しきい値={best_threshold:.2f}, OOF F1={max(threshold_scores):.3f}")
        """
    ),
    markdown("## 4. 重要な列を確認する\n\n検証データで列を1つずつ並べ替え、F1がどれだけ下がるかを測ります。"),
    code(
        """
        X_train, X_valid, y_train, y_valid = train_test_split(
            improved[improved_features], improved["active"], test_size=0.25,
            random_state=42, stratify=improved["active"]
        )
        final_model = search.best_estimator_.fit(X_train, y_train)
        importance = permutation_importance(
            final_model, X_valid, y_valid, scoring="f1", n_repeats=10, random_state=42
        )
        pd.DataFrame({"特徴量": improved_features, "重要度": importance.importances_mean}).sort_values(
            "重要度", ascending=False
        ).round(3)
        """
    ),
    markdown("## 演習\n\n特徴量、モデル設定、しきい値のうち1つだけ変更し、変更前後の平均F1と標準偏差を記録してください。"),
    markdown("## 振り返り\n\n1. 同時に複数条件を変えない理由は何か\n2. 探索も交差検証の内側で行う理由は何か\n3. 並べ替え重要度が答える問いは何か"),
]
