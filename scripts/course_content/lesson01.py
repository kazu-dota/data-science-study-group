"""第1回：Python、pandas、NumPy。"""

from course_content.builder import code, external_study, markdown

TITLE = "第1回：Pythonの基礎とpandas・NumPy"
SUMMARY = "短いコードを動かしながら、表データを読み、選び、集計できるようになります。"

CELLS = [
    markdown("## 今日できるようになること\n\n- 変数・リスト・繰り返し・関数を使う\n- NumPyでまとめて計算する\n- pandasでCSVを読み、必要な行や列を調べる"),
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
    markdown("## 6. 必要な行と列を選ぶ\n\n角括弧で列を選び、条件式で行を絞ります。"),
    code(
        """
        columns = ["sample_id", "catalyst", "temperature_c", "yield_pct", "active"]
        high_yield = data.loc[data["yield_pct"] >= 80, columns]
        high_yield.head(10)
        """
    ),
    markdown("## 7. グループごとに集計する\n\n触媒ごとの件数と平均収率を比べます。"),
    code(
        """
        catalyst_summary = (
            data.groupby("catalyst", as_index=False)
            .agg(件数=("sample_id", "count"), 平均収率=("yield_pct", "mean"))
            .sort_values("平均収率", ascending=False)
        )
        catalyst_summary.round(1)
        """
    ),
    markdown("## 8. 欠損を確認する\n\n空欄がある列と件数を確認します。勝手に削除せず、まず存在を把握します。"),
    code(
        """
        missing = data.isna().sum()
        missing[missing > 0].sort_values(ascending=False)
        """
    ),
    markdown("## 演習\n\n`yield_pct >= 80`を70や90へ変えて件数を比べます。次に、触媒ではなく`solvent`ごとの平均収率を集計してください。"),
    markdown("## 振り返り\n\n1. リストとNumPy配列は何が違うか\n2. pandasで行を絞る条件はどこに書くか\n3. `groupby`は何をまとめる処理か"),
]
