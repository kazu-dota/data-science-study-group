"""第2回：scikit-learn、分類、回帰。"""

from course_content.builder import code, markdown


TITLE = "第2回：scikit-learnと機械学習"
SUMMARY = "回帰と分類の違いを知り、fitとpredictで2種類の予測モデルを動かします。"

CELLS = [
    markdown("## 機械学習とは\n\n入力と答えの例から関係を学び、新しい入力の答えを予測する方法です。数値を予測する**回帰**と、種類を予測する**分類**を試します。"),
    code(
        """
        import pandas as pd
        from sklearn.dummy import DummyClassifier, DummyRegressor
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LinearRegression, LogisticRegression
        from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler

        data = pd.read_csv(DATA / "compound_experiments.csv")
        features = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
        """
    ),
    markdown("## 共通する5つの手順\n\n1. 説明変数`X`と目的変数`y`を作る\n2. 学習用と検証用に分ける\n3. モデルを作る\n4. `fit`で学習する\n5. `predict`で予測する"),
    markdown("## 1. 回帰：収率を予測する\n\n収率`yield_pct`は連続した数値なので回帰を使います。"),
    code(
        """
        X = data[features]
        y_yield = data["yield_pct"]
        X_train, X_valid, y_train, y_valid = train_test_split(
            X, y_yield, test_size=0.25, random_state=42
        )

        regression_model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
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
            SimpleImputer(strategy="median"),
            StandardScaler(),
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
        """
    ),
    markdown("## 演習\n\n回帰の目的変数を別の数値列へ変える、または分類モデルの`C`を0.1と10に変えて結果を比べます。"),
    markdown("## 振り返り\n\n1. 回帰と分類は何を予測するか\n2. `fit`と`predict`は何をするか\n3. 単純なモデルと比べる理由は何か"),
]
