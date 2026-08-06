"""第1回：Python、pandas、NumPy。"""

from course_content.builder import code, external_study, markdown

TITLE = "第1回：Pythonの基礎とpandas・NumPy"
SUMMARY = "短いコードを動かしながら、表データを読み、選び、集計できるようになります。"

CELLS = [
    markdown("## 学習の流れ\n\n1. Pythonで処理の順序を書く\n2. NumPyで同じ計算をまとめて行う\n3. pandasで表を読み、選択・加工・集計する\n4. 要約統計とグラフでデータの特徴を調べる"),
    external_study(1),
    markdown("## 1. Pythonの変数とリスト\n\n`=`の右側の値に、左側の名前を付けます。"),
    code(
        """
        experiment_name = "活性スクリーニング"
        temperatures = [60, 70, 80, 90]
        print(experiment_name)
        print("条件数:", len(temperatures))
        print("最初の温度:", temperatures[0])
        """
    ),
    markdown("## 2. 繰り返しと条件分岐\n\n`for`でリストを順番に取り出し、`if`で条件を分けます。"),
    code(
        """
        for temperature in temperatures:
            if temperature >= 80:
                print(temperature, "℃: 高温条件")
            else:
                print(temperature, "℃: 低温条件")
        """
    ),
    markdown("## 3. 処理を関数にする\n\nよく使う計算に名前を付けると、同じコードを繰り返さずに済みます。"),
    code(
        """
        def celsius_to_kelvin(celsius):
            return celsius + 273.15

        for temperature in temperatures:
            print(temperature, "℃ =", celsius_to_kelvin(temperature), "K")
        """
    ),
    markdown("## 4. NumPyでまとめて計算する\n\n配列全体への計算や条件抽出を、短く書けます。"),
    code(
        """
        import numpy as np

        temperature_array = np.array(temperatures)
        kelvin = temperature_array + 273.15
        print("形:", temperature_array.shape, "データ型:", temperature_array.dtype)
        print("平均温度:", temperature_array.mean())
        print("80℃以上:", temperature_array[temperature_array >= 80])
        print("K:", kelvin)
        """
    ),
    markdown("## 5. pandasでCSVを読む\n\n`DataFrame`は行と列を持つ表です。まず件数、列名、先頭行を確認します。"),
    code(
        """
        import pandas as pd

        data = pd.read_csv(DATA / "compound_experiments.csv")
        print("行数・列数:", data.shape)
        print("列名:", data.columns.tolist())
        data.head()
        """
    ),
    markdown("## 6. 列の型と分布を確認する\n\n数値、文字列、日付では使える処理が違います。代表値とばらつきも確認します。"),
    code(
        """
        print(data[["temperature_c", "solvent", "experiment_date"]].dtypes)
        data[["temperature_c", "reaction_time_h", "yield_pct"]].describe().round(2)
        """
    ),
    markdown("## 7. 必要な行と列を選ぶ\n\n角括弧で列を選び、条件式で行を絞ります。複数条件は括弧で囲みます。"),
    code(
        """
        columns = ["sample_id", "catalyst", "temperature_c", "yield_pct", "active"]
        high_yield = data.loc[
            (data["yield_pct"] >= 80) & (data["temperature_c"] <= 100), columns
        ]
        high_yield.head(10)
        """
    ),
    markdown("## 8. 列を作り、グループごとに集計する\n\n元の列から反応速度の目安を作り、触媒ごとの件数・平均・ばらつきを比べます。"),
    code(
        """
        data = data.assign(yield_per_hour=data["yield_pct"] / data["reaction_time_h"])
        catalyst_summary = (
            data.groupby("catalyst", as_index=False)
            .agg(
                件数=("sample_id", "count"),
                平均収率=("yield_pct", "mean"),
                収率の標準偏差=("yield_pct", "std"),
            )
            .sort_values("平均収率", ascending=False)
        )
        catalyst_summary.round(2)
        """
    ),
    markdown("## 9. 欠損と外れ値候補を確認する\n\n空欄と極端な値を数えます。理由を調べる前に、機械的に削除しません。"),
    code(
        """
        missing = data.isna().sum()
        print("欠損数:")
        print(missing[missing > 0].sort_values(ascending=False))
        print("120℃超の件数:", (data["temperature_c"] > 120).sum())
        data.plot.scatter(x="temperature_c", y="yield_pct", alpha=0.6, title="温度と収率")
        """
    ),
    markdown("## 演習\n\n`yield_pct >= 80`を70や90へ変えて件数を比べます。次に、`solvent`ごとの件数・平均・標準偏差を集計し、件数の少ない平均をそのまま比較してよいか考えてください。"),
    markdown("## 到達確認\n\n1. リスト、NumPy配列、DataFrameの役割を説明できるか\n2. 行の抽出、列の作成、グループ集計を使い分けられるか\n3. 平均だけでなく件数・ばらつき・欠損・外れ値候補を確認できるか"),
]
