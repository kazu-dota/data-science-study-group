"""合成データと全15回のNotebookを再生成する。

公開可能な架空データだけを使い、乱数シードを固定して再現性を保つ。
"""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
LESSONS_DIR = ROOT / "lessons"


def markdown(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": dedent(text).strip() + "\n"}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": dedent(text).strip() + "\n",
    }


def notebook(title: str, question: str, cells: list[dict]) -> dict:
    intro = markdown(
        f"""
        # {title}

        **今日の問い：{question}**

        上から順に実行してください。`TRY`は全員、`CHANGE`は値を1つ変える練習、
        `CHALLENGE`は余裕がある人向けです。分からないコードは、セル全体ではなく
        気になる数行をM365 Copilotへ貼って相談します。
        """
    )
    setup = code(
        """
        from pathlib import Path

        def find_repo_root(start=Path.cwd()):
            for candidate in [start, *start.parents]:
                if (candidate / "pyproject.toml").exists():
                    return candidate
            raise FileNotFoundError("pyproject.tomlがある勉強会フォルダ内で実行してください")

        ROOT = find_repo_root()
        DATA = ROOT / "data"
        print("教材フォルダ:", ROOT)
        """
    )
    return {
        "cells": [intro, setup, *cells],
        "metadata": {
            "kernelspec": {"display_name": "Python 3 (uv)", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def write_notebook(folder: str, content: dict) -> None:
    path = LESSONS_DIR / folder / "lesson.ipynb"
    for index, cell in enumerate(content["cells"]):
        cell["id"] = f"cell-{index:02d}"
    path.write_text(json.dumps(content, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def make_dataset() -> pd.DataFrame:
    rng = np.random.default_rng(20260727)
    n = 420
    scaffold_names = np.array([f"S{i:02d}" for i in range(1, 13)])
    scaffold = rng.choice(scaffold_names, n)
    scaffold_index = np.array([int(value[1:]) - 1 for value in scaffold])

    smiles_table = np.array([
        "CCO", "CC(=O)O", "c1ccccc1", "CCN", "CCCO", "CC(C)O",
        "c1ccncc1", "CC(=O)N", "O=C(O)c1ccccc1", "CCOC(=O)C", "CN(C)C", "CC(C)C(=O)O",
    ])
    mw_table = np.array([46.1, 60.1, 78.1, 45.1, 60.1, 60.1, 79.1, 59.1, 122.1, 102.1, 59.1, 88.1])
    logp_table = np.array([-0.3, -0.3, 2.1, -0.6, 0.3, 0.1, 0.7, -1.3, 1.4, 0.2, -0.4, 0.8])
    tpsa_table = np.array([20.2, 37.3, 0.0, 26.0, 20.2, 20.2, 25.8, 43.1, 37.3, 26.3, 3.2, 37.3])
    hbd_table = np.array([1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1])
    rot_table = np.array([0, 0, 0, 0, 1, 0, 0, 0, 1, 2, 0, 1])

    solvents = np.array(["EtOH", "MeOH", "EtOAc", "Water", "THF"])
    catalysts = np.array(["Cat-A", "Cat-B", "Cat-C", "None"])
    solvent = rng.choice(solvents, n, p=[0.24, 0.20, 0.20, 0.16, 0.20])
    catalyst = rng.choice(catalysts, n, p=[0.28, 0.25, 0.22, 0.25])
    temperature = rng.normal(75, 18, n).clip(20, 130)
    reaction_time = rng.lognormal(mean=1.25, sigma=0.55, size=n).clip(0.5, 24)
    concentration = rng.normal(0.50, 0.16, n).clip(0.08, 1.00)

    scaffold_effect = np.array([-5, 3, 7, -2, 5, -7, 1, 8, -4, 4, -1, 6])[scaffold_index]
    solvent_effect = pd.Series(solvent).map({"EtOH": 3, "MeOH": 1, "EtOAc": 5, "Water": -7, "THF": 4}).to_numpy()
    catalyst_effect = pd.Series(catalyst).map({"Cat-A": 9, "Cat-B": 5, "Cat-C": 2, "None": -9}).to_numpy()
    temp_effect = 18 * np.exp(-((temperature - 78) ** 2) / 650)
    time_effect = 5 * np.log1p(reaction_time)
    noise = rng.normal(0, 6, n)
    yield_pct = (24 + scaffold_effect + solvent_effect + catalyst_effect + temp_effect + time_effect - 18 * abs(concentration - 0.48) + noise).clip(2, 98)

    logit = (yield_pct - 58) / 8 + 0.45 * (logp_table[scaffold_index] - 0.3) - 0.018 * (tpsa_table[scaffold_index] - 25)
    probability = 1 / (1 + np.exp(-logit))
    active = rng.binomial(1, probability)
    post_assay_signal = (0.12 + 0.78 * active + rng.normal(0, 0.045, n)).clip(0, 1)
    purity_pct = (yield_pct + 12 + rng.normal(0, 4, n)).clip(20, 99.9)

    dates = pd.Timestamp("2025-01-06") + pd.to_timedelta(rng.integers(0, 300, n), unit="D")
    batch = np.array([f"B{value:02d}" for value in rng.integers(1, 19, n)])
    df = pd.DataFrame({
        "sample_id": [f"CMP-{i:04d}" for i in range(1, n + 1)],
        "experiment_date": dates.astype(str),
        "batch_id": batch,
        "scaffold_group": scaffold,
        "smiles": smiles_table[scaffold_index],
        "solvent": solvent,
        "catalyst": catalyst,
        "temperature_c": np.round(temperature, 1),
        "reaction_time_h": np.round(reaction_time, 2),
        "concentration_m": np.round(concentration, 3),
        "molecular_weight": mw_table[scaffold_index],
        "logp": logp_table[scaffold_index],
        "tpsa": tpsa_table[scaffold_index],
        "h_bond_donors": hbd_table[scaffold_index],
        "rotatable_bonds": rot_table[scaffold_index],
        "yield_pct": np.round(yield_pct, 1),
        "active": active,
        "post_assay_signal": np.round(post_assay_signal, 3),
        "purity_pct": np.round(purity_pct, 1),
    })

    for column, fraction in {"solvent": 0.03, "temperature_c": 0.04, "concentration_m": 0.05, "logp": 0.03, "tpsa": 0.03}.items():
        index = rng.choice(df.index, int(n * fraction), replace=False)
        df.loc[index, column] = np.nan
    df.loc[5, "temperature_c"] = 180.0
    df.loc[17, "reaction_time_h"] = 72.0
    return df


def write_data(df: pd.DataFrame) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(DATA_DIR / "compound_experiments.csv", index=False)
    competition = DATA_DIR / "local_competition"
    competition.mkdir(exist_ok=True)
    rng = np.random.default_rng(13014)
    test_index = rng.choice(df.index, 105, replace=False)
    test = df.loc[test_index].copy().sort_values("sample_id")
    train = df.drop(test_index).copy().sort_values("sample_id")
    excluded = ["yield_pct", "post_assay_signal", "purity_pct"]
    feature_columns = [column for column in df.columns if column not in [*excluded, "active"]]
    train[[*feature_columns, "active"]].to_csv(competition / "train.csv", index=False)
    test[feature_columns].to_csv(competition / "test.csv", index=False)
    test[["sample_id", "active"]].to_csv(competition / "instructor_answers.csv", index=False)
    pd.DataFrame({"sample_id": test["sample_id"], "active": 0}).to_csv(competition / "sample_submission.csv", index=False)


def common_load_cell() -> dict:
    return code(
        """
        import pandas as pd

        df = pd.read_csv(DATA / "compound_experiments.csv")
        print(f"{len(df)}行 × {len(df.columns)}列")
        df.head()
        """
    )


def build_notebooks() -> None:
    write_notebook("01-kickoff", notebook(
        "第1回：予測モデルを動かしてみる",
        "予測モデルは、データを受け取って何を返しているのか。",
        [
            common_load_cell(),
            markdown("""## まず完成済みモデルを動かす\n\n`X`はモデルへ渡す特徴量、`y`は答えとなる目的変数です。最初は細部を暗記せず、`fit`と`predict`の前後で何が入出力されるかを見ます。"""),
            code("""
                from sklearn.model_selection import train_test_split
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.metrics import accuracy_score

                features = ["molecular_weight", "logp", "tpsa", "h_bond_donors", "rotatable_bonds"]
                X = df[features].fillna(df[features].median())
                y = df["active"]
                X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
                model = RandomForestClassifier(n_estimators=100, max_depth=4, random_state=42)
                model.fit(X_train, y_train)
                prediction = model.predict(X_valid)
                print("検証データの正解率:", round(accuracy_score(y_valid, prediction), 3))
                pd.DataFrame({"実際": y_valid.head(8), "予測": prediction[:8]})
            """),
            markdown("""## TRY\n\n`X_valid.iloc[[0]]`をモデルへ渡し、1試料の予測を見ます。予測`0`は非活性、`1`は活性を表します。"""),
            code("""
                one_sample = X_valid.iloc[[0]]
                print("入力した特徴量")
                display(one_sample)
                print("予測クラス:", model.predict(one_sample)[0])
                print("活性である確率:", round(model.predict_proba(one_sample)[0, 1], 3))
            """),
            markdown("""## CHANGE\n\n`max_depth=4`を`2`または`8`へ変え、正解率がどう変わるか試します。値を変えた理由と結果を1行で残してください。\n\n## ASK COPILOT\n\n`fit`と`predict_proba`の違いを、測定装置の校正と未知試料の測定にたとえて説明してもらいます。\n\n## まとめ\n\n- 特徴量はモデルへ渡す情報\n- 目的変数は予測したい答え\n- `fit`で関係を学び、`predict`で未知データを予測する""")
        ]
    ))

    write_notebook("02-python-with-copilot", notebook(
        "第2回：Pythonを読み、Copilotと少し変える",
        "分からないコードを、どうやって小さく理解するか。",
        [
            markdown("""## 変数・リスト・辞書\n\n化学実験の小さな記録をPythonの値として表します。"""),
            code("""
                sample_name = "CMP-0001"
                temperatures = [60, 75, 90]
                experiment = {"sample_id": sample_name, "solvent": "EtOH", "active": 1}
                print(type(sample_name), sample_name)
                print(type(temperatures), temperatures)
                print(type(experiment), experiment)
            """),
            markdown("""## TRY：`for`と`if`を読む\n\n実行前に、何行表示されるか予想します。"""),
            code("""
                for temperature in temperatures:
                    if temperature >= 75:
                        label = "高温条件"
                    else:
                        label = "低温条件"
                    print(temperature, label)
            """),
            markdown("""## 関数は処理に名前を付けるもの"""),
            code("""
                def celsius_to_kelvin(celsius):
                    return celsius + 273.15

                converted = [celsius_to_kelvin(value) for value in temperatures]
                print(converted)
            """),
            markdown("""## TRY：エラーを省略せず読む"""),
            code("""
                try:
                    temperatures[10]
                except Exception as error:
                    print(type(error).__name__)
                    print(error)
            """),
            markdown("""## CHANGE\n\n`temperatures`へ温度を1つ追加し、表示と変換結果を確認します。\n\n## ASK COPILOT\n\n気になるセルを貼り、「各行の実行後に変数の型と中身がどうなるか、表で説明してください」と依頼します。提案された変更は1つずつ試します。""")
        ]
    ))

    write_notebook("03-pandas", notebook(
        "第3回：pandasで表データに触る",
        "初めて見る表データを受け取ったら、最初に何を見るか。",
        [
            common_load_cell(),
            markdown("""## TRY：最初の健康診断\n\n行数・列数、列名、データ型、欠損数を順番に確認します。"""),
            code("""
                print("形:", df.shape)
                display(pd.DataFrame({"データ型": df.dtypes, "欠損数": df.isna().sum()}))
                display(df.select_dtypes(include="number").describe().T)
            """),
            markdown("""## 行と列を選ぶ"""),
            code("""
                columns = ["sample_id", "solvent", "temperature_c", "yield_pct", "active"]
                display(df.loc[:4, columns])
                high_yield = df.loc[df["yield_pct"] >= 75, columns]
                print("収率75%以上:", len(high_yield), "件")
                high_yield.head()
            """),
            markdown("""## TRY：カテゴリごとに比べる"""),
            code("""
                solvent_summary = (
                    df.groupby("solvent", dropna=False)
                      .agg(件数=("sample_id", "size"), 平均収率=("yield_pct", "mean"), 活性率=("active", "mean"))
                      .sort_values("平均収率", ascending=False)
                )
                solvent_summary.round(2)
            """),
            markdown("""## CHANGE\n\n`solvent`を`catalyst`または`scaffold_group`へ変えます。順位が変わる理由をデータだけから断定せず、仮説として書きます。\n\n## CHALLENGE\n\n`query`または複数条件を使い、「Cat-Aかつ温度80度以上」の行を抽出します。""")
        ]
    ))

    write_notebook("04-eda", notebook(
        "第4回：データ探偵—分布・欠損・外れ値",
        "モデルを作る前に、データの怪しいところをどう見つけるか。",
        [
            common_load_cell(),
            code("""
                import matplotlib.pyplot as plt
                import seaborn as sns
                sns.set_theme(style="whitegrid", font="sans-serif")
            """),
            markdown("""## TRY：1変数の分布を見る"""),
            code("""
                fig, axes = plt.subplots(1, 2, figsize=(12, 4))
                sns.histplot(data=df, x="yield_pct", bins=20, ax=axes[0])
                axes[0].set_title("収率の分布")
                sns.boxplot(data=df, x="reaction_time_h", ax=axes[1])
                axes[1].set_title("反応時間：外れ値候補を探す")
                plt.tight_layout()
            """),
            markdown("""## 2変数の関係とカテゴリ比較"""),
            code("""
                fig, axes = plt.subplots(1, 2, figsize=(12, 4))
                sns.scatterplot(data=df, x="temperature_c", y="yield_pct", hue="catalyst", alpha=0.65, ax=axes[0])
                axes[0].set_title("温度と収率")
                sns.boxplot(data=df, x="catalyst", y="yield_pct", ax=axes[1])
                axes[1].set_title("触媒別の収率")
                plt.tight_layout()
            """),
            markdown("""## TRY：欠損と怪しい値を表で確認"""),
            code("""
                missing = df.isna().sum().sort_values(ascending=False)
                display(missing[missing > 0].to_frame("欠損数"))
                display(df.nlargest(5, "temperature_c")[["sample_id", "temperature_c", "reaction_time_h", "yield_pct"]])
            """),
            markdown("""## CHANGE\n\n色分けを`catalyst`から`solvent`へ変えます。見え方が変わった点を1つ共有します。\n\n## 注意\n\n外れ値は入力ミスとは限りません。「誰に確認するか」「残す場合に何が起きるか」まで考えます。""")
        ]
    ))

    write_notebook("05-problem-framing", notebook(
        "第5回：何を、いつ、何のために予測するか",
        "モデル構築より前に決めるべきことは何か。",
        [
            common_load_cell(),
            markdown("""## 予測問題を1文にする\n\n例：**実験条件を決める時点で利用できる情報から、収率を予測し、優先して実施する条件を選ぶ。**\n\n`post_assay_signal`、`purity_pct`、`yield_pct`は実験後に得られるため、この時点の説明変数にはできません。"""),
            code("""
                available_at_planning = [
                    "scaffold_group", "solvent", "catalyst", "temperature_c", "reaction_time_h",
                    "concentration_m", "molecular_weight", "logp", "tpsa", "h_bond_donors", "rotatable_bonds",
                ]
                unavailable_at_planning = ["yield_pct", "active", "post_assay_signal", "purity_pct"]
                print("計画時に使える列:", available_at_planning)
                print("実験後に得られる列:", unavailable_at_planning)
            """),
            markdown("""## TRY：単純な予測を基準にする\n\n複雑なモデルより先に、平均値または最頻値だけを返すモデルを作ります。"""),
            code("""
                from sklearn.dummy import DummyRegressor, DummyClassifier
                from sklearn.metrics import mean_absolute_error, accuracy_score
                from sklearn.model_selection import train_test_split

                train, valid = train_test_split(df, test_size=0.25, random_state=42)
                reg = DummyRegressor(strategy="mean").fit(train[["molecular_weight"]], train["yield_pct"])
                cls = DummyClassifier(strategy="most_frequent").fit(train[["molecular_weight"]], train["active"])
                print("平均収率だけで予測したMAE:", round(mean_absolute_error(valid["yield_pct"], reg.predict(valid[["molecular_weight"]])), 2))
                print("多数派だけで予測した正解率:", round(accuracy_score(valid["active"], cls.predict(valid[["molecular_weight"]])), 3))
            """),
            markdown("""## TRY：自分のテーマを整理する\n\n次の7項目を埋めます。\n\n1. 誰が、何の判断に使うか\n2. いつ予測するか\n3. 目的変数\n4. その時点で利用できる説明変数\n5. 利用してはいけない情報\n6. 回帰か分類か\n7. 単純な基準は何か\n\n## ASK COPILOT\n\n曖昧な点を推測で埋めず、確認質問として返すよう依頼します。""")
        ]
    ))

    # 第6回以降は同じデータを使い、評価・改善・模擬コンペへ段階的に進む。
    write_notebook("06-validation-leakage", notebook(
        "第6回：モデルは本当に当たっているか",
        "手元のスコアをどこまで信じてよいか。",
        [
            common_load_cell(),
            code("""
                import pandas as pd
                from sklearn.model_selection import train_test_split, GroupShuffleSplit
                from sklearn.tree import DecisionTreeClassifier
                from sklearn.metrics import accuracy_score

                features = ["molecular_weight", "logp", "tpsa", "temperature_c", "reaction_time_h"]
                clean = df.dropna(subset=features)
                X_train, X_valid, y_train, y_valid = train_test_split(clean[features], clean["active"], test_size=0.25, random_state=42, stratify=clean["active"])
            """),
            markdown("""## TRY：木の深さと過学習"""),
            code("""
                rows = []
                for depth in [1, 2, 4, 8, None]:
                    model = DecisionTreeClassifier(max_depth=depth, random_state=42).fit(X_train, y_train)
                    rows.append({
                        "max_depth": str(depth),
                        "学習スコア": accuracy_score(y_train, model.predict(X_train)),
                        "検証スコア": accuracy_score(y_valid, model.predict(X_valid)),
                    })
                pd.DataFrame(rows).round(3)
            """),
            markdown("""## TRY：リークを入れると不自然に良くなる"""),
            code("""
                leak_features = [*features, "post_assay_signal"]
                leaked = df.dropna(subset=leak_features)
                X_train_l, X_valid_l, y_train_l, y_valid_l = train_test_split(leaked[leak_features], leaked["active"], test_size=0.25, random_state=42, stratify=leaked["active"])
                leaked_model = DecisionTreeClassifier(max_depth=3, random_state=42).fit(X_train_l, y_train_l)
                print("リーク列ありの検証スコア:", round(accuracy_score(y_valid_l, leaked_model.predict(X_valid_l)), 3))
                print("post_assay_signalは活性測定後の値なので、計画時の予測には使えません。")
            """),
            markdown("""## CHALLENGE：化合物系列を跨がせない分割"""),
            code("""
                splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
                train_idx, valid_idx = next(splitter.split(clean, groups=clean["scaffold_group"]))
                print("学習側の系列:", sorted(clean.iloc[train_idx]["scaffold_group"].unique()))
                print("検証側の系列:", sorted(clean.iloc[valid_idx]["scaffold_group"].unique()))
            """),
            markdown("""## リーク確認の3問\n\n- その列は予測時点で存在するか\n- 分割より前に全データから平均や変換を学習していないか\n- 同じバッチ・日付・化合物系列が両側へ跨いでいないか""")
        ]
    ))

    write_notebook("07-regression", notebook(
        "第7回：数値を予測する—回帰",
        "連続値の予測モデルを、何と比べればよいか。",
        [
            common_load_cell(),
            code("""
                import numpy as np
                import pandas as pd
                import matplotlib.pyplot as plt
                from sklearn.model_selection import train_test_split
                from sklearn.impute import SimpleImputer
                from sklearn.pipeline import make_pipeline
                from sklearn.dummy import DummyRegressor
                from sklearn.linear_model import LinearRegression
                from sklearn.tree import DecisionTreeRegressor
                from sklearn.ensemble import RandomForestRegressor
                from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

                features = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
                X_train, X_valid, y_train, y_valid = train_test_split(df[features], df["yield_pct"], test_size=0.25, random_state=42)
            """),
            markdown("""## TRY：4モデルを同じ条件で比べる"""),
            code("""
                models = {
                    "平均値": DummyRegressor(),
                    "線形回帰": LinearRegression(),
                    "決定木": DecisionTreeRegressor(max_depth=4, random_state=42),
                    "Random Forest": RandomForestRegressor(n_estimators=150, max_depth=6, random_state=42),
                }
                results, predictions = [], {}
                for name, estimator in models.items():
                    pipeline = make_pipeline(SimpleImputer(strategy="median"), estimator).fit(X_train, y_train)
                    pred = pipeline.predict(X_valid)
                    predictions[name] = pred
                    results.append({"モデル": name, "MAE": mean_absolute_error(y_valid, pred), "RMSE": mean_squared_error(y_valid, pred) ** 0.5, "R2": r2_score(y_valid, pred)})
                pd.DataFrame(results).sort_values("MAE").round(3)
            """),
            markdown("""## 予測と実測、残差を見る"""),
            code("""
                pred = predictions["Random Forest"]
                fig, axes = plt.subplots(1, 2, figsize=(11, 4))
                axes[0].scatter(y_valid, pred, alpha=0.65)
                axes[0].plot([y_valid.min(), y_valid.max()], [y_valid.min(), y_valid.max()], "--")
                axes[0].set(xlabel="実測収率", ylabel="予測収率", title="予測と実測")
                axes[1].scatter(pred, y_valid - pred, alpha=0.65)
                axes[1].axhline(0, linestyle="--")
                axes[1].set(xlabel="予測収率", ylabel="残差（実測-予測）", title="残差")
                plt.tight_layout()
            """),
            code("""
                errors = df.loc[y_valid.index, ["sample_id", "scaffold_group", "catalyst", "yield_pct"]].copy()
                errors["予測"] = pred
                errors["絶対誤差"] = abs(errors["yield_pct"] - errors["予測"])
                errors.nlargest(8, "絶対誤差").round(2)
            """),
            markdown("""## CHANGE\n\n`max_depth=6`を`3`または`10`へ変えます。MAEだけでなく、残差図と大きく外した試料も比較します。""")
        ]
    ))

    write_notebook("08-classification", notebook(
        "第8回：クラスを予測する—分類",
        "正解率だけで十分なのはどんなときか。",
        [
            common_load_cell(),
            code("""
                import numpy as np
                import pandas as pd
                import matplotlib.pyplot as plt
                from sklearn.model_selection import train_test_split
                from sklearn.impute import SimpleImputer
                from sklearn.pipeline import make_pipeline
                from sklearn.linear_model import LogisticRegression
                from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, precision_score, recall_score, f1_score

                features = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
                X_train, X_valid, y_train, y_valid = train_test_split(df[features], df["active"], test_size=0.25, random_state=42, stratify=df["active"])
                model = make_pipeline(SimpleImputer(strategy="median"), LogisticRegression(max_iter=1000)).fit(X_train, y_train)
                probability = model.predict_proba(X_valid)[:, 1]
            """),
            markdown("""## TRY：閾値0.5で混同行列を読む"""),
            code("""
                prediction = (probability >= 0.5).astype(int)
                print("accuracy:", round(accuracy_score(y_valid, prediction), 3))
                print("precision:", round(precision_score(y_valid, prediction), 3))
                print("recall:", round(recall_score(y_valid, prediction), 3))
                print("F1:", round(f1_score(y_valid, prediction), 3))
                ConfusionMatrixDisplay.from_predictions(y_valid, prediction, display_labels=["非活性", "活性"], cmap="Blues")
                plt.title("混同行列")
            """),
            markdown("""## TRY：判定閾値を変える"""),
            code("""
                rows=[]
                for threshold in [0.3, 0.5, 0.7]:
                    pred=(probability >= threshold).astype(int)
                    rows.append({"閾値": threshold, "precision": precision_score(y_valid, pred), "recall": recall_score(y_valid, pred), "F1": f1_score(y_valid, pred)})
                pd.DataFrame(rows).round(3)
            """),
            markdown("""## 話し合い\n\n活性候補を見逃したくない探索段階ならrecall、追試コストが非常に高い絞り込み段階ならprecisionを重く見る、といった使い分けが考えられます。正解は利用場面で変わります。""")
        ]
    ))

    write_notebook("09-preprocessing-pipeline", notebook(
        "第9回：前処理をPipelineにまとめる",
        "数値列とカテゴリ列を、安全に同じモデルへ入れるにはどうするか。",
        [
            common_load_cell(),
            code("""
                from sklearn.model_selection import train_test_split
                from sklearn.compose import ColumnTransformer
                from sklearn.pipeline import Pipeline
                from sklearn.impute import SimpleImputer
                from sklearn.preprocessing import OneHotEncoder, StandardScaler
                from sklearn.linear_model import LogisticRegression
                from sklearn.metrics import classification_report

                numeric = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
                categorical = ["solvent", "catalyst", "scaffold_group"]
                X = df[numeric + categorical]
                y = df["active"]
                X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
            """),
            markdown("""## TRY：列ごとの前処理を組み立てる"""),
            code("""
                numeric_process = Pipeline([
                    ("欠損補完", SimpleImputer(strategy="median")),
                    ("標準化", StandardScaler()),
                ])
                categorical_process = Pipeline([
                    ("欠損補完", SimpleImputer(strategy="most_frequent")),
                    ("one_hot", OneHotEncoder(handle_unknown="ignore")),
                ])
                preprocess = ColumnTransformer([
                    ("数値列", numeric_process, numeric),
                    ("カテゴリ列", categorical_process, categorical),
                ])
                model = Pipeline([
                    ("前処理", preprocess),
                    ("予測", LogisticRegression(max_iter=1000)),
                ])
                model.fit(X_train, y_train)
                print(classification_report(y_valid, model.predict(X_valid), target_names=["非活性", "活性"]))
            """),
            markdown("""## 未知カテゴリでも予測できるか"""),
            code("""
                unknown = X_valid.iloc[[0]].copy()
                unknown["solvent"] = "New-Solvent"
                print("未知カテゴリを含む予測:", model.predict(unknown)[0])
            """),
            markdown("""## CHANGE\n\n数値の欠損補完を`median`から`mean`へ変えます。変更はPipelineの1行だけにし、同じ検証データで比べます。""")
        ]
    ))

    write_notebook("10-model-comparison", notebook(
        "第10回：モデル対決",
        "複雑なモデルは本当にいつも優れているか。",
        [
            common_load_cell(),
            code("""
                import time
                import pandas as pd
                from sklearn.model_selection import train_test_split
                from sklearn.impute import SimpleImputer
                from sklearn.pipeline import make_pipeline
                from sklearn.preprocessing import StandardScaler
                from sklearn.dummy import DummyClassifier
                from sklearn.linear_model import LogisticRegression
                from sklearn.tree import DecisionTreeClassifier
                from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
                from sklearn.metrics import f1_score

                features = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa", "h_bond_donors", "rotatable_bonds"]
                X_train, X_valid, y_train, y_valid = train_test_split(df[features], df["active"], test_size=0.25, random_state=42, stratify=df["active"])
                models = {
                    "Dummy": DummyClassifier(strategy="most_frequent"),
                    "Logistic": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=1000)),
                    "Tree": make_pipeline(SimpleImputer(strategy="median"), DecisionTreeClassifier(max_depth=4, random_state=42)),
                    "Random Forest": make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)),
                    "Gradient Boosting": make_pipeline(SimpleImputer(strategy="median"), HistGradientBoostingClassifier(max_iter=100, random_state=42)),
                }
            """),
            markdown("""## TRY：同じ分割・同じ指標で比較"""),
            code("""
                rows=[]
                for name, model in models.items():
                    start=time.perf_counter()
                    model.fit(X_train, y_train)
                    elapsed=time.perf_counter()-start
                    rows.append({"モデル": name, "検証F1": f1_score(y_valid, model.predict(X_valid)), "学習秒": elapsed})
                comparison=pd.DataFrame(rows).sort_values("検証F1", ascending=False)
                comparison.round({"検証F1": 3, "学習秒": 4})
            """),
            markdown("""## 5人の担当案\n\n1. Dummy：単純基準\n2. Logistic：説明しやすい線形モデル\n3. Tree：1本の決定木\n4. Random Forest：複数の木\n5. Gradient Boosting：前の誤りを順に改善\n\nスコアだけでなく、実行時間、説明しやすさ、安定性を1行ずつ共有します。""")
        ]
    ))

    write_notebook("11-feature-engineering", notebook(
        "第11回：化学の知識を特徴量にする",
        "研究者の知識を、モデルへ渡せる形にするにはどうするか。",
        [
            common_load_cell(),
            markdown("""## TRY：仮説を計算式にする\n\n最適温度78℃からの距離、単位時間あたりの濃度という2つの仮説特徴量を作ります。"""),
            code("""
                engineered = df.copy()
                engineered["temperature_distance"] = abs(engineered["temperature_c"] - 78)
                engineered["concentration_per_hour"] = engineered["concentration_m"] / engineered["reaction_time_h"]
                engineered[["temperature_c", "temperature_distance", "concentration_per_hour"]].head()
            """),
            markdown("""## 同じ検証条件で追加前後を比べる"""),
            code("""
                from sklearn.model_selection import train_test_split
                from sklearn.impute import SimpleImputer
                from sklearn.pipeline import make_pipeline
                from sklearn.ensemble import RandomForestRegressor
                from sklearn.metrics import mean_absolute_error

                base = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
                added = [*base, "temperature_distance", "concentration_per_hour"]
                train_idx, valid_idx = train_test_split(engineered.index, test_size=0.25, random_state=42)
                for name, columns in {"追加前": base, "追加後": added}.items():
                    model = make_pipeline(SimpleImputer(strategy="median"), RandomForestRegressor(n_estimators=150, max_depth=6, random_state=42))
                    model.fit(engineered.loc[train_idx, columns], engineered.loc[train_idx, "yield_pct"])
                    pred = model.predict(engineered.loc[valid_idx, columns])
                    print(name, "MAE:", round(mean_absolute_error(engineered.loc[valid_idx, "yield_pct"], pred), 3))
            """),
            markdown("""## CHALLENGE：RDKitでSMILESから記述子を再計算"""),
            code("""
                try:
                    from rdkit import Chem
                    from rdkit.Chem import Descriptors, Crippen
                    molecule = Chem.MolFromSmiles("CCO")
                    print("エタノールの分子量:", round(Descriptors.MolWt(molecule), 3))
                    print("エタノールのLogP:", round(Crippen.MolLogP(molecule), 3))
                except ImportError:
                    print("RDKitは任意です。計算済みのmolecular_weight、logp、tpsa列で本編を進められます。")
            """),
            markdown("""## CHANGE\n\n自分の化学的仮説を1つ選び、計算式・予測時点・期待する方向を先に書いてから列を作ります。改善しなくても有益な結果です。""")
        ]
    ))

    write_notebook("12-experiment-cycle", notebook(
        "第12回：改善実験を小さく回す",
        "改善した理由を後から説明できる実験とは何か。",
        [
            common_load_cell(),
            code("""
                import pandas as pd
                from sklearn.model_selection import cross_validate, StratifiedKFold
                from sklearn.impute import SimpleImputer
                from sklearn.pipeline import make_pipeline
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.inspection import permutation_importance

                features = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
                X, y = df[features], df["active"]
                cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            """),
            markdown("""## TRY：1要素だけ変えて記録する"""),
            code("""
                rows=[]
                for depth in [3, 6, None]:
                    model=make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=150, max_depth=depth, random_state=42))
                    scores=cross_validate(model, X, y, cv=cv, scoring="f1", return_train_score=True)
                    rows.append({"実験名": f"depth={depth}", "変更点": "max_depthのみ", "学習F1": scores["train_score"].mean(), "検証F1平均": scores["test_score"].mean(), "検証F1標準偏差": scores["test_score"].std()})
                experiment_log=pd.DataFrame(rows)
                experiment_log.round(3)
            """),
            markdown("""## 重要度から次の仮説を考える"""),
            code("""
                best=make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42)).fit(X, y)
                importance=permutation_importance(best, X, y, scoring="f1", n_repeats=10, random_state=42)
                pd.DataFrame({"特徴量": features, "重要度": importance.importances_mean}).sort_values("重要度", ascending=False).round(3)
            """),
            markdown("""## 実験ログの最小項目\n\n- 実験名\n- 変えたもの（1つ）\n- 固定した比較条件\n- 結果の平均とばらつき\n- 気づき\n- 次の仮説\n\nCopilotには案を出してもらい、優先順位と予測時点の妥当性は人が判断します。""")
        ]
    ))

    write_notebook("13-kaggle-kickoff", notebook(
        "第13回：模擬コンペで最初の提出を作る",
        "コンペの説明を、ローカルの分析手順へどう翻訳するか。",
        [
            code("""
                import pandas as pd
                train = pd.read_csv(DATA / "local_competition" / "train.csv")
                test = pd.read_csv(DATA / "local_competition" / "test.csv")
                sample = pd.read_csv(DATA / "local_competition" / "sample_submission.csv")
                print("train:", train.shape, "test:", test.shape, "提出見本:", sample.shape)
                display(train.head(3))
                display(sample.head(3))
            """),
            markdown("""## コンペ説明\n\n- 目的：実験計画時の情報から活性`active`（0/1）を予測する\n- 指標：F1\n- `train.csv`には答えがある\n- `test.csv`には答えがない\n- 提出列は`sample_id`と`active`\n\nKaggle Titanicを使える場合も、最初に同じ4点を確認します。"""),
            code("""
                from sklearn.model_selection import train_test_split
                from sklearn.compose import ColumnTransformer
                from sklearn.pipeline import Pipeline
                from sklearn.impute import SimpleImputer
                from sklearn.preprocessing import OneHotEncoder
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.metrics import f1_score

                target="active"
                drop_columns=["sample_id", "experiment_date", "smiles", target]
                features=[column for column in train.columns if column not in drop_columns]
                numeric=train[features].select_dtypes(include="number").columns.tolist()
                categorical=[column for column in features if column not in numeric]
                preprocess=ColumnTransformer([
                    ("数値", SimpleImputer(strategy="median"), numeric),
                    ("カテゴリ", Pipeline([("補完", SimpleImputer(strategy="most_frequent")), ("one_hot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
                ])
                model=Pipeline([("前処理", preprocess), ("モデル", RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42))])
                X_train, X_valid, y_train, y_valid=train_test_split(train[features], train[target], test_size=0.25, random_state=42, stratify=train[target])
                model.fit(X_train, y_train)
                print("ローカル検証F1:", round(f1_score(y_valid, model.predict(X_valid)), 3))
            """),
            markdown("""## TRY：提出CSVを作り、機械的に検査する"""),
            code("""
                model.fit(train[features], train[target])
                submission=pd.DataFrame({"sample_id": test["sample_id"], "active": model.predict(test[features])})
                assert list(submission.columns) == ["sample_id", "active"]
                assert len(submission) == len(test)
                assert submission["sample_id"].is_unique
                output=ROOT / "workspace" / "submission_baseline.csv"
                submission.to_csv(output, index=False)
                print("保存先:", output)
                submission.head()
            """),
            markdown("""## CHANGE\n\n提出前に変えるのは1点だけです。例：`max_depth=6`を`3`へ変え、ローカル検証がどう変わるか確認します。""")
        ]
    ))

    write_notebook("14-kaggle-improvement", notebook(
        "第14回：模擬Kaggle改善会",
        "限られた時間で、次に何を試すか。",
        [
            code("""
                import pandas as pd
                train=pd.read_csv(DATA / "local_competition" / "train.csv")
                test=pd.read_csv(DATA / "local_competition" / "test.csv")
                answers=pd.read_csv(DATA / "local_competition" / "instructor_answers.csv")
            """),
            markdown("""## 5人の担当\n\n1. 欠損補完\n2. 特徴量（最適温度からの距離）\n3. モデルの深さ\n4. 判定閾値\n5. 誤分類の確認\n\n全員が同じ`random_state=42`とF1を使い、担当箇所以外は変えません。"""),
            code("""
                from sklearn.model_selection import train_test_split
                from sklearn.compose import ColumnTransformer
                from sklearn.pipeline import Pipeline
                from sklearn.impute import SimpleImputer
                from sklearn.preprocessing import OneHotEncoder
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.metrics import f1_score

                improved_train=train.copy()
                improved_test=test.copy()
                for frame in [improved_train, improved_test]:
                    frame["temperature_distance"] = abs(frame["temperature_c"] - 78)
                target="active"
                ignored=["sample_id", "experiment_date", "smiles", target]
                features=[c for c in improved_train.columns if c not in ignored]
                numeric=improved_train[features].select_dtypes(include="number").columns.tolist()
                categorical=[c for c in features if c not in numeric]
                preprocess=ColumnTransformer([
                    ("数値", SimpleImputer(strategy="median"), numeric),
                    ("カテゴリ", Pipeline([("補完", SimpleImputer(strategy="most_frequent")), ("one_hot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
                ])
                model=Pipeline([("前処理", preprocess), ("モデル", RandomForestClassifier(n_estimators=300, max_depth=6, random_state=42))])
                X_train, X_valid, y_train, y_valid=train_test_split(improved_train[features], improved_train[target], test_size=0.25, random_state=42, stratify=improved_train[target])
                model.fit(X_train, y_train)
                print("改善案のローカルF1:", round(f1_score(y_valid, model.predict(X_valid)), 3))
            """),
            code("""
                model.fit(improved_train[features], improved_train[target])
                improved_submission=pd.DataFrame({"sample_id": improved_test["sample_id"], "active": model.predict(improved_test[features])})
                output=ROOT / "workspace" / "submission_improved.csv"
                improved_submission.to_csv(output, index=False)
                local_score=f1_score(answers["active"], answers.merge(improved_submission, on="sample_id", suffixes=("_true", "_pred"))["active_pred"])
                print("模擬Leaderboard F1:", round(local_score, 3))
                print("保存先:", output)
            """),
            markdown("""## 実験ログ\n\n改善しても悪化しても、`変更点 / ローカルF1 / 模擬Leaderboard F1 / 気づき`を1行で記録します。Leaderboardだけ改善し、ローカル検証が悪化した案は慎重に扱います。""")
        ]
    ))

    write_notebook("15-show-and-tell", notebook(
        "第15回：Show & Tellと自社データへの橋渡し",
        "自社データで始めるなら、最初の小さな一歩は何か。",
        [
            markdown("""## 最初から再実行できるか\n\n第14回Notebookを`Kernel`→`Restart Kernel and Run All Cells`で実行し、提出CSVが同じ手順で作れることを確認します。"""),
            code("""
                import pandas as pd
                experiment_data=pd.read_csv(DATA / "compound_experiments.csv")
                print("共有する候補")
                print("データ件数:", len(experiment_data))
                print("活性率:", round(experiment_data["active"].mean(), 3))
                print("収率の中央値:", experiment_data["yield_pct"].median())
            """),
            markdown("""## 1人5分のShow & Tell\n\n次のうち1つを選びます。\n\n- 面白かった図\n- 改善した実験\n- 悪化したが学びがあった実験\n- Copilotへの良かった聞き方\n- 自社テーマへ持ち帰りたい考え方\n\n完成度は競いません。"""),
            markdown("""## 自社テーマ1枚シート\n\n機密情報や実データは書かず、一般化した表現で埋めます。\n\n| 項目 | 記入内容 |\n|---|---|\n| 利用者と判断 | 誰が何を決めるか |\n| 予測時点 | いつ予測するか |\n| 目的変数 | 何を予測するか |\n| 説明変数候補 | その時点で得られる情報 |\n| 使えない情報 | 未来情報、測定後情報、機密上使えない情報 |\n| 評価方法 | 指標と分割単位 |\n| 単純な基準 | 平均、最頻値、現在の判断方法など |\n| 最初の実験 | 1〜2週間で試せる小さな範囲 |\n\n## 最後の確認\n\n良いモデルを作ることより、**何を予測し、どう評価し、何を1つ変えたか説明できること**を持ち帰ります。""")
        ]
    ))


def main() -> None:
    df = make_dataset()
    write_data(df)
    build_notebooks()
    print(f"generated: {len(df)} rows and 15 notebooks")


if __name__ == "__main__":
    main()
