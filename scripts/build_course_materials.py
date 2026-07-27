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


LESSON_META = {
    "01-kickoff": {
        "objectives": ["特徴量・目的変数・学習・予測を、画面上の入出力と結びつける", "クラス予測と確率予測を区別する", "設定を1つ変え、検証結果の変化を言葉にする"],
        "terms": ["特徴量：予測時点でモデルへ渡す情報", "目的変数：予測したい答え", "学習：既知データから関係を推定する処理", "推論：学習済みモデルを未知データへ使う処理"],
        "reading": ["正解率は未知データ役の検証データで確認する", "確率0.8は『必ず活性』ではなく、モデルの確信度として扱う", "設定変更の効果は同じ分割で比べる"],
        "pitfalls": ["学習データの成績を実力だと思う", "1試料の予測だけでモデル全体を判断する", "良い数値が出るまで設定を無計画に変える"],
        "self_study": ["任意の3試料について特徴量・予測クラス・確率を1表にする", "木の深さ2・4・8を比較し、どれを選ぶか2文で書く"],
        "check": ["Xとyはそれぞれ何か", "fitとpredictは何をするか", "検証データが必要なのはなぜか"],
    },
    "02-python-with-copilot": {
        "objectives": ["変数・リスト・辞書・条件分岐・繰り返し・関数を読める", "型と値を表示してコードの状態を確認する", "Copilotの提案を小さく検証する"],
        "terms": ["値：文字列や数値などのデータ", "型：値に対して可能な操作の種類", "関数：入力から出力を作る処理のまとまり", "例外：処理を続けられない理由を伝える仕組み"],
        "reading": ["コードは上から順に状態を変える", "エラーの末尾には原因に近い情報がある", "関数は代表値だけでなく境界値でも試す"],
        "pitfalls": ["Notebookを途中から実行して変数がない", "Copilotの長い修正を一度に採用する", "エラー全文を読まずにセルを繰り返し実行する"],
        "self_study": ["温度の単位変換関数へ型ヒントと説明文を足す", "正常値・負値・文字列の3ケースを試し、期待結果を先に書く"],
        "check": ["listとdictはどう使い分けるか", "ifの条件がFalseのとき何が起こるか", "生成AIのコードを何で確認するか"],
    },
    "03-pandas": {
        "objectives": ["初見データの形・型・欠損・要約統計を確認する", "locで列と条件を明示して抽出する", "groupbyとaggで比較表を作る"],
        "terms": ["DataFrame：行と列を持つ表", "Series：DataFrameの1列に相当するデータ", "欠損値：未測定・不明など値が存在しない状態", "集約：複数行を件数や平均などへまとめる処理"],
        "reading": ["平均だけでなく件数とばらつきを一緒に見る", "行番号とsample_idを混同しない", "カテゴリ別の差は因果関係とは限らない"],
        "pitfalls": ["列の単位や定義を確認せず計算する", "欠損行を知らないまま自動で落とす", "件数が極端に少ない群の平均を強く信じる"],
        "self_study": ["触媒×溶媒の件数・平均収率・標準偏差を表にする", "自分なら毎回使うデータ健康診断を5項目にまとめる"],
        "check": ["shapeの2つの数は何か", "locの行条件と列指定はどこか", "groupby結果に件数が必要なのはなぜか"],
    },
    "04-eda": {
        "objectives": ["単変量・二変量・群別の順でデータを見る", "欠損や外れ値を調査対象として扱う", "図から断定ではなく検証可能な仮説を作る"],
        "terms": ["分布：値がどこにどれだけ存在するか", "外れ値：他と大きく異なる観測値", "相関：2変数が一緒に変化する程度", "EDA：モデル化前に品質と構造を探索する作業"],
        "reading": ["軸・単位・件数を確認してから形を見る", "相関は非線形関係や群ごとの差を隠すことがある", "欠損の発生理由が予測時点と関係するか考える"],
        "pitfalls": ["外れ値を自動削除する", "相関を因果と読む", "見栄えの良い図だけを選ぶ"],
        "self_study": ["数値列の相関ヒートマップから仮説を1つ書く", "外れ値候補2件について確認先・残す場合・除く場合を整理する"],
        "check": ["箱ひげ図で何が分かるか", "欠損率だけでは足りない理由は何か", "良い仮説に必要な次の確認は何か"],
    },
    "05-problem-framing": {
        "objectives": ["利用者・判断・予測時点を1文にする", "目的変数と利用可能な説明変数を分ける", "業務上意味のあるベースラインと指標を決める"],
        "terms": ["予測時点：モデルを実際に使う瞬間", "ベースライン：複雑なモデルと比較する単純な基準", "回帰：連続値を予測する問題", "分類：クラスやカテゴリを予測する問題"],
        "reading": ["スコアより先に誰の判断をどう変えるかを確認する", "未来情報や測定後情報は高性能でも使えない", "誤りの種類ごとの業務コストを考える"],
        "pitfalls": ["入手できる列をすべて使う", "目的変数が測定や運用で不安定", "精度目標だけで利用方法が決まっていない"],
        "self_study": ["自社テーマを機密情報なしで7項目の問題設定へ落とす", "偽陽性・偽陰性または過大・過小予測のコストを書く"],
        "check": ["誰が何を判断するモデルか", "予測時点で本当に得られる列はどれか", "単純基準を超えることにどんな価値があるか"],
    },
    "06-validation-leakage": {
        "objectives": ["学習・検証・テストの役割を区別する", "過学習を学習スコアとの差から見つける", "系列やバッチを意識した分割を設計する"],
        "terms": ["汎化：未知データでも性能を保つこと", "過学習：学習データへ合わせすぎること", "リーク：予測時には得られない情報が学習へ混ざること", "グループ分割：関連試料を同じ側へまとめる分割"],
        "reading": ["検証方法は将来の使われ方を模擬する", "高すぎるスコアはリークを疑うきっかけになる", "平均スコアだけでなく分割ごとのばらつきを見る"],
        "pitfalls": ["前処理を全データで済ませてから分割する", "同じ系列の類似化合物を両側へ入れる", "検証データを何度も見て実質的に学習する"],
        "self_study": ["ランダム分割と系列分割のF1を比較する", "自社データで跨がせてはいけない単位を3候補挙げる"],
        "check": ["検証とテストの違いは何か", "リークを疑う3つの質問は何か", "分割方法を先に決める理由は何か"],
    },
    "07-regression": {
        "objectives": ["MAE・RMSE・R²を異なる視点として読む", "Dummyと複数モデルを同条件で比較する", "残差を群別に調べて次の仮説を作る"],
        "terms": ["MAE：絶対誤差の平均", "RMSE：大きな誤差をより重く扱う指標", "R²：平均予測と比べた当てはまり", "残差：実測値と予測値の差"],
        "reading": ["MAEは目的変数と同じ単位で説明できる", "全体指標が良くても特定系列で外すことがある", "残差の模様は未学習の構造を示すことがある"],
        "pitfalls": ["R²だけで利用可能と判断する", "テストデータでモデルを選ぶ", "大きな誤差を外れ値としてすぐ除く"],
        "self_study": ["触媒別と系列別のMAEを計算する", "MAE 5ポイントが業務上許容できるか利用場面から考える"],
        "check": ["MAEとRMSEは何を違って重視するか", "Dummyより悪い場合に何を見直すか", "残差図に模様があると何を疑うか"],
    },
    "08-classification": {
        "objectives": ["混同行列の4区分を利用場面に結びつける", "precision・recall・F1を使い分ける", "確率と閾値を分けて考える"],
        "terms": ["precision：陽性予測のうち正しかった割合", "recall：実際の陽性を見つけた割合", "F1：precisionとrecallの調和平均", "閾値：確率をクラスへ変換する境界"],
        "reading": ["同じ確率でも閾値によりクラスが変わる", "不均衡データではaccuracyが高くても役立たないことがある", "閾値はモデル学習後にも業務要件から調整できる"],
        "pitfalls": ["常に閾値0.5を使う", "偽陽性と偽陰性のコストを同じとみなす", "検証データで閾値を細かく最適化しすぎる"],
        "self_study": ["0.1刻みの閾値表を作り利用目的に合う点を選ぶ", "探索段階と確証段階で重視する指標を比較する"],
        "check": ["偽陽性・偽陰性はそれぞれ何か", "accuracyが危険な例は何か", "閾値を下げると一般にrecallはどうなるか"],
    },
    "09-preprocessing-pipeline": {
        "objectives": ["列型ごとの前処理を説明する", "前処理とモデルをPipelineとして一体化する", "未知カテゴリと欠損を安全に扱う"],
        "terms": ["欠損補完：欠けた値を規則に基づいて埋める処理", "標準化：尺度を平均0・標準偏差1付近へ揃える処理", "One-Hot：カテゴリを0/1列へ変換する処理", "Pipeline：順序付き処理を1つの推定器として扱う仕組み"],
        "reading": ["fit時に学ぶ値とtransformだけの処理を区別する", "変換後は元より列数が増えることがある", "Pipeline全体を交差検証へ渡す"],
        "pitfalls": ["全データ平均で欠損補完する", "カテゴリを意味のない大小関係へ変換する", "本番の未知カテゴリでエラーになる"],
        "self_study": ["変換後の特徴量名と列数を確認する", "Pipelineあり・なしの手順を図にしてリーク箇所を示す"],
        "check": ["数値列とカテゴリ列で何を変えるか", "Pipelineがリークを防ぎやすい理由は何か", "handle_unknownが必要なのはなぜか"],
    },
    "10-model-comparison": {
        "objectives": ["同じ分割・指標で複数モデルを比較する", "性能・速度・説明性・安定性を合わせて評価する", "学習と検証の差から過学習を読む"],
        "terms": ["線形モデル：特徴量効果を重みの和で表すモデル", "決定木：条件分岐を重ねるモデル", "アンサンブル：複数モデルを組み合わせる方法", "交差検証：分割を変えて性能の安定性を見る方法"],
        "reading": ["1回の勝敗より平均とばらつきを見る", "わずかな改善と複雑化の釣り合いを考える", "目的により最良モデルは変わる"],
        "pitfalls": ["異なる分割で比較する", "モデルごとに異なる指標を報告する", "最も高い1回のスコアだけを採用する"],
        "self_study": ["5-fold CVでF1平均・標準偏差・時間を比較する", "説明重視と性能重視の2用途で推奨モデルを選ぶ"],
        "check": ["公平な比較に固定すべきものは何か", "ばらつきが大きいモデルをどう扱うか", "最高スコア以外の選択理由は何か"],
    },
    "11-feature-engineering": {
        "objectives": ["化学的仮説を再計算可能な特徴量へ変える", "追加前後を同じ条件で比較する", "系列分割と記述子の限界を意識する"],
        "terms": ["特徴量設計：既存情報から予測に役立つ表現を作ること", "記述子：分子構造などを数値で表す量", "アブレーション：要素を足し引きして寄与を調べる比較", "適用領域：モデルが信頼できる入力範囲"],
        "reading": ["特徴量は予測時点で計算できる必要がある", "追加して悪化する結果も仮説検証として価値がある", "類似構造への補間と新規骨格への外挿を区別する"],
        "pitfalls": ["意味を説明できない特徴量を大量追加する", "目的変数由来の値を特徴量にする", "追加前後で分割やモデルも変える"],
        "self_study": ["自分の仮説特徴量を式・期待方向・反証条件とともに記録する", "RDKitが使える場合は3記述子を再計算し既存列と照合する"],
        "check": ["その特徴量はいつ計算できるか", "追加効果をどう公平に比較するか", "新規骨格で性能が落ちる理由は何か"],
    },
    "12-experiment-cycle": {
        "objectives": ["変更を1要素に限定した比較を設計する", "交差検証の平均とばらつきを記録する", "検証データ上の重要度と誤りから次の仮説を選ぶ"],
        "terms": ["実験ログ：変更・条件・結果・解釈を残す記録", "ハイパーパラメータ：学習前に人が決める設定", "permutation importance：列を崩したときの性能低下で寄与を見る方法", "再現性：同じ手順で同じ結果を得られる性質"],
        "reading": ["標準偏差が改善幅より大きくないか確認する", "重要度は因果効果ではない", "仮説は次の実験で反証可能な形にする"],
        "pitfalls": ["同時に複数要素を変える", "学習データ上の重要度だけを見る", "悪化した実験を記録から消す"],
        "self_study": ["実験ログをCSVへ保存し再読込する", "重要度上位1列を外すアブレーションを行う"],
        "check": ["1要素だけ変える理由は何か", "平均と標準偏差をどう読むか", "重要度から断定できないことは何か"],
    },
    "13-kaggle-kickoff": {
        "objectives": ["問題・指標・データ・提出形式を読み解く", "再現可能なベースラインをローカル評価する", "提出CSVを機械的に検査する"],
        "terms": ["Leaderboard：提出結果を順位表示する仕組み", "Public/Private：公開中と最終判定で使う評価データの区分", "submission：指定形式の予測ファイル", "ベースライン：最初に必ず保存する比較起点"],
        "reading": ["testには答えがないことを確認する", "ローカル検証とLeaderboardの役割を分ける", "ID列の順序と一意性を検査する"],
        "pitfalls": ["testの情報へ合わせて特徴量を決める", "提出ファイルのindex列を混入させる", "最初から公開Notebookを丸ごと写す"],
        "self_study": ["データ辞書を自分の言葉で1ページにする", "ベースライン提出後に変更点を1つだけ試す"],
        "check": ["評価指標は何か", "trainとtestの違いは何か", "提出前に検査する3項目は何か"],
    },
    "14-kaggle-improvement": {
        "objectives": ["限られた時間で実験を優先順位付けする", "特徴量・モデル・閾値を分離して評価する", "誤分類を群別に調べて改善仮説を作る"],
        "terms": ["Leaderboard overfitting：順位表へ過度に合わせること", "誤分類分析：外した試料の共通点を調べる作業", "閾値調整：確率からクラスへの境界を変えること", "実験統合：有効な変更を再検証しながら組み合わせること"],
        "reading": ["ローカル改善とLeaderboard改善の一致を確認する", "改善幅が偶然でないか再分割で見る", "誤分類群にデータ不足や分布差がないか調べる"],
        "pitfalls": ["5人の変更を一度に統合する", "Leaderboardだけを目的関数にする", "検証データで選んだ閾値を同じデータで報告する"],
        "self_study": ["系列別の件数・F1・誤分類数を表にする", "最終案をゼロから再実行して同じ提出を作る"],
        "check": ["次の実験を何で優先するか", "ローカルとLeaderboardがずれたら何を疑うか", "改善を統合する順序はどうするか"],
    },
    "15-show-and-tell": {
        "objectives": ["モデルの目的・検証・結果・限界を短く説明する", "失敗を含む改善過程を再現可能に共有する", "自社データでの小さな次の一歩を設計する"],
        "terms": ["モデルカード：用途・データ・評価・限界をまとめた記録", "適用範囲：モデルを使ってよい対象と条件", "再現手順：第三者が同じ結果へ到達する手順", "モニタリング：運用後の入力や性能変化を確認すること"],
        "reading": ["最高スコアより判断への使い方を説明する", "既知の弱点と使ってはいけない条件を書く", "機密情報を公開教材や生成AIへ入力しない"],
        "pitfalls": ["スコアだけを成果として示す", "自社データの利用許可や来歴を省略する", "本番投入を最初の試行にする"],
        "self_study": ["1ページのモデルカードを完成させる", "30日以内にできるデータ棚卸し・ベースライン・レビューを計画する"],
        "check": ["このモデルは誰の何の判断を助けるか", "どの対象では信頼できないか", "次の小さな検証は何か"],
    },
}


DEEP_DIVE_CODE = {
    "01-kickoff": """
        probability = model.predict_proba(X_valid)[:, 1]
        summary = pd.DataFrame({"実際": y_valid.to_numpy(), "活性確率": probability})
        display(summary.groupby("実際")["活性確率"].describe().round(3))
        importance = pd.DataFrame({"特徴量": features, "重要度": model.feature_importances_})
        display(importance.sort_values("重要度", ascending=False).round(3))
    """,
    "02-python-with-copilot": """
        def celsius_to_kelvin_checked(celsius: float) -> float:
            if not isinstance(celsius, (int, float)):
                raise TypeError("温度は数値で入力してください")
            if celsius < -273.15:
                raise ValueError("絶対零度より低い値は指定できません")
            return celsius + 273.15

        for value in [25, -273.15, -300, "25"]:
            try:
                print(value, "->", celsius_to_kelvin_checked(value))
            except (TypeError, ValueError) as error:
                print(value, "->", type(error).__name__, error)
    """,
    "03-pandas": """
        quality_report = pd.DataFrame({
            "型": df.dtypes.astype(str),
            "欠損率": df.isna().mean(),
            "ユニーク数": df.nunique(dropna=True),
        })
        display(quality_report.sort_values("欠損率", ascending=False).head(10).round(3))
        display(pd.pivot_table(df, index="catalyst", columns="solvent", values="yield_pct", aggfunc=["count", "mean"]).round(1))
    """,
    "04-eda": """
        numeric_columns = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa", "yield_pct"]
        correlation = df[numeric_columns].corr()
        plt.figure(figsize=(9, 6))
        sns.heatmap(correlation, annot=True, fmt=".2f", cmap="coolwarm", center=0)
        plt.title("数値列の相関（因果関係ではない）")
        plt.tight_layout()
        missing_by_solvent = df.assign(temperature_missing=df["temperature_c"].isna()).groupby("solvent", dropna=False)["temperature_missing"].agg(["count", "mean"])
        display(missing_by_solvent.rename(columns={"count": "件数", "mean": "温度欠損率"}).round(3))
    """,
    "05-problem-framing": """
        problem_canvas = pd.DataFrame({
            "項目": ["利用者", "判断", "予測時点", "目的変数", "使える情報", "使えない情報", "評価指標", "単純基準"],
            "例": ["実験担当者", "次に試す条件の優先順位", "実験計画時", "yield_pct", "構造・予定条件", "実験後の測定値", "MAE", "過去平均"],
        })
        display(problem_canvas)
        error_cost = pd.DataFrame({"誤り": ["収率を過大予測", "収率を過小予測"], "起こりうる影響": ["低収率条件へ実験資源を使う", "有望条件を見送る"], "確認したい相手": ["実験担当者", "テーマリーダー"]})
        display(error_cost)
    """,
    "06-validation-leakage": """
        from sklearn.model_selection import GroupKFold, cross_val_score
        from sklearn.pipeline import make_pipeline
        from sklearn.impute import SimpleImputer

        grouped_model = make_pipeline(SimpleImputer(strategy="median"), DecisionTreeClassifier(max_depth=4, random_state=42))
        group_cv = GroupKFold(n_splits=5)
        group_scores = cross_val_score(grouped_model, df[features], df["active"], groups=df["scaffold_group"], cv=group_cv, scoring="f1")
        print("系列分割F1:", group_scores.round(3))
        print("平均 ± 標準偏差:", round(group_scores.mean(), 3), "±", round(group_scores.std(), 3))
    """,
    "07-regression": """
        errors["残差"] = errors["yield_pct"] - errors["予測"]
        group_error = errors.groupby("scaffold_group").agg(件数=("残差", "size"), MAE=("絶対誤差", "mean"), 平均残差=("残差", "mean"))
        display(group_error.sort_values("MAE", ascending=False).round(2))
        print("平均残差が正なら、その系列を平均的に過小予測しています。")
    """,
    "08-classification": """
        from sklearn.metrics import precision_recall_curve
        precision_curve, recall_curve, thresholds = precision_recall_curve(y_valid, probability)
        curve = pd.DataFrame({"閾値": thresholds, "precision": precision_curve[:-1], "recall": recall_curve[:-1]})
        curve["F1"] = 2 * curve["precision"] * curve["recall"] / (curve["precision"] + curve["recall"])
        display(curve.iloc[::max(1, len(curve)//10)].round(3))
        best_row = curve.loc[curve["F1"].idxmax()]
        print("この検証データ上でF1最大の閾値（最終性能ではない）:", round(best_row["閾値"], 3))
    """,
    "09-preprocessing-pipeline": """
        transformed_names = model.named_steps["前処理"].get_feature_names_out()
        transformed = model.named_steps["前処理"].transform(X_train.head(3))
        print("元の列数:", X_train.shape[1], "変換後の列数:", transformed.shape[1])
        display(pd.DataFrame(transformed, columns=transformed_names, index=X_train.head(3).index).iloc[:, :12].round(2))
    """,
    "10-model-comparison": """
        from sklearn.model_selection import StratifiedKFold, cross_val_score
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        stability = []
        for name, estimator in models.items():
            scores = cross_val_score(estimator, df[features], df["active"], cv=cv, scoring="f1")
            stability.append({"モデル": name, "F1平均": scores.mean(), "F1標準偏差": scores.std(), "最低F1": scores.min()})
        display(pd.DataFrame(stability).sort_values("F1平均", ascending=False).round(3))
    """,
    "11-feature-engineering": """
        candidate_sets = {"基本": base, "温度距離だけ": [*base, "temperature_distance"], "濃度/時間だけ": [*base, "concentration_per_hour"], "両方": added}
        ablation = []
        for name, columns in candidate_sets.items():
            estimator = make_pipeline(SimpleImputer(strategy="median"), RandomForestRegressor(n_estimators=150, max_depth=6, random_state=42))
            estimator.fit(engineered.loc[train_idx, columns], engineered.loc[train_idx, "yield_pct"])
            prediction = estimator.predict(engineered.loc[valid_idx, columns])
            ablation.append({"特徴量セット": name, "列数": len(columns), "MAE": mean_absolute_error(engineered.loc[valid_idx, "yield_pct"], prediction)})
        display(pd.DataFrame(ablation).sort_values("MAE").round(3))
    """,
    "12-experiment-cycle": """
        from sklearn.model_selection import train_test_split
        X_fit, X_holdout, y_fit, y_holdout = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
        best = make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42)).fit(X_fit, y_fit)
        importance = permutation_importance(best, X_holdout, y_holdout, scoring="f1", n_repeats=10, random_state=42)
        holdout_importance = pd.DataFrame({"特徴量": features, "重要度平均": importance.importances_mean, "重要度標準偏差": importance.importances_std})
        display(holdout_importance.sort_values("重要度平均", ascending=False).round(3))
        experiment_log.to_csv(ROOT / "workspace" / "experiment_log.csv", index=False)
        print("実験ログをworkspace/experiment_log.csvへ保存しました")
    """,
    "13-kaggle-kickoff": """
        def validate_submission(submission, test, expected_columns):
            assert list(submission.columns) == expected_columns, "列名または順序が違います"
            assert len(submission) == len(test), "行数がtestと一致しません"
            assert submission[expected_columns[0]].is_unique, "IDが重複しています"
            assert submission[expected_columns[0]].tolist() == test[expected_columns[0]].tolist(), "IDの順序がtestと一致しません"
            assert submission[expected_columns[1]].isin([0, 1]).all(), "予測値は0/1にしてください"
            return "提出形式OK"

        print(validate_submission(submission, test, ["sample_id", "active"]))
        display(train[target].value_counts(normalize=True).rename("割合").to_frame().round(3))
    """,
    "14-kaggle-improvement": """
        validation_result = X_valid[["scaffold_group"]].copy()
        validation_result["正解"] = y_valid
        validation_result["予測"] = model.predict(X_valid)
        validation_result["誤分類"] = validation_result["正解"] != validation_result["予測"]
        error_by_group = validation_result.groupby("scaffold_group").agg(件数=("誤分類", "size"), 誤分類数=("誤分類", "sum"), 誤分類率=("誤分類", "mean"))
        display(error_by_group.sort_values(["誤分類率", "件数"], ascending=False).round(3))
    """,
    "15-show-and-tell": """
        model_card = pd.DataFrame({
            "項目": ["想定利用者", "支援する判断", "学習データ", "評価方法", "既知の限界", "使ってはいけない条件", "再現手順", "次の検証"],
            "記入例": ["実験担当者", "候補条件の優先順位", "公開合成データ420件", "系列分割F1", "新規系列に弱い可能性", "対象外化学空間", "uv sync→Run All", "社内データ辞書の確認"],
        })
        display(model_card)
    """,
}


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
    meta = LESSON_META[folder]
    objectives = "\n".join(f"- {item}" for item in meta["objectives"])
    terms = "\n".join(f"- {item}" for item in meta["terms"])
    reading = "\n".join(f"- {item}" for item in meta["reading"])
    pitfalls = "\n".join(f"- {item}" for item in meta["pitfalls"])
    self_study = "\n".join(f"- {item}" for item in meta["self_study"])
    check = "\n".join(f"{index}. {item}" for index, item in enumerate(meta["check"], start=1))
    guide = markdown(
        f"""
        ## この回でできるようになること

        {objectives}

        ### 進み方

        `CORE`は同期90分で扱う本線、`DEEP DIVE`は時間があれば扱う深掘り、
        `SELF-STUDY`は任意自習です。すべて終わらなくても次回へ進めます。

        ### 先に押さえる言葉

        {terms}

        > **実行前の30秒予想**：今日の問いに、今の言葉で仮の答えを書いてから始めます。
        """
    )
    deep_dive_intro = markdown(
        f"""
        ## DEEP DIVE：結果を一段深く読む

        次のセルは、数値を出して終わらず「どの条件で、なぜそう見えるか」を調べる発展です。

        ### 出力を見る観点

        {reading}
        """
    )
    wrap_up = markdown(
        f"""
        ## よくある誤り

        {pitfalls}

        ## SELF-STUDY（任意・30〜60分）

        {self_study}

        成果は完成したコードでなくても、予想・変更点・出力・解釈を4行で残せば十分です。

        ## 振り返りチェック

        {check}

        答えに詰まった項目が、次に見返す場所です。暗記ではなくNotebookの該当セルを指せればOKです。
        """
    )
    content["cells"] = [content["cells"][0], content["cells"][1], guide, *content["cells"][2:], deep_dive_intro, code(DEEP_DIVE_CODE[folder]), wrap_up]
    write_named_notebook(folder, "lesson.ipynb", content)


def write_named_notebook(folder: str, filename: str, content: dict) -> None:
    path = LESSONS_DIR / folder / filename
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
                high_yield = df.loc[df["yield_pct"] >= 60, columns]
                print("収率60%以上:", len(high_yield), "件")
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
                from matplotlib import font_manager
                available_fonts = {font.name for font in font_manager.fontManager.ttflist}
                for candidate in ["Yu Gothic", "Meiryo", "Hiragino Sans", "Noto Sans CJK JP"]:
                    if candidate in available_fonts:
                        plt.rcParams["font.family"] = candidate
                        break
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
                from matplotlib import font_manager
                from sklearn.model_selection import train_test_split
                from sklearn.impute import SimpleImputer
                from sklearn.pipeline import make_pipeline
                from sklearn.dummy import DummyRegressor
                from sklearn.linear_model import LinearRegression
                from sklearn.tree import DecisionTreeRegressor
                from sklearn.ensemble import RandomForestRegressor
                from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

                available_fonts = {font.name for font in font_manager.fontManager.ttflist}
                for candidate in ["Yu Gothic", "Meiryo", "Hiragino Sans", "Noto Sans CJK JP"]:
                    if candidate in available_fonts:
                        plt.rcParams["font.family"] = candidate
                        break

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
                from matplotlib import font_manager
                from sklearn.model_selection import train_test_split
                from sklearn.impute import SimpleImputer
                from sklearn.pipeline import make_pipeline
                from sklearn.linear_model import LogisticRegression
                from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, precision_score, recall_score, f1_score

                available_fonts = {font.name for font in font_manager.fontManager.ttflist}
                for candidate in ["Yu Gothic", "Meiryo", "Hiragino Sans", "Noto Sans CJK JP"]:
                    if candidate in available_fonts:
                        plt.rcParams["font.family"] = candidate
                        break

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
                model=Pipeline([("前処理", preprocess), ("モデル", RandomForestClassifier(n_estimators=300, max_depth=3, class_weight="balanced", random_state=42))])
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

    write_named_notebook("13-kaggle-kickoff", "titanic_optional.ipynb", notebook(
        "任意実践：Kaggle Titanicへ提出する",
        "模擬コンペで覚えた手順を、実際のKaggle過去コンペで再現できるか。",
        [
            markdown("""## 事前準備\n\n1. Kaggleの`Titanic - Machine Learning from Disaster`を開く\n2. `Join Competition`からルールへ同意する\n3. `Data`画面からデータをダウンロードする\n4. ZIP内の`train.csv`、`test.csv`、`gender_submission.csv`を次へ置く\n\n```text\ndata/kaggle/titanic/\n```\n\nこのフォルダはGit管理対象外です。会社のデータや認証情報を置かないでください。"""),
            code("""
                import pandas as pd

                titanic_dir = DATA / "kaggle" / "titanic"
                train_path = titanic_dir / "train.csv"
                test_path = titanic_dir / "test.csv"
                ready = train_path.exists() and test_path.exists()
                if not ready:
                    print("Kaggleからtrain.csvとtest.csvをダウンロードし、次へ置いてください:")
                    print(titanic_dir)
                else:
                    train = pd.read_csv(train_path)
                    test = pd.read_csv(test_path)
                    print("train:", train.shape, "test:", test.shape)
                    display(train.head(3))
            """),
            markdown("""## ベースラインを検証する\n\n評価指標はaccuracyです。`Survived`を目的変数にし、提出に存在する列だけを使います。"""),
            code("""
                if ready:
                    from sklearn.model_selection import train_test_split
                    from sklearn.compose import ColumnTransformer
                    from sklearn.pipeline import Pipeline
                    from sklearn.impute import SimpleImputer
                    from sklearn.preprocessing import OneHotEncoder
                    from sklearn.ensemble import RandomForestClassifier
                    from sklearn.metrics import accuracy_score

                    target = "Survived"
                    features = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked"]
                    numeric = ["Age", "SibSp", "Parch", "Fare"]
                    categorical = ["Pclass", "Sex", "Embarked"]
                    preprocess = ColumnTransformer([
                        ("数値", SimpleImputer(strategy="median"), numeric),
                        ("カテゴリ", Pipeline([
                            ("補完", SimpleImputer(strategy="most_frequent")),
                            ("one_hot", OneHotEncoder(handle_unknown="ignore")),
                        ]), categorical),
                    ])
                    model = Pipeline([
                        ("前処理", preprocess),
                        ("モデル", RandomForestClassifier(n_estimators=250, max_depth=5, random_state=42)),
                    ])
                    X_train, X_valid, y_train, y_valid = train_test_split(
                        train[features], train[target], test_size=0.25, random_state=42, stratify=train[target]
                    )
                    model.fit(X_train, y_train)
                    print("ローカル検証accuracy:", round(accuracy_score(y_valid, model.predict(X_valid)), 3))
                else:
                    print("データ準備後に、このセルをもう一度実行します。")
            """),
            markdown("""## 提出CSVを作る\n\n列名と行数を機械的に検査してから、Kaggleの`Submit Predictions`へアップロードします。"""),
            code("""
                if ready:
                    model.fit(train[features], train[target])
                    submission = pd.DataFrame({
                        "PassengerId": test["PassengerId"],
                        "Survived": model.predict(test[features]),
                    })
                    assert list(submission.columns) == ["PassengerId", "Survived"]
                    assert len(submission) == len(test)
                    assert submission["PassengerId"].is_unique
                    output = ROOT / "workspace" / "titanic_submission.csv"
                    submission.to_csv(output, index=False)
                    print("提出ファイル:", output)
                    display(submission.head())
                else:
                    print("データ準備後に、このセルをもう一度実行します。")
            """),
            markdown("""## 提出後\n\nLeaderboardの点数だけで良し悪しを決めず、ローカル検証、変更点、結果を実験ログへ残します。Kaggle上の他者Notebookは、自分のベースラインを提出した後に読みます。""")
        ]
    ))


def main() -> None:
    df = make_dataset()
    write_data(df)
    build_notebooks()
    print(f"generated: {len(df)} rows and 15 notebooks")


if __name__ == "__main__":
    main()
