"""第3回：GBDTなどの高度な予測モデル。"""

from course_content.builder import code, markdown

TITLE = "第3回：高度な予測モデル"
SUMMARY = "決定木、Random Forest、GBDTを同じデータで動かし、予測の違いを比べます。"

CELLS = [
    markdown("## 木を組み合わせるモデル\n\n- **決定木**：条件分岐を1本作る\n- **Random Forest**：異なる決定木を並列に作り、多数決する\n- **GBDT**：前の木が間違えた部分を、次の木が順番に補う"),
    code(
        """
        import time

        import matplotlib.pyplot as plt
        import pandas as pd
        from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
        from sklearn.impute import SimpleImputer
        from sklearn.metrics import f1_score
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import make_pipeline
        from sklearn.tree import DecisionTreeClassifier

        data = pd.read_csv(DATA / "compound_experiments.csv")
        features = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
        X_train, X_valid, y_train, y_valid = train_test_split(
            data[features], data["active"], test_size=0.25, random_state=42, stratify=data["active"]
        )
        """
    ),
    markdown("## 3モデルを同じ条件で比べる\n\n欠損補完、学習データ、検証データ、評価指標をそろえます。"),
    code(
        """
        models = {
            "決定木": DecisionTreeClassifier(max_depth=4, random_state=42),
            "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42),
            "GBDT": HistGradientBoostingClassifier(max_iter=150, learning_rate=0.08, random_state=42),
        }

        rows = []
        fitted_models = {}
        for name, estimator in models.items():
            model = make_pipeline(SimpleImputer(strategy="median"), estimator)
            start = time.perf_counter()
            model.fit(X_train, y_train)
            elapsed = time.perf_counter() - start
            prediction = model.predict(X_valid)
            rows.append({"モデル": name, "F1": f1_score(y_valid, prediction), "学習秒": elapsed})
            fitted_models[name] = model

        pd.DataFrame(rows).sort_values("F1", ascending=False).round(3)
        """
    ),
    markdown("## GBDTの予測確率を見る\n\n0か1だけでなく、活性と判断した強さを0〜1の確率で確認します。"),
    code(
        """
        gbdt = fitted_models["GBDT"]
        probability = gbdt.predict_proba(X_valid)[:, 1]
        plt.hist(probability, bins=15, edgecolor="white")
        plt.xlabel("活性の予測確率")
        plt.ylabel("件数")
        plt.title("GBDTの予測確率")
        """
    ),
    markdown("## learning_rateと木の本数\n\n小さな`learning_rate`では1本ずつの修正が控えめになります。その分、木の本数`max_iter`を増やします。"),
    code(
        """
        settings = [(0.20, 50), (0.08, 150), (0.03, 300)]
        for learning_rate, max_iter in settings:
            candidate = make_pipeline(
                SimpleImputer(strategy="median"),
                HistGradientBoostingClassifier(
                    learning_rate=learning_rate, max_iter=max_iter, random_state=42
                ),
            )
            candidate.fit(X_train, y_train)
            score = f1_score(y_valid, candidate.predict(X_valid))
            print(f"learning_rate={learning_rate:.2f}, 木={max_iter:3d}, F1={score:.3f}")
        """
    ),
    markdown("## 任意：XGBoostを試す\n\n`uv sync --extra advanced`を実行した環境だけで動きます。未導入なら自動でスキップします。"),
    code(
        """
        try:
            from xgboost import XGBClassifier

            xgb = make_pipeline(
                SimpleImputer(strategy="median"),
                XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.08, random_state=42),
            )
            xgb.fit(X_train, y_train)
            print("XGBoost F1:", round(f1_score(y_valid, xgb.predict(X_valid)), 3))
        except ImportError:
            print("XGBoostは未導入です。標準のGBDTだけで本編は完了しています。")
        """
    ),
    markdown("## 演習\n\nGBDTの`learning_rate`か`max_iter`を1つだけ変え、F1と学習時間を記録してください。"),
    markdown("## 振り返り\n\n1. Random ForestとGBDTは木をどう組み合わせるか\n2. GBDTの`learning_rate`は何を変えるか\n3. 複雑なモデルが常に良いとは限らない理由は何か"),
]
