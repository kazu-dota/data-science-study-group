"""第5回：予測性能を向上させる。"""

from course_content.builder import code, external_study, markdown

TITLE = "第5回：性能を向上させるテクニック"
SUMMARY = "比較条件を固定し、特徴量、モデル設定、しきい値を1つずつ改善します。"

CELLS = [
    external_study(5),
    markdown("## 学習の流れ\n\n1. 基準と最終確認用データを固定する\n2. 学習曲線から改善の方向を考える\n3. 特徴量・モデル設定・しきい値を順に試す\n4. 重要度と誤りを調べる\n5. 変更履歴を残し、最後に1回だけ確認する"),
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
            learning_curve,
            train_test_split,
        )
        from sklearn.pipeline import make_pipeline

        data = pd.read_csv(DATA / "compound_experiments.csv")
        base_features = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
        cv = StratifiedKFold(5, shuffle=True, random_state=42)
        development, final_test = train_test_split(
            data, test_size=0.2, random_state=42, stratify=data["active"]
        )
        print("改善に使う件数:", len(development), "最終確認用:", len(final_test))
        """
    ),
    markdown("## 基準となるモデル\n\n最終確認用データには触れず、改善用データを同じ5分割交差検証で比べます。"),
    code(
        """
        base_model = make_pipeline(
            SimpleImputer(strategy="median"),
            HistGradientBoostingClassifier(max_iter=150, random_state=42),
        )
        base_scores = cross_val_score(
            base_model, development[base_features], development["active"], cv=cv, scoring="f1"
        )
        print(f"基準F1: {base_scores.mean():.3f} ± {base_scores.std():.3f}")
        """
    ),
    markdown("## 学習曲線で改善の方向を考える\n\nデータ量を増やしたときの学習側と検証側のF1を比べます。差が大きいか、両方低いかで次の一手が変わります。"),
    code(
        """
        sizes, train_scores, valid_scores = learning_curve(
            base_model, development[base_features], development["active"],
            train_sizes=[0.25, 0.5, 0.75, 1.0], cv=cv, scoring="f1"
        )
        pd.DataFrame({
            "学習件数": sizes,
            "学習F1": train_scores.mean(axis=1),
            "検証F1": valid_scores.mean(axis=1),
            "検証F1標準偏差": valid_scores.std(axis=1),
        }).round(3)
        """
    ),
    markdown("## 1. 知識から特徴量を作る\n\n温度78℃からの距離と、濃度×反応時間を追加します。元の列は残したまま効果を比べます。"),
    code(
        """
        improved = development.copy()
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
        search_results = pd.DataFrame(search.cv_results_)[
            ["rank_test_score", "mean_test_score", "std_test_score", "params"]
        ].sort_values("rank_test_score")
        search_results.head(5)
        """
    ),
    markdown("## 3. しきい値を調整する\n\n各行が検証側になったときの確率を集めます。この予測をOOF予測と呼び、しきい値選びに使います。"),
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
    markdown("## 4. 重要な列を確認する\n\n改善用データをもう一度分け、列を1つずつ並べ替えたときにF1がどれだけ下がるかを測ります。"),
    code(
        """
        X_train, X_valid, y_train, y_valid = train_test_split(
            improved[improved_features], improved["active"], test_size=0.25,
            random_state=7, stratify=improved["active"]
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
    markdown("## 5. 最後に1回だけ確認する\n\n選んだ特徴量・設定・しきい値を固定し、取り分けておいたデータでF1を確認します。"),
    code(
        """
        final_data = final_test.copy()
        final_data["temperature_distance"] = (final_data["temperature_c"] - 78).abs()
        final_data["concentration_time"] = final_data["concentration_m"] * final_data["reaction_time_h"]

        final_model = search.best_estimator_.fit(improved[improved_features], improved["active"])
        final_probability = final_model.predict_proba(final_data[improved_features])[:, 1]
        final_prediction = final_probability >= best_threshold
        print("最終確認のF1:", round(f1_score(final_data["active"], final_prediction), 3))
        """
    ),
    markdown("## 最終確認後に誤りを調べる\n\n性能を報告した後で誤りを確認し、次の実験候補を作ります。この分析結果で同じ最終確認データへ再調整はしません。"),
    code(
        """
        final_errors = final_data[["sample_id", "scaffold_group", "solvent"]].copy()
        final_errors["正解"] = final_data["active"]
        final_errors["予測確率"] = final_probability
        final_errors["予測"] = final_prediction.astype(int)
        final_errors.loc[final_errors["正解"] != final_errors["予測"]].sort_values("予測確率")
        """
    ),
    markdown("## 演習\n\n特徴量、モデル設定、しきい値のうち1つだけ変更し、変更内容、交差検証の平均F1・標準偏差、実行時間、判断を1行に記録してください。"),
    markdown("## 到達確認\n\n1. 学習曲線から、データ追加とモデル変更のどちらを先に試すか考えられるか\n2. 探索結果の平均とばらつきを読めるか\n3. 特徴量、設定、しきい値を同時に変えず比較できるか\n4. 最終確認データを改善に使い回さない理由を説明できるか\n5. 重要度と誤り分析から次の実験候補を作れるか"),
]
