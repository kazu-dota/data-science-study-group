"""第2回：scikit-learn、分類、回帰。"""

from course_content.builder import code, external_study, markdown

TITLE = "第2回：scikit-learnと機械学習"
SUMMARY = "回帰と分類の違いを知り、fitとpredictで2種類の予測モデルを動かします。"

CELLS = [
    external_study(2),
    markdown("## 学習の流れ\n\n1. 予測する対象と時点を決める\n2. 数値列とカテゴリ列を前処理する\n3. 回帰と分類を同じ手順で学習する\n4. 単純な予測と比べる\n5. 未知の1件を予測する"),
    code(
        """
        import pandas as pd
        from sklearn.compose import make_column_transformer
        from sklearn.dummy import DummyClassifier, DummyRegressor
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LinearRegression, LogisticRegression
        from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import OneHotEncoder, StandardScaler

        data = pd.read_csv(DATA / "compound_experiments.csv")
        numeric_features = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
        categorical_features = ["solvent", "catalyst", "scaffold_group"]
        features = [*numeric_features, *categorical_features]

        def build_preprocessor():
            return make_column_transformer(
                (make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), numeric_features),
                (make_pipeline(
                    SimpleImputer(strategy="most_frequent"),
                    OneHotEncoder(handle_unknown="ignore"),
                ), categorical_features),
            )
        """
    ),
    markdown("## 予測問題と列の役割\n\n回帰では収率、分類では活性を予測します。`post_assay_signal`と`purity_pct`は測定後に分かるため、予測時点では使いません。IDも予測の手掛かりから外します。"),
    markdown("## 共通する6つの手順\n\n1. 特徴量`X`と目的変数`y`を決める\n2. 学習用と検証用に分ける\n3. 欠損補完・標準化・カテゴリ変換をPipelineに入れる\n4. `fit`で学習する\n5. `predict`で予測する\n6. 未学習データで基準モデルと比べる"),
    markdown("## 1. 回帰：収率を予測する\n\n収率`yield_pct`は連続した数値なので回帰を使います。"),
    code(
        """
        X = data[features]
        y_yield = data["yield_pct"]
        X_train, X_valid, y_train, y_valid = train_test_split(
            X, y_yield, test_size=0.25, random_state=42
        )

        regression_model = make_pipeline(
            build_preprocessor(),
            LinearRegression(),
        )
        regression_model.fit(X_train, y_train)
        yield_prediction = regression_model.predict(X_valid)
        print("予測例:", yield_prediction[:5].round(1))
        """
    ),
    markdown("## 単純な予測と比べる\n\n平均値を答えるだけのモデルより誤差が小さいか確認します。MAEは平均で何ポイント外したかを表します。"),
    code(
        """
        dummy_regression = DummyRegressor(strategy="mean").fit(X_train, y_train)
        dummy_prediction = dummy_regression.predict(X_valid)
        print("平均だけのMAE:", round(mean_absolute_error(y_valid, dummy_prediction), 2))
        print("線形回帰のMAE:", round(mean_absolute_error(y_valid, yield_prediction), 2))
        """
    ),
    markdown("## 2. 分類：活性の有無を予測する\n\n`active`は0か1なので分類を使います。分割時に`stratify`を指定し、活性の割合をそろえます。"),
    code(
        """
        y_active = data["active"]
        X_train, X_valid, y_train, y_valid = train_test_split(
            X, y_active, test_size=0.25, random_state=42, stratify=y_active
        )

        classification_model = make_pipeline(
            build_preprocessor(),
            LogisticRegression(max_iter=1000),
        )
        classification_model.fit(X_train, y_train)
        active_prediction = classification_model.predict(X_valid)
        """
    ),
    markdown("## 分類結果を確認する\n\naccuracyは全体の正解率、F1は活性を見つける力と空振りの少なさを両方見ます。"),
    code(
        """
        dummy_classification = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
        dummy_prediction = dummy_classification.predict(X_valid)
        print("多数派だけのF1:", round(f1_score(y_valid, dummy_prediction), 3))
        print("分類モデルのaccuracy:", round(accuracy_score(y_valid, active_prediction), 3))
        print("分類モデルのF1:", round(f1_score(y_valid, active_prediction), 3))
        """
    ),
    markdown("## 1件を予測する\n\n検証データの先頭1件について、活性になる確率を表示します。"),
    code(
        """
        one_sample = X_valid.iloc[[0]]
        probability = classification_model.predict_proba(one_sample)[0, 1]
        print("実際の答え:", y_valid.iloc[0])
        print(f"活性の予測確率: {probability:.1%}")
        print("学習時に使った列:", one_sample.columns.tolist())
        """
    ),
    markdown("## 演習\n\nカテゴリ列を使う場合と数値列だけの場合のF1を比べます。次に、`post_assay_signal`を使うと高得点でも運用できない理由を、予測時点という言葉を使って説明してください。"),
    markdown("## 到達確認\n\n1. 回帰と分類の目的変数を区別できるか\n2. 数値列とカテゴリ列に必要な前処理を説明できるか\n3. Pipelineが学習データだけで前処理を学ぶ理由を説明できるか\n4. 単純な予測との比較と、リーク列を除く判断ができるか"),
]
