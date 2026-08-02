"""合成データと全15回のNotebookを再生成する。

公開可能な架空データだけを使い、乱数シードを固定して再現性を保つ。
各回はCORE（本線）とDEEP DIVE（発展）の両方をやや高めの難易度で用意し、
コーディング力・評価の厳密さ・モデルの多様さを段階的に扱う。
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


# 日本語フォントを選ぶ再利用ヘルパー。描画する回の先頭で読み込む。
JP_FONT_HELPER = """
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    def use_japanese_font():
        \"\"\"文字化けしないフォントを選ぶ。見つからなければ既定のまま。\"\"\"
        available = {font.name for font in font_manager.fontManager.ttflist}
        for candidate in ["Yu Gothic", "Meiryo", "Hiragino Sans", "Noto Sans CJK JP", "IPAexGothic"]:
            if candidate in available:
                plt.rcParams["font.family"] = candidate
                return candidate
        return None

    use_japanese_font()
"""


LESSON_META = {
    "01-kickoff": {
        "objectives": [
            "特徴量・目的変数・学習・予測を、画面上の入出力と結びつける",
            "予測を関数へ切り出し、型ヒントとassertで最小の検証を付ける",
            "ベースラインと比べ、設定変更の効果を交差検証の平均とばらつきで語る",
        ],
        "terms": [
            "特徴量：予測時点でモデルへ渡す情報",
            "目的変数：予測したい答え",
            "学習：既知データから関係を推定する処理",
            "予測：学習済みモデルを未知データへ使う処理",
        ],
        "reading": [
            "学習F1と検証F1の差が過学習の目安になる",
            "不純度重要度は高カーディナリティ列へ偏るため並べ替え重要度と併読する",
            "予測確率は当たり外れの確信度であり、真実そのものではない",
        ],
        "pitfalls": [
            "学習データの成績を実力だと思う",
            "1試料の予測だけでモデル全体を判断する",
            "良い数値が出るまで設定を無計画に変える",
        ],
        "self_study": [
            "evaluate_classifierを拡張し、precisionとrecallも返してテストを足す",
            "木の深さ2・4・8を交差検証で比較し、選ぶ理由を平均とばらつきで2文書く",
        ],
        "check": [
            "Xとyはそれぞれ何か",
            "不純度重要度と並べ替え重要度はどう違うか",
            "単一の検証スコアより交差検証を見る理由は何か",
        ],
    },
    "02-python-with-copilot": {
        "objectives": [
            "変数・リスト・辞書・条件分岐・繰り返し・関数を読める",
            "型ヒント・docstring・防御的な入力検査を備えた関数を書く",
            "assertによる小さなテストで、境界値と例外を先に固定する",
        ],
        "terms": [
            "型ヒント：引数と戻り値の型を明示する注釈",
            "docstring：関数の目的と使い方を書く文字列",
            "例外：処理を続けられない理由を伝える仕組み",
            "単体テスト：関数の入出力を自動で確かめる小さなコード",
            "純粋関数：同じ入力へ常に同じ出力を返し副作用のない関数",
        ],
        "reading": [
            "コードは上から順に状態を変える",
            "エラーの末尾には原因に近い情報がある",
            "関数は代表値だけでなく境界値と異常値でも試す",
        ],
        "pitfalls": [
            "Notebookを途中から実行して変数がない",
            "Copilotの長い修正を一度に採用する",
            "エラー全文を読まずにセルを繰り返し実行する",
        ],
        "self_study": [
            "収率のリストから外れ値をIQRで除く関数を、型ヒントとテスト付きで書く",
            "正常値・空リスト・NaN混在の3ケースを、期待結果を先に書いてから検証する",
        ],
        "check": [
            "型ヒントとdocstringは何の役に立つか",
            "assertは何を保証し、何を保証しないか",
            "生成AIのコードを何で確認するか",
        ],
    },
    "03-pandas": {
        "objectives": [
            "初見データの形・型・欠損・要約統計を確認する",
            "locとqueryで条件を明示し、method chainingで読みやすくまとめる",
            "groupby・agg・pivot_tableで多軸の比較表を作り、性能差にも気を配る",
        ],
        "terms": [
            "DataFrame：行と列を持つ表",
            "method chaining：中間変数を作らず処理をつなげる書き方",
            "ベクトル化：ループの代わりに列全体へ一括演算すること",
            "集約：複数行を件数や平均などへまとめる処理",
            "カテゴリ型：取りうる値が限られる列の省メモリ表現",
        ],
        "reading": [
            "平均だけでなく件数とばらつきを一緒に見る",
            "applyの前にベクトル化で書けないかを考える",
            "カテゴリ別の差は因果関係とは限らない",
        ],
        "pitfalls": [
            "列の単位や定義を確認せず計算する",
            "行ごとのapplyを多用して遅く読みにくくする",
            "件数が極端に少ない群の平均を強く信じる",
        ],
        "self_study": [
            "触媒×溶媒の件数・平均収率・標準偏差をpivot_tableで作る",
            "applyとベクトル化の実行時間を比較し、差をm%で記録する",
        ],
        "check": [
            "shapeの2つの数は何か",
            "method chainingの利点と注意点は何か",
            "applyよりベクトル化を選ぶ理由は何か",
        ],
    },
    "04-eda": {
        "objectives": [
            "単変量・二変量・群別の順でデータを見る",
            "欠損の発生機構と外れ値を、検定や多変量手法で客観的に調べる",
            "図と統計量から、断定ではなく検証可能な仮説を作る",
        ],
        "terms": [
            "分布：値がどこにどれだけ存在するか",
            "外れ値：他と大きく異なる観測値",
            "相互情報量：非線形も捉える関連の強さ",
            "欠損機構：MCAR/MAR/MNARという欠損の起こり方",
            "多変量外れ値：単変量では見えない組み合わせの異常",
        ],
        "reading": [
            "軸・単位・件数を確認してから形を見る",
            "相関は非線形関係や群ごとの差を隠すことがある",
            "欠損の有無が他の列と関係するなら発生機構を疑う",
        ],
        "pitfalls": [
            "外れ値を自動削除する",
            "相関を因果と読む",
            "見栄えの良い図だけを選ぶ",
        ],
        "self_study": [
            "相互情報量の上位3列について、散布図で関係の形を確認する",
            "IsolationForestの外れ値候補2件を、残す場合と除く場合で整理する",
        ],
        "check": [
            "相関係数と相互情報量はどう違うか",
            "MCARとMARの違いは何か",
            "多変量外れ値が単変量で見つからない理由は何か",
        ],
    },
    "05-problem-framing": {
        "objectives": [
            "利用者・判断・予測時点を1文にする",
            "目的変数と利用可能な説明変数を分け、リーク候補を自動監査する",
            "誤りのコストから期待値を計算し、指標と閾値を業務要件で決める",
        ],
        "terms": [
            "予測時点：モデルを実際に使う瞬間",
            "ベースライン：複雑なモデルと比較する単純な基準",
            "コスト行列：誤りの種類ごとの損失をまとめた表",
            "期待コスト：確率×損失で見積もる平均的な損失",
            "リーク監査：目的変数と強く結びつく怪しい列を洗い出す確認",
        ],
        "reading": [
            "スコアより先に誰の判断をどう変えるかを確認する",
            "未来情報や測定後情報は高性能でも使えない",
            "最適な閾値は指標ではなく誤りのコストで決まる",
        ],
        "pitfalls": [
            "入手できる列をすべて使う",
            "目的変数が測定や運用で不安定",
            "精度目標だけで利用方法とコストが決まっていない",
        ],
        "self_study": [
            "自社テーマを機密情報なしで問題設定キャンバスへ落とす",
            "偽陽性・偽陰性のコストを入れ、期待コスト最小の閾値を計算する",
        ],
        "check": [
            "誰が何を判断するモデルか",
            "予測時点で本当に得られる列はどれか",
            "コスト行列から最適な閾値をどう求めるか",
        ],
    },
    "06-validation-leakage": {
        "objectives": [
            "学習・検証・テストの役割を区別し、前処理を分割の内側へ入れる",
            "分割方式ごとのスコアのばらつきを比べ、楽観的な評価を見抜く",
            "ネストした交差検証とadversarial validationで、楽観の少ない推定と分布ずれを確かめる",
        ],
        "terms": [
            "汎化：未知データでも性能を保つこと",
            "リーク：予測時には得られない情報が学習へ混ざること",
            "グループ分割：関連試料を同じ側へまとめる分割",
            "ネストCV：探索と評価を二重の交差検証で分ける方法",
            "adversarial validation：学習とテストを見分けられるか調べる手法",
        ],
        "reading": [
            "検証方法は将来の使われ方を模擬する",
            "同じ系列を跨がせるとスコアは楽観的に膨らむ",
            "探索と評価を同じ分割で兼ねると性能を過大評価する",
        ],
        "pitfalls": [
            "前処理を全データで済ませてから分割する",
            "同じ系列の類似化合物を両側へ入れる",
            "検証データを何度も見て実質的に学習する",
        ],
        "self_study": [
            "KFold・StratifiedKFold・GroupKFoldのF1分布を箱ひげ図で比べる",
            "adversarial validationのAUCを下げる列を1つ見つけ理由を書く",
        ],
        "check": [
            "検証とテストの違いは何か",
            "ネストCVが必要になるのはどんなときか",
            "adversarial validationのAUCが高いと何を意味するか",
        ],
    },
    "07-regression": {
        "objectives": [
            "MAE・RMSE・R²を異なる視点として読み、複数モデルを同条件で比較する",
            "学習曲線と残差診断から、データ不足か表現力不足かを切り分ける",
            "分位点回帰やブートストラップで予測の不確かさを区間として示す",
        ],
        "terms": [
            "MAE：絶対誤差の平均",
            "RMSE：大きな誤差をより重く扱う指標",
            "残差：実測値と予測値の差",
            "学習曲線：データ量に対する性能の変化",
            "予測区間：予測値に付ける不確かさの幅",
        ],
        "reading": [
            "MAEは目的変数と同じ単位で説明できる",
            "学習曲線が高止まりならデータ追加より特徴量やモデルを見直す",
            "残差の模様は未学習の構造を示すことがある",
        ],
        "pitfalls": [
            "R²だけで利用可能と判断する",
            "テストデータでモデルを選ぶ",
            "点予測だけを示し不確かさを伝えない",
        ],
        "self_study": [
            "学習曲線を描き、データ追加が効くかを1文で判断する",
            "分位点回帰の10-90%区間の被覆率を検証データで確認する",
        ],
        "check": [
            "MAEとRMSEは何を違って重視するか",
            "学習曲線から何を読み取れるか",
            "予測区間が点予測より役立つ場面はどこか",
        ],
    },
    "08-classification": {
        "objectives": [
            "混同行列とprecision・recall・F1・PR-AUCを利用場面へ結びつける",
            "確率の較正（calibration）を信頼度図と指標で評価する",
            "不均衡データへclass_weightや閾値調整で対処し、効果を検証する",
        ],
        "terms": [
            "precision：陽性予測のうち正しかった割合",
            "recall：実際の陽性を見つけた割合",
            "PR-AUC：適合率-再現率曲線の下側面積",
            "較正：予測確率と実際の頻度が一致している度合い",
            "class_weight：少数クラスの誤りを重く扱う設定",
        ],
        "reading": [
            "不均衡データではaccuracyよりPR-AUCが実態を映す",
            "確率をコスト計算へ使うなら較正が前提になる",
            "閾値はモデル学習後にも業務要件から調整できる",
        ],
        "pitfalls": [
            "常に閾値0.5を使う",
            "偽陽性と偽陰性のコストを同じとみなす",
            "未較正の確率をそのまま意思決定へ使う",
        ],
        "self_study": [
            "CalibratedClassifierCVで較正前後の信頼度図とBrierスコアを比べる",
            "コスト行列から期待コスト最小の閾値を求め、0.5と比較する",
        ],
        "check": [
            "accuracyが危険な例は何か",
            "較正が悪い確率を使うと何が起きるか",
            "コストから閾値をどう決めるか",
        ],
    },
    "09-preprocessing-pipeline": {
        "objectives": [
            "列型ごとの前処理をColumnTransformerで分け、Pipelineへ一体化する",
            "BaseEstimatorとTransformerMixinで、意味のある自作変換器を書く",
            "前処理の選択肢をGridSearchCVの探索対象に含める",
        ],
        "terms": [
            "ColumnTransformer：列ごとに別の前処理を割り当てる仕組み",
            "自作変換器：fit/transformを実装した独自の前処理",
            "get_feature_names_out：変換後の列名を取得するAPI",
            "パラメータ探索：前処理やモデルの設定を系統的に比較すること",
            "メモリキャッシュ：共通の前処理計算を使い回す仕組み",
        ],
        "reading": [
            "fit時に学ぶ値とtransformだけの処理を区別する",
            "自作変換器もPipelineへ入れれば分割の内側で学習される",
            "前処理もハイパーパラメータとして交差検証で選べる",
        ],
        "pitfalls": [
            "全データ平均で欠損補完する",
            "カテゴリを意味のない大小関係へ変換する",
            "本番の未知カテゴリでエラーになる",
        ],
        "self_study": [
            "分子量あたりのTPSAを作る自作変換器を書き、Pipelineへ組み込む",
            "数値標準化の有無と補完戦略をGridSearchCVで比較する",
        ],
        "check": [
            "自作変換器に最低限必要なメソッドは何か",
            "前処理をPipelineへ入れるとリークがなぜ防げるか",
            "get_feature_names_outは何に使うか",
        ],
    },
    "10-model-comparison": {
        "objectives": [
            "同じ分割・指標で複数モデルを比較し、性能・速度・安定性を並べる",
            "反復交差検証と対応のある検定で、差が偶然でないかを確かめる",
            "投票・スタッキングで複数モデルを束ね、単体との差を評価する",
        ],
        "terms": [
            "反復交差検証：分割の乱数を変えて繰り返す評価",
            "対応のある検定：同じ分割上の差を比べる統計的検定",
            "投票分類器：複数モデルの多数決や平均確率で決めるモデル",
            "スタッキング：モデルの予測を入力に上位モデルで統合する方法",
            "勾配ブースティング：前の誤りを順に補正する木の集合",
        ],
        "reading": [
            "1回の勝敗より平均とばらつきを見る",
            "平均差が標準誤差に埋もれていないかを検定で確かめる",
            "束ねる価値は、束ねる元が互いに間違え方が違うときに出る",
        ],
        "pitfalls": [
            "異なる分割で比較する",
            "モデルごとに異なる指標を報告する",
            "最も高い1回のスコアだけを採用する",
        ],
        "self_study": [
            "RepeatedStratifiedKFoldでF1分布を作り、上位2モデルをWilcoxon検定で比べる",
            "StackingClassifierと最良単体のF1・学習時間を比較する",
        ],
        "check": [
            "公平な比較に固定すべきものは何か",
            "対応のある検定が必要な理由は何か",
            "スタッキングが効きやすいのはどんなときか",
        ],
    },
    "11-feature-engineering": {
        "objectives": [
            "化学的仮説を再計算可能な特徴量へ変え、交差検証でアブレーションする",
            "リークを避けたtarget encodingを、分割の内側で自作する",
            "相互情報量・RFECVで特徴量を選び、適用領域の限界を意識する",
        ],
        "terms": [
            "特徴量設計：既存情報から予測に役立つ表現を作ること",
            "target encoding：カテゴリを目的変数の集約値で置き換える手法",
            "アブレーション：要素を足し引きして寄与を調べる比較",
            "RFECV：交差検証つきで再帰的に特徴量を削る選択法",
            "適用領域：モデルが信頼できる入力範囲",
        ],
        "reading": [
            "特徴量は予測時点で計算できる必要がある",
            "target encodingは分割の外で計算するとリークする",
            "選択も評価も同じ分割の内側で行う",
        ],
        "pitfalls": [
            "意味を説明できない特徴量を大量追加する",
            "目的変数由来の値を全データで作って特徴量にする",
            "追加前後で分割やモデルも変える",
        ],
        "self_study": [
            "自作KFold target encodingの有無でMAEを比較する",
            "RFECVで残った特徴量と、化学的な解釈を突き合わせる",
        ],
        "check": [
            "その特徴量はいつ計算できるか",
            "target encodingでリークを防ぐ手順は何か",
            "特徴量選択も交差検証の内側で行う理由は何か",
        ],
    },
    "12-experiment-cycle": {
        "objectives": [
            "変更を1要素に限定した比較を設計し、実験ログを関数で残す",
            "RandomizedSearchCVで探索し、ネストCVで楽観の少ない推定を得る",
            "並べ替え重要度の信頼区間とエラー分析から次の仮説を選ぶ",
        ],
        "terms": [
            "実験ログ：変更・条件・結果・解釈を残す記録",
            "ランダム探索：候補を無作為に試すハイパーパラメータ探索",
            "ネストCV：探索と評価を分けて過大評価を防ぐ交差検証",
            "信頼区間：推定値の不確かさを表す幅",
            "再現性：同じ手順で同じ結果を得られる性質",
        ],
        "reading": [
            "標準偏差が改善幅より大きくないか確認する",
            "内側で選んだ設定を外側で評価すると楽観が減る",
            "重要度は因果効果ではなく予測への寄与である",
        ],
        "pitfalls": [
            "同時に複数要素を変える",
            "探索に使った分割で最終性能も報告する",
            "悪化した実験を記録から消す",
        ],
        "self_study": [
            "RandomizedSearchCVの最良設定を、ネストCVの外側スコアで確かめる",
            "並べ替え重要度を20反復で計算し、区間が0を跨ぐ列を挙げる",
        ],
        "check": [
            "1要素だけ変える理由は何か",
            "ネストCVは何を防ぐか",
            "重要度の区間が0を跨ぐとどう解釈するか",
        ],
    },
    "13-kaggle-kickoff": {
        "objectives": [
            "問題・指標・データ・提出形式を読み解き、再現可能なベースラインを作る",
            "cross_val_predictでOOF予測を作り、CVとLBの一致を確かめる",
            "提出CSVを検査する関数を、テスト付きで書く",
        ],
        "terms": [
            "Leaderboard：提出結果を順位表示する仕組み",
            "OOF予測：交差検証の検証側だけを集めた予測",
            "submission：指定形式の予測ファイル",
            "CV-LBギャップ：手元の検証と公開スコアの差",
            "ベースライン：最初に必ず保存する比較起点",
        ],
        "reading": [
            "testには答えがないことを確認する",
            "OOF予測は手元でLBに近い推定を与える",
            "ID列の順序と一意性を検査する",
        ],
        "pitfalls": [
            "testの情報へ合わせて特徴量を決める",
            "提出ファイルのindex列を混入させる",
            "最初から公開Notebookを丸ごと写す",
        ],
        "self_study": [
            "OOFのF1と提出後スコアの差を記録し、原因を1つ推測する",
            "validate_submissionへ異常な提出を渡し、全assertが働くか試す",
        ],
        "check": [
            "OOF予測は何に使えるか",
            "CV-LBギャップが大きいとき何を疑うか",
            "提出前に検査する項目は何か",
        ],
    },
    "14-kaggle-improvement": {
        "objectives": [
            "限られた時間で実験を優先順位付けし、OOFスタッキングで統合する",
            "adversarial validationで学習とテストの分布ずれを点検する",
            "複数シードの平均と閾値調整で、偶然に頼らない改善を積む",
        ],
        "terms": [
            "OOFスタッキング：OOF予測を入力に上位モデルで統合する方法",
            "分布ずれ：学習とテストで入力の分布が違うこと",
            "シードアンサンブル：乱数だけ変えた複数モデルの平均",
            "閾値調整：確率からクラスへの境界を変えること",
            "実験統合：有効な変更を再検証しながら組み合わせること",
        ],
        "reading": [
            "ローカル改善とLeaderboard改善の一致を確認する",
            "分布ずれがあるとランダムCVは楽観的になる",
            "検証データで選んだ閾値は別データで確かめる",
        ],
        "pitfalls": [
            "5人の変更を一度に統合する",
            "Leaderboardだけを目的関数にする",
            "分布ずれを無視してランダム分割だけで判断する",
        ],
        "self_study": [
            "単体最良・投票・スタッキングのOOF F1を比較する",
            "adversarial validationのAUCが高い列を除いて再評価する",
        ],
        "check": [
            "OOFスタッキングの手順は何か",
            "分布ずれをどう検知するか",
            "改善を統合する順序はどうするか",
        ],
    },
    "15-show-and-tell": {
        "objectives": [
            "モデルの目的・検証・結果・限界を短く説明し、再現可能に共有する",
            "学習済みPipelineをjoblibで保存し、モデルカードを関数で生成する",
            "適用領域と較正の観点から、使ってよい範囲と監視項目を決める",
        ],
        "terms": [
            "モデルカード：用途・データ・評価・限界をまとめた記録",
            "適用領域：モデルを使ってよい対象と条件",
            "永続化：学習済みモデルをファイルへ保存すること",
            "ドリフト：運用後に入力や関係が変わること",
            "監視：運用後の入力や性能変化を確認すること",
        ],
        "reading": [
            "最高スコアより判断への使い方を説明する",
            "既知の弱点と使ってはいけない条件を書く",
            "機密情報を公開教材や生成AIへ入力しない",
        ],
        "pitfalls": [
            "スコアだけを成果として示す",
            "自社データの利用許可や来歴を省略する",
            "本番投入を最初の試行にする",
        ],
        "self_study": [
            "保存したPipelineを読み直し、同じ入力で同じ予測になるか検証する",
            "適用領域スコアを閾値化し、範囲外の試料を要確認として仕分ける",
        ],
        "check": [
            "このモデルは誰の何の判断を助けるか",
            "適用領域をどう数値化したか",
            "運用後に監視すべき指標は何か",
        ],
    },
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
        dedent(
            """
            # {title}

            **今日の問い：{question}**

            **セルの動かし方**：各セル（灰色の枠）を選んで `Shift + Enter`（またはセル左の▷ボタン）を押すと実行できます。
            **上から順に**実行してください。前のセルを飛ばすと、後のセルでエラーになります。

            `TRY`は全員、`CHANGE`は値を1つ変える練習、`CHALLENGE`は余裕がある人向けです。
            `DEEP DIVE`・`APPENDIX`は経験者や自習向けの発展で、飛ばしても本編は完結します。
            分からないコードは、セル全体ではなく気になる数行をM365 Copilotへ貼って相談します。
            """
        ).format(title=title, question=question)
    )
    setup = code(
        """
        # 【準備セル】教材フォルダの場所を自動で見つけます。中身は今は理解しなくてOK、そのまま実行してください。
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
        "_title": title,
        "_question": question,
        "metadata": {
            "kernelspec": {"display_name": "Python 3 (uv)", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


# 旧15回分の中身をいったん「モジュール」として登録し、あとで5回へ組み立てる。
MODULES: dict = {}


def write_notebook(folder: str, content: dict, deep_dive_cells: list[dict], appendix_cells: list[dict] | None = None) -> None:
    """旧1回分を、統合前の素材として登録する（この時点ではファイルを書かない）。

    content["cells"]は[intro, setup, *core]なので、intro/setupを外したcoreだけを保持する。
    intro/setupとguide/wrap_upは、統合後の回で1つずつ作り直す。
    """
    MODULES[folder] = {
        "title": content["_title"],
        "question": content["_question"],
        "core": content["cells"][2:],
        "deep_dive": deep_dive_cells,
        "appendix": appendix_cells or [],
        "meta": LESSON_META[folder],
    }


def write_named_notebook(folder: str, filename: str, content: dict) -> None:
    path = LESSONS_DIR / folder / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    content = {k: v for k, v in content.items() if not k.startswith("_")}
    for index, cell in enumerate(content["cells"]):
        cell["id"] = f"cell-{index:02d}"
    path.write_text(json.dumps(content, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


# ---- 旧15回を5回へ統合する定義とヘルパー ----

COURSE_GROUPS = [
    {
        "folder": "01-python-and-data",
        "title": "第1回：Pythonとデータに触れ、まず予測を動かす",
        "overview": "環境を整え、Pythonとpandasの基礎を身につけ、完成済みの予測モデルを動かして「学習と予測」を体で覚えます。",
        "members": ["01-kickoff", "02-python-with-copilot", "03-pandas"],
    },
    {
        "folder": "02-look-frame-validate",
        "title": "第2回：データを見て、問いを立て、評価を正しく設計する",
        "overview": "データの怪しい点を見つけ（EDA）、何をいつ予測するかを決め（問題設定）、その評価がどこまで信じられるか（検証とリーク）を設計します。",
        "members": ["04-eda", "05-problem-framing", "06-validation-leakage"],
    },
    {
        "folder": "03-build-models",
        "title": "第3回：回帰・分類・前処理Pipelineでモデルを作る",
        "overview": "連続値の回帰、クラスの分類、そして数値列とカテゴリ列を安全に扱うPipelineで、評価できるモデルを組み立てます。",
        "members": ["07-regression", "08-classification", "09-preprocessing-pipeline"],
    },
    {
        "folder": "04-compare-and-improve",
        "title": "第4回：モデルを比較し、特徴量と実験で改善する",
        "overview": "複数モデルを公平に比べ、知識を特徴量に変え、1要素ずつ変える実験で「理由を説明できる改善」を回します。",
        "members": ["10-model-comparison", "11-feature-engineering", "12-experiment-cycle"],
    },
    {
        "folder": "05-ship-and-operate",
        "title": "第5回：提出から運用・監視・再学習（MLOps）へ",
        "overview": "模擬コンペで提出と改善を体験し、最後にモデルを「作って終わり」にせず、運用・監視・再学習のループ（MLOps）へつなげます。",
        "members": ["13-kaggle-kickoff", "14-kaggle-improvement", "15-show-and-tell"],
    },
]


def setup_cell() -> dict:
    return code(
        """
        # 【準備セル】教材フォルダの場所を自動で見つけます。中身は今は理解しなくてOK、そのまま実行してください。
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


def merged_intro(group: dict) -> dict:
    subs = " ／ ".join(MODULES[m]["title"].split("：", 1)[-1] for m in group["members"])
    return markdown(
        dedent(
            """
            # {title}

            この回は3つのパートで構成します：**{subs}**。

            **セルの動かし方**：各セル（灰色の枠）を選んで `Shift + Enter`（またはセル左の▷ボタン）を押すと実行できます。
            **上から順に**実行してください。前のセルを飛ばすと、後のセルでエラーになります。

            **AIと一緒に進める**：分からないコードは、セル全体ではなく気になる数行をM365 CopilotなどのAIへ貼って
            説明や修正を相談します（`ASK COPILOT`）。ただしAIの答えは鵜呑みにせず、必ず自分の出力で確かめます。

            `TRY`は全員、`CHANGE`は値を1つ変える練習、`CHALLENGE`は余裕がある人向け、
            `DEEP DIVE`・`APPENDIX`は発展です（飛ばしても本編は完結します）。
            """
        ).format(title=group["title"], subs=subs)
    )


def merged_guide(group: dict) -> dict:
    objectives, terms = [], []
    for member in group["members"]:
        objectives += MODULES[member]["meta"]["objectives"]
        terms += MODULES[member]["meta"]["terms"]
    obj_md = "\n".join(f"- {item}" for item in objectives)
    term_md = "\n".join(f"- {item}" for item in terms)
    return markdown(
        dedent(
            """
            ## この回でできるようになること

            {overview}

            {objectives}

            ### この回の進み方（大切）

            この回は、旧カリキュラムの**3回分をまとめた長い回**です。**パート1→2→3**の順に、各パートの
            `CORE`（本線）で手を動かします。1回の時間で全部を終える必要はありません。各パートの
            `DEEP DIVE`／`APPENDIX`は、余裕のある人や自習で進めてください。日をまたいで少しずつでも大丈夫です。

            ### 先に押さえる言葉

            {terms}

            > **実行前の30秒予想**：各パートの問いに、今の言葉で仮の答えを書いてから始めます。
            """
        ).format(overview=group["overview"], objectives=obj_md, terms=term_md)
    )


def chapter_heading(index: int, member: str) -> dict:
    mod = MODULES[member]
    sub = mod["title"].split("：", 1)[-1]
    return markdown(
        dedent(
            """
            ---

            # パート{index}：{sub}

            **このパートの問い：{question}**
            """
        ).format(index=index, sub=sub, question=mod["question"])
    )


def merged_wrapup(group: dict) -> dict:
    pitfalls, self_study, check = [], [], []
    for member in group["members"]:
        pitfalls += MODULES[member]["meta"]["pitfalls"]
        self_study += MODULES[member]["meta"]["self_study"]
        check += MODULES[member]["meta"]["check"]
    pit_md = "\n".join(f"- {item}" for item in pitfalls)
    ss_md = "\n".join(f"- {item}" for item in self_study)
    ck_md = "\n".join(f"{index}. {item}" for index, item in enumerate(check, start=1))
    return markdown(
        dedent(
            """
            ---

            ## よくある誤り

            {pitfalls}

            ## SELF-STUDY（任意・30〜60分）

            {self_study}

            成果は完成したコードでなくても、予想・変更点・出力・解釈を4行で残せば十分です。

            ## 振り返りチェック

            {check}

            答えに詰まった項目が、次に見返す場所です。暗記ではなくNotebookの該当セルを指せればOKです。
            """
        ).format(pitfalls=pit_md, self_study=ss_md, check=ck_md)
    )


def mlops_cells() -> list[dict]:
    """第5回の最後に足すMLOps（運用・監視・再学習）の章。前のパートで作った reloaded / feat / X_te を再利用する。"""
    return [
        markdown(
            dedent(
                """
                ---

                # パート4：MLOpsの考え方（運用・監視・再学習）

                ここまでで「良いモデルを作る」ことはできました。実務では、そこからが本番です。モデルは
                **作って終わりではなく、動かし続けるループ**の中で価値を出します。

                > **学習 → 提供（サービング）→ 監視 → 再学習 → …**

                このループを回す考え方や道具をまとめて**MLOps**と呼びます。実はこの教材では、その部品を
                すでに各所で触っています——`Pipeline`（再現性）、`joblib`での**永続化**、実験ログ（追跡）、
                ドリフト監視、適用領域。ここではそれらを「運用のループ」として一本につなぎます。
                """
            )
        ),
        markdown(
            dedent(
                """
                ### 提供（サービング）：学習済みモデルを「関数」として使えるようにする

                運用では、新しい試料が来るたびに学習し直しません。**保存済みモデルを読み込み、予測だけを返す
                関数**を用意します。前のパートで保存した`reloaded`（前処理ごと保存したPipeline）をそのまま使います。
                """
            )
        ),
        code(
            """
            def predict_activity(samples):
                "新しい試料(DataFrame)へ、活性の予測(0/1)と確率を返す推論関数。"
                proba = reloaded.predict_proba(samples[feat])[:, 1]
                return pd.DataFrame(
                    {"活性予測": (proba >= 0.5).astype(int), "活性確率": proba.round(3)},
                    index=samples.index,
                )

            display(predict_activity(X_te.head()))
            """
        ),
        markdown(
            dedent(
                """
                ### 出力の読み方

                前処理ごと保存したPipelineなので、受け取った人は`predict_activity(新しいデータ)`を呼ぶだけで
                予測できます。これが「サービング」の最小形です。Webサービスやバッチ処理も、裏でこの関数を
                呼んでいるだけ、とイメージしてください。
                """
            )
        ),
        markdown(
            dedent(
                """
                ### 監視と再学習：いつモデルを作り直すか

                運用後は、次を定期的に見張ります（このパートまでで手を動かした道具が、そのまま使えます）。

                - **入力のドリフト**：入力分布が学習時とずれていないか（第2回・このパートのadversarial validationの監視AUC）。正解が手に入らなくても検知できるのが利点。
                - **予測の傾向**：予測の陽性率が急に変わっていないか。
                - **性能**：正解ラベルが遅れて届いたら、F1などを計算し直す。
                - **適用領域**：学習データから遠い入力が増えていないか（近傍距離）。

                これらが目安を超えたら**再学習のトリガー**です。新しいデータを足して学習し直し、
                **同じ検証（第2回）・同じ評価（このパート）で前のモデルと比較**してから入れ替えます。
                作って終わりにせず、このループを回し続けることが、実データでモデルを役立て続けるコツです。
                """
            )
        ),
        markdown(
            dedent(
                """
                ### 再現性チェックリスト（引き継ぎ・監査のために）

                - データ生成・前処理・学習が**固定シードで再現**できる（この教材はすべてシード固定です）。
                - モデルは**Pipelineごと保存**し、前処理を含めて復元できる。
                - **モデルカード**（用途・限界・禁止条件）と**メタ情報**（使った特徴量・学習件数）を一緒に残す。
                - 実験は**ログ**に残し、なぜその設定にしたかを後から説明できる。

                ここまで来れば、「作って終わり」から「**運用でき、引き継げる**」モデルへの橋を渡せています。
                """
            )
        ),
    ]


def assemble_courses() -> None:
    for group in COURSE_GROUPS:
        cells = [merged_intro(group), setup_cell(), merged_guide(group)]
        for index, member in enumerate(group["members"], start=1):
            module = MODULES[member]
            cells.append(chapter_heading(index, member))
            cells.extend(module["core"])
            cells.extend(module["deep_dive"])
            cells.extend(module["appendix"])
        if group["folder"] == "05-ship-and-operate":
            cells.extend(mlops_cells())
        cells.append(merged_wrapup(group))
        content = {
            "cells": cells,
            "metadata": {
                "kernelspec": {"display_name": "Python 3 (uv)", "language": "python", "name": "python3"},
                "language_info": {"name": "python", "version": "3.12"},
            },
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        write_named_notebook(group["folder"], "lesson.ipynb", content)


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


FONT_SNIPPET = """
    # グラフの日本語が文字化けしないようにする設定です。中身は今は理解しなくてOK、そのまま実行してください。
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    for _name in ["Yu Gothic", "Meiryo", "Hiragino Sans", "Noto Sans CJK JP", "IPAexGothic"]:
        if _name in {f.name for f in font_manager.fontManager.ttflist}:
            plt.rcParams["font.family"] = _name
            break
"""


def font_cell(extra: str = "") -> dict:
    """日本語フォント設定に追加コードを続けたコードセルを作る。

    2つの文字列を別々にdedentしてから結合するため、インデントの深さが
    違っても崩れない（f-string内で多行を連結するとdedentが効かない問題を避ける）。
    """
    body = dedent(FONT_SNIPPET).strip() + "\n" + dedent(extra).strip() + "\n"
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": body,
    }


def build_notebooks() -> None:
    # ---- 第1回 ----
    write_notebook(
        "01-kickoff",
        notebook(
            "第1回：予測モデルを動かしてみる",
            "予測モデルは、データを受け取って何を返しているのか。",
            [
                markdown("""## この回で押さえる4つの言葉

この回は、モデルの中身のアルゴリズムは一旦置いて、**何を入れると何が返るか**だけを確認します。
モデルがやることは「過去のデータから関係を推定し（学習）、未知のデータへ当てはめる（予測）」の2段です。
先に、繰り返し出てくる4つの言葉を整理します。

| 言葉 | 意味 |
|---|---|
| 特徴量（X） | モデルへ渡す入力の列（例：分子量・LogP） |
| 目的変数（y） | 予測したい答えの列（例：活性 0/1） |
| 学習（fit） | 既知データから関係を推定する処理 |
| 予測（predict） | 学習済みモデルを未知データへ使う処理 |"""),
                markdown("""## まずデータを開く

分析は「データを見る」ことから始まります。次のセルはCSV（表計算のような表データ）を読み込み、
`df`という名前の**表（DataFrame）**に入れます。`df.head()`は先頭5行だけを表示します。
全部で何行・何列あるかも一緒に出します。"""),
                common_load_cell(),
                markdown("""### 出力の読み方

- `420行 × 19列`：試料が420件、各試料について19種類の情報がある、という意味です。
- 表の**1行が1試料**、**1列が1種類の情報**です。`sample_id`は試料の名札で、予測には使いません。
- `NaN`（Not a Number）は**欠損＝その値が測られていない**印です。第3〜4回で詳しく扱います。

まだ意味が分からない列があっても大丈夫です。今日は下の5列だけ使います。"""),
                markdown("""## モデルへ渡す列を決めて、学習させる

ここが今日の中心です。次のセルは4つの手順を続けて行っています。1行ずつ何をしているかは、
セルの下の「コードの読み方」で説明します。まず実行して、出てくる数字を眺めてください。

**なぜ「ベースライン」と比べるのか？** いきなり高機能なモデルの点数だけ見ても、それが
「すごい」のか「当たり前」なのか分かりません。そこで、**いつも多数派（ここでは非活性）と
答えるだけの単純なモデル**を先に用意し、本命がそれをどれだけ上回るかで価値を測ります。"""),
                code("""
                    from sklearn.model_selection import train_test_split
                    from sklearn.ensemble import RandomForestClassifier
                    from sklearn.dummy import DummyClassifier
                    from sklearn.metrics import accuracy_score, f1_score

                    features = ["molecular_weight", "logp", "tpsa", "h_bond_donors", "rotatable_bonds"]
                    X = df[features].fillna(df[features].median())
                    y = df["active"]
                    X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

                    baseline = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
                    model = RandomForestClassifier(n_estimators=200, max_depth=4, random_state=42).fit(X_train, y_train)
                    for name, estimator in {"多数派ベースライン": baseline, "Random Forest": model}.items():
                        pred = estimator.predict(X_valid)
                        print(f"{name:14s} accuracy={accuracy_score(y_valid, pred):.3f}  F1={f1_score(y_valid, pred):.3f}")
                """),
                markdown("""### コードの読み方（1行ずつ）

- `features = [...]`：モデルへ渡す**入力列の名前リスト**。ここでは分子の性質5つを選びました。
- `X = df[features].fillna(...)`：`X`は入力の表。`fillna(...median())`は、欠損を**その列の中央値で埋める**処理です（モデルは空欄を扱えないため）。※この回では簡単のため**分割の前**に補完していますが、本来は分割の後に行うべきで、その理由は第6回で学びます。
- `y = df["active"]`：`y`は答えの列（活性=1／非活性=0）。
- `train_test_split(...)`：データを**学習用（train）と検証用（valid）に分ける**関数。`test_size=0.25`で25%を検証用に取り置きます。未知データでの成績を測るため、検証用は学習に使いません。`random_state=42`は分け方を固定して**毎回同じ結果**にするための指定、`stratify=y`は活性の割合が両側で揃うようにする指定です。
- `.fit(X_train, y_train)`：**学習**。過去データ（train）から関係を覚えます。
- `.predict(X_valid)`：覚えた関係を**検証用の未知データ**へ当てはめて予測します。
- `print(f"...{accuracy_score(...):.3f}...")`：`f"..."`は文字と計算結果を混ぜて表示する書き方（f文字列）。`{値:.3f}`は**小数第3位まで**表示する指定です。桁を変えたいときはこの数字を変えます。

### 出力の読み方

- **accuracy（正解率）**：全体のうち何割を当てたか。
- **F1**：活性を「見つける力」と「間違えない力」のバランス（0〜1、高いほど良い）。活性が少ないデータでは正解率より頼りになります（第8回で詳説）。
- 見るべきは**Random Forestがベースラインをどれだけ上回ったか**。差が小さいなら、そのモデルはまだ価値を出せていません。"""),
                markdown("""## TRY：たった1試料を予測させてみる

モデルは表全体だけでなく、**1件ずつ**予測できます。検証用データの先頭1件を渡してみましょう。
`predict`は0か1の**判定**を、`predict_proba`は**活性である確率**を返します。"""),
                code("""
                    one_sample = X_valid.iloc[[0]]
                    display(one_sample)
                    print("予測クラス:", model.predict(one_sample)[0])
                    print("活性である確率:", round(model.predict_proba(one_sample)[0, 1], 3))
                """),
                markdown("""### 出力の読み方と、よくある勘違い

- 上の表がこの試料の**入力（特徴量）**、その下がモデルの**答え**です。
- **予測クラス**が`1`なら「活性ありと判定」、`0`なら「非活性と判定」。
- **確率0.8**は「80%の確信で活性」という**モデルの自信**であって、「必ず活性」という保証ではありません。ここを混同しないことが、今日いちばん大事な感覚です。
- `iloc[[0]]`と二重角括弧にしているのは、1行でも**表の形のまま**渡すためです（`iloc[0]`だと1次元になり、モデルが受け取れません）。"""),
                markdown("""## CORE深掘り：同じ評価は「関数」にまとめる

上では `accuracy_score(...)` と `f1_score(...)` を手で並べました。同じ評価を何度も書くと、
書き間違いが起きます。そこで**名前を付けた処理のかたまり（関数）**にまとめます。

- `def evaluate_classifier(...) -> dict:` の `-> dict` は「この関数は辞書を返す」という**型ヒント**（読み手への注釈）。
- 関数の1行目の文字列は**docstring**で、何をする関数かの説明です。
- `assert 条件, "メッセージ"` は「この条件が成り立たなければ止まれ」という**自己点検**。想定外の値が返っていないかを自動で見張ります。"""),
                code("""
                    def evaluate_classifier(estimator, X_valid, y_valid) -> dict:
                        "検証データでaccuracyとF1を計算し、辞書で返す純粋な評価関数。"
                        pred = estimator.predict(X_valid)
                        return {
                            "accuracy": round(accuracy_score(y_valid, pred), 3),
                            "f1": round(f1_score(y_valid, pred), 3),
                        }

                    scores = evaluate_classifier(model, X_valid, y_valid)
                    assert set(scores) == {"accuracy", "f1"}, "返す指標が想定と違います"
                    assert 0.0 <= scores["f1"] <= 1.0, "F1は0〜1のはず"
                    scores
                """),
                markdown("""### なぜ関数にすると良いのか

- **繰り返しに強い**：別のモデルを評価したいとき、`evaluate_classifier(別のモデル, ...)`と呼ぶだけ。
- **間違いに気づける**：`assert`があるので、うっかりF1が1.2のような有り得ない値になったら即座に止まります。
- **読みやすい**：中身を知らなくても関数名で「何をするか」が伝わります。

この「小さく作って、テストで守る」考え方は第2回でさらに練習します。"""),
                markdown("""## CHANGE：1か所だけ変えて、違いを観察する

`max_depth=4`（木の深さ）を`2`や`8`に変えて、上のセルを再実行してみましょう。
深くすると学習データには合いますが、検証スコアは必ずしも上がりません（**過学習**）。
変えた値・理由・結果を1行でメモしておきます。

## ASK COPILOT

M365 Copilotに、`fit`と`predict_proba`の違いを初心者向けに説明してもらいましょう。
返答を鵜呑みにせず、上の出力と照らして確かめます。

## まとめ

- 表の1行＝1試料、列＝情報。**特徴量（X）**を入れ、**目的変数（y）**を予測する。
- **fit=学習、predict=予測**。確率は「自信」であって真実ではない。
- 良し悪しは**ベースラインとの差**で測り、評価は**関数**にまとめて再利用する。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：木の深さと「過学習」を交差検証で見る

ここからは経験者・自習向けの発展です。1回の学習/検証の分け方だと、たまたま簡単な検証データに
当たって点数が良く見えることがあります。そこで**交差検証**を使います。

**交差検証（cross validation）とは**：データを5つに分け、「4つで学習→残り1つで検証」を
担当を変えて5回行い、5回のスコアを平均する方法です。1回だけの運・不運をならして、
より信頼できる成績を出します。

次の表では、木の深さ（`max_depth`）を変えながら、**学習F1**と**検証F1**の両方を出します。
学習F1だけが高くて検証F1が伸びない＝**過学習**（覚えすぎて未知に弱い）のサインです。"""),
            code("""
                import pandas as pd
                from sklearn.model_selection import cross_validate, StratifiedKFold

                cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
                rows = []
                for depth in [1, 2, 3, 4, 6, 8, None]:
                    estimator = RandomForestClassifier(n_estimators=200, max_depth=depth, random_state=42)
                    result = cross_validate(estimator, X, y, cv=cv, scoring="f1", return_train_score=True)
                    rows.append({
                        "max_depth": str(depth),
                        "学習F1": result["train_score"].mean(),
                        "検証F1": result["test_score"].mean(),
                        "検証F1_SD": result["test_score"].std(),
                    })
                pd.DataFrame(rows).round(3)
            """),
            markdown("""### 出力の読み方

- 上から下へ木を深くすると、**学習F1はほぼ単調に上がる**はずです（覚える力が増えるため）。
- 一方**検証F1**はどこかで頭打ち・悪化します。その手前が「ちょうど良い深さ」の目安です。
- `検証F1_SD`は5回のばらつき。小さいほど安定。**平均が少し高くてもSDが大きいモデル**は、運任せに近いので注意します。"""),
            markdown("""### 特徴量重要度は2種類を見比べる

「どの特徴量が効いているか」を知りたくなります。ただし木モデルが標準で出す**不純度重要度**は、
値の種類が多い列を過大評価する癖があります。そこで、**列の値をわざと混ぜて性能がどれだけ落ちるか**で
測る**並べ替え重要度（permutation importance）**と並べて読みます。落ち幅が大きい列ほど本当に効いています。"""),
            code("""
                from sklearn.inspection import permutation_importance

                perm = permutation_importance(model, X_valid, y_valid, scoring="f1", n_repeats=20, random_state=42)
                importance = pd.DataFrame({
                    "特徴量": features,
                    "不純度重要度": model.feature_importances_,
                    "並べ替え重要度": perm.importances_mean,
                    "並べ替えSD": perm.importances_std,
                }).sort_values("並べ替え重要度", ascending=False)
                importance.round(3)
            """),
            markdown("""### 出力の読み方

2つの列で順位が食い違ったら、**並べ替え重要度**を優先します。並べ替え重要度が0付近（SDより小さい）なら、
その特徴量は「効いているとは言い切れない」と読みます。"""),
            markdown("""## CHALLENGE：確率は「当たっている」か（較正）

モデルが「確率0.8」と言った試料たちは、本当に約80%が活性でしょうか。確率を確率帯ごとに束ね、
**その帯の実際の活性率**と見比べます。予測確率と実際がだいたい一致していれば、確率を意思決定に
使えます（この一致度を**較正**と呼び、第8回で詳しく扱います）。"""),
            code("""
                probability = model.predict_proba(X_valid)[:, 1]
                bucket = pd.cut(probability, bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0])
                calibration = (
                    pd.DataFrame({"確率帯": bucket, "実際の活性": y_valid.to_numpy()})
                    .groupby("確率帯", observed=True)["実際の活性"]
                    .agg(件数="size", 実際の活性率="mean")
                )
                calibration.round(3)
            """),
            markdown("""### 出力の読み方

各行は「その確率帯に入った試料の件数」と「実際に活性だった割合」です。
`0.6〜0.8`の帯で実際の活性率が0.7前後なら、確率はよく較正されています。大きくずれていたら、
確率の数字を鵜呑みにせず、順位付け（どれを先に試すか）にとどめる使い方が安全です。
なお件数が少ない帯は割合が不安定なので、件数も一緒に見ます。"""),
        ],
        [
            markdown("""## APPENDIX（任意・追加演習）

ここから先は90分では扱いません。手を動かして深めたい人向けの追加コードです。飛ばして次回へ進んでも
問題ありません。まずは**複数モデルを1つの関数でまとめて比較**します（第10回の予告編）。"""),
            code("""
                from sklearn.linear_model import LogisticRegression
                from sklearn.tree import DecisionTreeClassifier
                from sklearn.ensemble import HistGradientBoostingClassifier
                from sklearn.pipeline import make_pipeline
                from sklearn.impute import SimpleImputer

                def compare_models(candidates, X_tr, y_tr, X_va, y_va) -> pd.DataFrame:
                    "候補モデルを同じデータで学習し、accuracyとF1の表を返す。"
                    out = []
                    for name, est in candidates.items():
                        est.fit(X_tr, y_tr)
                        pred = est.predict(X_va)
                        out.append({"モデル": name, "accuracy": accuracy_score(y_va, pred), "F1": f1_score(y_va, pred)})
                    return pd.DataFrame(out).sort_values("F1", ascending=False).round(3)

                candidates = {
                    "多数派": DummyClassifier(strategy="most_frequent"),
                    "ロジスティック回帰": make_pipeline(SimpleImputer(strategy="median"), LogisticRegression(max_iter=1000)),
                    "決定木": DecisionTreeClassifier(max_depth=4, random_state=42),
                    "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=4, random_state=42),
                    "勾配ブースティング": HistGradientBoostingClassifier(max_iter=200, random_state=42),
                }
                compare_models(candidates, X_train, y_train, X_valid, y_valid)
            """),
            markdown("""### 出力の読み方

F1の高い順に5モデルが並びます。**最も複雑なモデルが必ず1位とは限らない**こと、そして
「多数派」を全モデルが上回っているかを確認します。この`compare_models`関数は、以降の回でも使い回せます。"""),
            markdown("""### ROC曲線と混同行列を並べて見る

分類の性能を2つの図で確認します。**ROC曲線**は閾値を動かしたときの当たり方を1本の曲線にしたもので、
曲線下の面積（AUC）が1に近いほど良い。**混同行列**は0.5で判定したときの内訳です。"""),
            code("""
                import matplotlib.pyplot as plt
                from sklearn.metrics import RocCurveDisplay, ConfusionMatrixDisplay

                fig, axes = plt.subplots(1, 2, figsize=(11, 4))
                RocCurveDisplay.from_estimator(model, X_valid, y_valid, ax=axes[0])
                axes[0].plot([0, 1], [0, 1], "--", color="gray")
                axes[0].set_title("ROC曲線（Random Forest）")
                ConfusionMatrixDisplay.from_estimator(model, X_valid, y_valid, display_labels=["非活性", "活性"], cmap="Blues", ax=axes[1])
                axes[1].set_title("混同行列（閾値0.5）")
                plt.tight_layout()
            """),
            markdown("""### 出力の読み方

- **ROC曲線**：左上に張り付くほど良く、対角線（点線）はランダム予測。凡例のAUCが目安の数字です。
- **混同行列**：右下（活性を活性と当てた数）と、左下（活性を見逃した数）に注目。第8回で本格的に読み解きます。
- 指標の詳しい意味は第8回で扱うので、ここでは「こういう図で確認できる」と体験できれば十分です。"""),
        ],
    )

    # ---- 第2回 ----
    write_notebook(
        "02-python-with-copilot",
        notebook(
            "第2回：Pythonを読み、Copilotと少し変える",
            "分からないコードを、どうやって小さく理解し、安全に書き換えるか。",
            [
                markdown("""## なぜ「読む」練習から始めるのか

これからの回では、完成したコードを**少しだけ書き換えて**実験します。ゼロから書けなくても、
**読めて・1か所いじれる**ようになれば十分に前へ進めます。この回は、以後ずっと出てくる
4つの部品（値・リスト・辞書・繰り返し・関数）に絞って読み方を身につけます。文法の網羅はしません。

Copilotは「一発で完成品を作らせる道具」ではなく、「短い相談を何度もする相棒」として使います。
提案は必ず1つずつ試し、出力を自分の目で確かめます。"""),
                markdown("""## 変数・リスト・辞書：データを入れる3つの箱

- **変数**：1つの値に名前を付けた箱（例：`sample_name`）。
- **リスト `[...]`**：順番のある複数の値（例：温度の並び）。
- **辞書 `{key: value}`**：名前で値を引く箱（例：`experiment["solvent"]`で溶媒を取り出す）。

`type(x)`は「その値が何型か」を教えてくれます。実行して、3つの箱の見た目の違いを確かめましょう。"""),
                code("""
                    sample_name = "CMP-0001"
                    temperatures = [60, 75, 90]
                    experiment = {"sample_id": sample_name, "solvent": "EtOH", "active": 1}
                    print(type(sample_name), sample_name)
                    print(type(temperatures), temperatures)
                    print(type(experiment), experiment)
                """),
                markdown("""### 出力の読み方

- `<class 'str'>`は**文字列**、`<class 'list'>`は**リスト**、`<class 'dict'>`は**辞書**。
- 辞書は`{'sample_id': 'CMP-0001', ...}`のように、**名前（キー）と値**の組で並びます。
- pandasの表（`df`）は、ざっくり言うと「辞書（列名→列の値）」と「リスト（行の並び）」を合わせたものです。この3つが分かると表データも読みやすくなります。"""),
                markdown("""## TRY：`for`（繰り返し）と`if`（条件分岐）を読む

`for`は「リストの要素を1つずつ取り出して同じ処理を繰り返す」書き方、`if ... else`は
「条件で処理を分ける」書き方です。**実行する前に、何行表示されるか予想**してから動かしましょう。
予想と結果を比べるのが、コードを読む力を最短で伸ばすコツです。"""),
                code("""
                    for temperature in temperatures:
                        label = "高温条件" if temperature >= 75 else "低温条件"
                        print(temperature, label)
                """),
                markdown("""### 出力の読み方

- `temperatures`は3要素なので**3行**出ます（予想は合っていましたか？）。
- 各行で`temperature`が60→75→90と変わり、`75以上か`で「高温／低温」が切り替わります。
- `A if 条件 else B`は「条件が真ならA、偽ならB」を1行で書く形。`if:` を複数行で書いても同じ意味です。"""),
                markdown("""## 関数：処理に名前を付けて再利用する

**関数**は「入力を受け取り、決まった処理をして、結果を返す」部品です。同じ計算を何度も書かずに済みます。

- `def 関数名(引数: 型) -> 戻り値の型:` の**型ヒント**は、読み手（と生成AI）への注釈です。動作は変えませんが、誤解を減らします。
- 直後の文字列は**docstring**（関数の説明）。`help(関数)`で読めます。
- `[celsius_to_kelvin(v) for v in temperatures]`は**リスト内包表記**。「各要素に関数をかけた新しいリスト」を1行で作ります。"""),
                code("""
                    def celsius_to_kelvin(celsius: float) -> float:
                        "摂氏をケルビンへ変換する。"
                        return celsius + 273.15

                    converted = [celsius_to_kelvin(value) for value in temperatures]
                    print(converted)
                    help(celsius_to_kelvin)
                """),
                markdown("""### 出力の読み方

- `converted`は、各温度に273.15を足したリスト（例：`[333.15, 348.15, 363.15]`）。
- `help(...)`は、書いておいたdocstringと引数の形を表示します。**自分の関数にも説明が付く**ことを体験しておきましょう。"""),
                markdown("""## TRY：エラーは「読む」もの。省略せず全文を見る

エラーは失敗ではなく、**どこで何が起きたかの手がかり**です。わざと存在しない要素を取り出して、
エラーの形を観察します。`try/except`は「エラーが出ても止まらず、内容を受け取る」書き方です。"""),
                code("""
                    try:
                        temperatures[10]
                    except Exception as error:
                        print(type(error).__name__)
                        print(error)
                """),
                markdown("""### 出力の読み方

- `IndexError`という**エラーの種類（名前）**と、`list index out of range`という**説明**が出ます。
- リストは0番から数えるので、3要素の`temperatures`に`[10]`は存在せず、範囲外エラーになります。
- 実際のエラーでは、**末尾の1〜2行**（種類とメッセージ）にいちばん近い原因が書かれています。Copilotに貼るときも、この全文を省略しないことが大切です。"""),
                markdown("""## CHANGE

`temperatures`へ温度を1つ追加し、`for`ループと変換結果の表示がどう変わるか確認します。

## ASK COPILOT

気になるセルを貼り、「各行の実行後に、変数の型と中身がどう変わるか表で説明して」と依頼します。
提案は1つずつ試し、必ず出力で答え合わせをします。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：テストで守る小さなユーティリティ

ここからは発展です。「実行できる」ことと「正しい」ことは別物です。特にCopilotが書いたコードは、
**普通の入力では動いても、変な入力で静かに間違える**ことがあります。そこで、**変な入力を先に想定して
弾く関数**を書きます。

- `raise TypeError(...)` / `raise ValueError(...)` は、「この入力は受け付けない」と**わざとエラーを起こす**書き方。
- こうしておくと、間違った使い方をした人にすぐ気づいてもらえます（沈黙して誤った答えを返すより安全）。"""),
            code("""
                def celsius_to_kelvin_checked(celsius: float) -> float:
                    "型と物理的な下限を検査してから摂氏をケルビンへ変換する。"
                    if not isinstance(celsius, (int, float)):
                        raise TypeError("温度は数値で入力してください")
                    if celsius < -273.15:
                        raise ValueError("絶対零度より低い値は指定できません")
                    return celsius + 273.15

                for value in [25, -273.15, -300, "25"]:
                    try:
                        print(value, "->", round(celsius_to_kelvin_checked(value), 2))
                    except (TypeError, ValueError) as error:
                        print(value, "->", type(error).__name__, error)
            """),
            markdown("""### 出力の読み方

4つの入力それぞれの結果が並びます。`25`は正常変換、`-273.15`は境界（絶対零度ちょうど）でOK、
`-300`は物理的にありえないので`ValueError`、`"25"`は数値でなく文字列なので`TypeError`。
**正常・境界・異常**を1度に確かめられました。"""),
            markdown("""### assertで「期待する答え」を先に書いて固定する

`assert 式` は「式が真でなければ止まれ」という自己点検でした。これを使うと、関数の**テスト**が書けます。
コツは、**答えを先に書いてから**関数を作ること。ここではIQR法（四分位範囲）で外れ値を除く関数を、
正常・空リスト・NaN混在の3ケースで検証します。"""),
            code("""
                import numpy as np

                def drop_outliers_iqr(values: list[float], k: float = 1.5) -> list[float]:
                    "IQR法で外れ値を除いた値のリストを返す。NaNは事前に除く。"
                    clean = [v for v in values if v == v]  # NaN(v != v)を除外
                    if not clean:
                        return []
                    q1, q3 = np.percentile(clean, [25, 75])
                    iqr = q3 - q1
                    low, high = q1 - k * iqr, q3 + k * iqr
                    return [v for v in clean if low <= v <= high]

                assert drop_outliers_iqr([10, 11, 12, 13, 1000]) == [10, 11, 12, 13]
                assert drop_outliers_iqr([]) == []
                assert drop_outliers_iqr([5, 5, float("nan")]) == [5, 5]
                print("すべてのテストを通過しました")
            """),
            markdown("""### 出力の読み方

- 3つの`assert`がすべて通ると、最後の`print`だけが表示されます。**エラーが出ない＝合格**です。
- もし関数を壊すと（例：`k`を0にする）、どの`assert`で止まったかが表示され、**間違いの場所がすぐ分かります**。
- `v == v`が`False`になるのはNaNだけ、という小技で欠損を除いています。"""),
            markdown("""## CHALLENGE：関数の「性質」を調べる

外れ値を除いた後、もう一度同じ関数をかけると、さらに減るでしょうか。1回目で四分位が変わるため、
**必ずしも同じ結果（冪等）にはなりません**。こうした「関数の性質」を意識すると、思わぬ副作用に気づけます。"""),
            code("""
                rng = np.random.default_rng(0)
                sample = rng.normal(50, 5, 200).tolist()
                once = drop_outliers_iqr(sample)
                twice = drop_outliers_iqr(once)
                print("1回適用後の件数:", len(once))
                print("2回目でさらに減った件数:", len(once) - len(twice))
                print("2回目で変化なし(冪等):", once == twice)
            """),
            markdown("""### 出力の読み方

`2回目でさらに減った件数`が0でなければ、この関数は**冪等ではない**（適用回数で結果が変わる）と分かります。
外れ値除去を繰り返し適用する前処理は、この性質のせいで「消しすぎ」が起きやすい、という教訓につながります。"""),
        ],
        [
            markdown("""## APPENDIX（任意・追加演習）

90分の外で、以後よく使うPythonの部品をもう少し練習します。飛ばしても本編は進められます。
まずは`enumerate`（番号付き繰り返し）・`zip`（同時に回す）・`sorted`（並べ替え）・条件付き内包表記です。"""),
            code("""
                samples = ["CMP-0001", "CMP-0002", "CMP-0003"]
                yields = [82.5, 40.1, 63.7]

                for i, name in enumerate(samples, start=1):        # 番号付きで回す
                    print(i, name)

                pairs = {name: y for name, y in zip(samples, yields)}   # 2つを同時に回して辞書化
                print("辞書:", pairs)

                ranked = sorted(pairs.items(), key=lambda kv: kv[1], reverse=True)  # 収率降順
                print("収率降順:", ranked)

                high = [name for name, y in pairs.items() if y >= 60]   # 条件付き内包表記
                print("収率60以上:", high)
            """),
            markdown("""### 出力の読み方

- `enumerate`は`(番号, 要素)`を返すので、行番号付きの表示に便利。
- `zip`は複数リストを同時に回します。`for a, b in zip(...)`の形は頻出です。
- `sorted(..., key=..., reverse=True)`で並べ替え。`key`に「何で並べるか」を関数で渡します。
- これらは`for`ループを短く読みやすくする道具で、pandasの内部でも同じ発想が使われています。"""),
            markdown("""### 自分の「状態を持つ部品」を作る（クラス入門）

関数は入力→出力の1回きりですが、**クラス**は状態を持ち続けられます。値を足しながら件数と平均を
保つ小さなクラスを書き、`assert`で動作を確かめます。難しければ「こういう書き方がある」で十分です。"""),
            code("""
                class RunningStats:
                    "値を1つずつ足しながら件数・合計・平均を保つ小さなクラス。"
                    def __init__(self):
                        self.n = 0
                        self.total = 0.0
                    def add(self, value: float) -> None:
                        self.n += 1
                        self.total += value
                    @property
                    def mean(self) -> float:
                        return self.total / self.n if self.n else float("nan")

                stats = RunningStats()
                for y in [82.5, 40.1, 63.7]:
                    stats.add(y)
                assert stats.n == 3
                assert abs(stats.mean - 62.1) < 0.1
                print(f"件数={stats.n} 平均={stats.mean:.1f}")
            """),
            markdown("""### 出力の読み方

`add`を呼ぶたびに内部の`n`と`total`が更新され、`mean`はいつでも現在の平均を返します。`assert`が通れば
実装は期待どおり。scikit-learnのモデルも「`fit`で状態を覚え、`predict`で使う」クラスなので、この
仕組みが分かると内部のイメージがつかめます。"""),
            markdown("""### pandasに橋渡しする

第3回で本格的に使うpandasを、ひと足先に少しだけ触ります。CSVを読み、1列（Series）の平均や
種類を取り出します。"""),
            code("""
                import pandas as pd

                data = pd.read_csv(DATA / "compound_experiments.csv")
                print("1列の型:", type(data["yield_pct"]).__name__)
                print("平均収率:", round(data["yield_pct"].mean(), 1))
                print("溶媒の種類:", data["solvent"].dropna().unique().tolist())
            """),
            markdown("""### 出力の読み方

`data["yield_pct"]`は1列（Series）で、`.mean()`のような集計をそのまま呼べます。`.unique()`は値の種類、
`.dropna()`は欠損を除く指定。ここまで来れば、第3回のpandasはぐっと読みやすくなります。"""),
        ],
    )

    # ---- 第3回 ----
    write_notebook(
        "03-pandas",
        notebook(
            "第3回：pandasで表データに触る",
            "初めて見る表データを受け取ったら、最初に何を見るか。",
            [
                markdown("""## pandasは「表を操る道具」

pandasは、Excelのような表（DataFrame）をPythonで扱うライブラリです。研究データの多くは表なので、
これが読めると分析の8割は前に進みます。この回で身につけるのは、初見の表に対して**同じ手順で
最初の点検をする**習慣です。

初見データを受け取ったら、まず次の4つを見ます：**大きさ（行数×列数）／型（数値か文字か）／
欠損（空欄はどこか）／ばらつき（平均や範囲）**。"""),
                common_load_cell(),
                markdown("""## TRY：表の「健康診断」を1度に行う

次のセルは、点検の4項目をまとめて表示します。`df.shape`で大きさ、`df.dtypes`で型、
`df.isna()`で欠損、`df.describe()`で要約統計。**関数名がそのまま意味**なので、少しずつ覚えられます。"""),
                code("""
                    print("形:", df.shape)
                    quality = pd.DataFrame({
                        "データ型": df.dtypes.astype(str),
                        "欠損数": df.isna().sum(),
                        "欠損率": df.isna().mean().round(3),
                        "ユニーク数": df.nunique(),
                    })
                    display(quality)
                    display(df.select_dtypes(include="number").describe().T.round(2))
                """),
                markdown("""### 出力の読み方

- **1つ目の表（品質表）**：各列の型・欠損数・欠損率・値の種類数。`object`は文字列、`float64`/`int64`は数値。欠損率が高い列や、`sample_id`のようにユニーク数＝行数の列（＝ただの名札）に気づけます。
- **2つ目の表（describe）**：数値列の件数・平均・標準偏差・最小/四分位/最大。`temperature_c`の`max`が極端に大きいなど、**怪しい値の当たり**をここで付けます。
- `.T`は表を**転置**（行列入れ替え）して、列がたくさんあっても縦に読めるようにする工夫です。"""),
                markdown("""## 行と列を選ぶ：`loc` と `query`

分析は「必要な部分だけ取り出す」の連続です。2つの基本を覚えます。

- `df.loc[行の条件, 列のリスト]`：**場所を指定して取り出す**。
- `df.query("条件式")`：**条件を文章のように書いて絞り込む**。複数条件（`and`/`or`）が読みやすいのが利点です。"""),
                code("""
                    columns = ["sample_id", "solvent", "catalyst", "temperature_c", "yield_pct", "active"]
                    display(df.loc[:4, columns])
                    subset = df.query("catalyst == 'Cat-A' and temperature_c >= 80")[columns]
                    print("Cat-Aかつ80℃以上:", len(subset), "件")
                    subset.head()
                """),
                markdown("""### 出力の読み方とつまずきポイント

- `df.loc[:4, columns]`は「行番号0〜4」×「指定した6列」。`loc`の範囲指定は**末尾を含む**点がPythonの通常のスライス（末尾を含まない）と違うので注意します。
- `query`の中では、文字列は`'Cat-A'`のように**引用符**で囲みます。列名はそのまま書けます。
- `len(subset)`で、条件に合った件数が分かります。**まず件数を確かめる**のは、絞り込みが意図どおりかの安全確認です。"""),
                markdown("""## TRY：カテゴリごとにまとめて比べる（groupby）

「溶媒ごとの平均収率は？」のような問いには`groupby`が使えます。**同じ値の行をまとめて、
件数・平均・ばらつきなどを一気に計算**します。平均だけでなく**件数（size）とばらつき（std）**も
一緒に見るのが、だまされないコツです。"""),
                code("""
                    solvent_summary = (
                        df.groupby("solvent", dropna=False)
                          .agg(件数=("sample_id", "size"), 平均収率=("yield_pct", "mean"),
                               収率SD=("yield_pct", "std"), 活性率=("active", "mean"))
                          .sort_values("平均収率", ascending=False)
                    )
                    solvent_summary.round(2)
                """),
                markdown("""### 出力の読み方

- 溶媒ごとに1行、件数・平均収率・収率のばらつき・活性率が並び、平均収率の高い順に並びます。
- **平均が高くても件数が極端に少ない**溶媒は、たまたまかもしれません。件数の小さい行の平均は割り引いて読みます。
- `dropna=False`にしているので、溶媒が欠損の行も1グループとして見えます（欠損を見逃さない工夫）。"""),
                markdown("""## CHANGE

`groupby("solvent")`を`"catalyst"`や`"scaffold_group"`へ変えて、順位がどう変わるか見ます。
順位が変わる理由は、**データだけから断定せず仮説として**書き留めます（第4〜5回でその検証を学びます）。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：多軸集計・処理の連結・速度

発展として、実務でよく使う3つを扱います。**pivot_table**（2軸のクロス集計）、
**pipe**（処理を関数でつなぐ）、そして**ベクトル化**（速く書く）です。"""),
            markdown("""### pivot_table：2つの軸で同時に集計する

「触媒×溶媒」のように2軸で平均を見たいときは`pivot_table`が便利です。Excelのピボットテーブルと
同じ発想で、`index`（縦軸）・`columns`（横軸）・`values`（集計する値）・`aggfunc`（集計方法）を指定します。"""),
            code("""
                pivot = pd.pivot_table(df, index="catalyst", columns="solvent", values="yield_pct", aggfunc=["count", "mean"])
                pivot.round(1)
            """),
            markdown("""### 出力の読み方

行が触媒、列が溶媒で、各マスに「件数」と「平均収率」が入ります。件数が0や極端に少ないマスは、
平均が空欄や不安定になります。**組み合わせによって効き方が変わる**様子（交互作用）の当たりを付けられます。"""),
            markdown("""### pipe：処理を「関数の流れ」としてつなぐ

複数の加工を続けるとき、中間変数を増やすと読みにくくなります。`.pipe(関数)`を使うと、
**表を関数に通して次へ渡す**流れを、上から下へ素直に書けます。元データを壊さないよう、関数内で`copy()`します。"""),
            code("""
                def add_quality_flags(frame):
                    "収率の中央値以上かどうかのフラグ列を足して返す（元は変更しない）。"
                    out = frame.copy()
                    out["high_yield"] = out["yield_pct"] >= out["yield_pct"].median()
                    return out

                summary = (
                    df
                    .pipe(add_quality_flags)
                    .groupby(["catalyst", "high_yield"], observed=True)
                    .agg(件数=("sample_id", "size"), 平均収率=("yield_pct", "mean"))
                    .round(2)
                )
                summary
            """),
            markdown("""### 出力の読み方

触媒×「高収率かどうか」で件数と平均収率が出ます。**加工（フラグ付け）→集計**という流れが、
1つの縦長の式で読める点に注目してください。処理が増えても`.pipe(...)`を足すだけで拡張できます。"""),
            markdown("""## CHALLENGE：`apply`と「ベクトル化」の速度差

同じ判定を2通りで書き、時間を比べます。行を1つずつ処理する`apply`は読みやすい一方、遅くなりがち。
列全体へ一括で演算する**ベクトル化**は速く、pandasの本領です。"""),
            code("""
                import time

                def slow_flag(frame):
                    return frame.apply(lambda r: r["temperature_c"] >= 80 and r["catalyst"] == "Cat-A", axis=1)

                def fast_flag(frame):
                    return (frame["temperature_c"] >= 80) & (frame["catalyst"] == "Cat-A")

                t0 = time.perf_counter(); a = slow_flag(df); t1 = time.perf_counter()
                b = fast_flag(df); t2 = time.perf_counter()
                print("apply     :", round((t1 - t0) * 1000, 2), "ms")
                print("vectorized:", round((t2 - t1) * 1000, 2), "ms")
                print("結果一致:", bool((a.fillna(False) == b.fillna(False)).all()))
            """),
            markdown("""### 出力の読み方

- 2つの時間（ミリ秒）を比べると、**ベクトル化の方が速い**はずです。420行では差は小さくても、数十万行では体感が大きく変わります。
- `結果一致: True`は、2つの書き方が**同じ答え**を出した確認。速く書いても結果が同じであることを、必ず検証します。
- 教訓：`apply`が必要な場面もありますが、まず「列演算で書けないか」を考える習慣が、速く読みやすいコードにつながります。"""),
        ],
        [
            markdown("""## APPENDIX（任意・追加演習）

実データで頻出のpandas操作を、もう少し重めに練習します。90分の外の自習向けです。
まずは**度数の集計**（`value_counts`）と**クロス集計**（`crosstab`）です。"""),
            code("""
                print(df["catalyst"].value_counts(dropna=False))
                print()
                display(pd.crosstab(df["catalyst"], df["solvent"]))
            """),
            markdown("""### 出力の読み方

- `value_counts`は各カテゴリの件数を多い順に。`dropna=False`で欠損も1カテゴリとして数えます。
- `crosstab`は2つのカテゴリの組み合わせ件数の表。どの触媒×溶媒の組が多い／少ないかが一望できます。件数の少ない組は、後の分析で平均が不安定になりやすい箇所です。"""),
            markdown("""### 日付を扱う（datetime）

`experiment_date`は文字列です。`pd.to_datetime`で日付型に変えると、月ごとの集計や期間の計算ができます。
時系列の分割（第6回）にもつながる大事な操作です。"""),
            code("""
                dated = df.copy()
                dated["experiment_date"] = pd.to_datetime(dated["experiment_date"])
                dated["month"] = dated["experiment_date"].dt.to_period("M").astype(str)
                monthly = dated.groupby("month").agg(件数=("sample_id", "size"), 平均収率=("yield_pct", "mean")).round(1)
                display(monthly.head(6))
            """),
            markdown("""### 出力の読み方

月ごとの件数と平均収率が並びます。`.dt.to_period("M")`で「年月」に丸めています。実データでは、
月やバッチで性能が変わることがあり、こうした時間軸の集計が異常検知や分割設計の入口になります。"""),
            markdown("""### 表をつなぐ（merge）と、形を変える（melt）

`merge`は2つの表をキーで結合します。ここでは「触媒ごとの平均収率」を各行に付け直し、
各試料が平均より上か下かを計算します。`melt`は横広の表を縦長へ変える操作です。"""),
            code("""
                group_mean = df.groupby("catalyst")["yield_pct"].mean().rename("触媒平均収率").reset_index()
                merged = df[["sample_id", "catalyst", "yield_pct"]].merge(group_mean, on="catalyst")
                merged["平均との差"] = (merged["yield_pct"] - merged["触媒平均収率"]).round(1)
                display(merged.head())

                wide = df.head(3)[["sample_id", "molecular_weight", "logp", "tpsa"]]
                long = wide.melt(id_vars="sample_id", var_name="記述子", value_name="値")
                display(long)
            """),
            markdown("""### 出力の読み方

- **merge後**：各試料に「触媒平均収率」列が付き、「平均との差」で相対評価ができます。この「群平均を特徴量にする」発想は第11回のtarget encodingにつながります（ただしリークに注意）。
- **melt後**：3列だった記述子が「記述子・値」の2列に畳まれ、行数が増えます。可視化ライブラリはこの縦長形式を好むことが多いです。"""),
        ],
    )

    # ---- 第4回 ----
    write_notebook(
        "04-eda",
        notebook(
            "第4回：データ探偵—分布・欠損・外れ値",
            "モデルを作る前に、データの怪しいところをどう見つけるか。",
            [
                markdown("""## EDA＝モデルを作る前にデータをよく見る工程

EDA（探索的データ分析）は、いきなりモデルを作らず、まずデータをよく見る工程です。目的は
「きれいなグラフを作ること」ではなく、**モデルを惑わせる怪しい点（偏り・欠損・外れ値）を先に見つけ、
検証できる仮説を作ること**です。

見る順番にはコツがあります：**1変数（分布）→ 2変数（関係）→ 群別（カテゴリごと）**。
いきなり複雑な図に行かず、単純な図から積み上げます。次のセルはまず描画の下準備（日本語表示と
見た目のテーマ設定）です。"""),
                common_load_cell(),
                font_cell("""
                    import seaborn as sns
                    sns.set_theme(style="whitegrid")
                """),
                markdown("""## TRY：1変数の分布を見る（ヒストグラムと箱ひげ図）

まず1列ずつ「値がどこに、どれだけあるか」を見ます。

- **ヒストグラム**：値を区間に分け、各区間の件数を棒で表す。山の形・偏り・飛び離れた値が見えます。
- **箱ひげ図**：中央値・四分位・外れ値候補（ひげの外の点）をコンパクトに表す。外れ値探しに向きます。"""),
                code("""
                    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
                    sns.histplot(data=df, x="yield_pct", bins=20, ax=axes[0])
                    axes[0].set_title("収率の分布")
                    sns.boxplot(data=df, x="reaction_time_h", ax=axes[1])
                    axes[1].set_title("反応時間：外れ値候補を探す")
                    plt.tight_layout()
                """),
                markdown("""### 出力の読み方

- **左（収率のヒストグラム）**：山が1つか2つか、左右どちらに裾を引くかを見ます。裾が長い＝一部に極端な値。
- **右（反応時間の箱ひげ図）**：箱が中央50%、ひげの外の点が外れ値候補。**右端にぽつんと離れた点**があれば、それが要調査の試料です（このデータには意図的に極端な値を仕込んであります）。
- まだ「削除」はしません。EDAは**見つける**段階です。"""),
                markdown("""## 2変数の関係とカテゴリ比較（散布図・箱ひげ図）

次に「2つの列の関係」を見ます。散布図は連続値どうしの関係、色分け（`hue`）で3つ目の情報（触媒）も
重ねられます。カテゴリごとの違いは箱ひげ図で比べます。"""),
                code("""
                    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
                    sns.scatterplot(data=df, x="temperature_c", y="yield_pct", hue="catalyst", alpha=0.65, ax=axes[0])
                    axes[0].set_title("温度と収率")
                    sns.boxplot(data=df, x="catalyst", y="yield_pct", ax=axes[1])
                    axes[1].set_title("触媒別の収率")
                    plt.tight_layout()
                """),
                markdown("""### 出力の読み方

- **左（温度×収率）**：右肩上がりの直線ではなく、**中くらいの温度で収率が高くなる山型**に見えるはずです。「関係＝直線」とは限らないことを、目で確認しておきます（第4回DEEP DIVEの相互情報量につながります）。
- 点の色（触媒）で**かたまり**ができていれば、触媒が収率に効いている手がかり。
- **右（触媒別の箱ひげ）**：触媒ごとに箱の高さ（収率の中心）が違えば、触媒の効果が疑われます。ただし件数が少ない触媒は割り引いて読みます。"""),
                markdown("""## TRY：欠損と「明らかに怪しい値」を表で押さえる

図で当たりを付けたら、表で具体的に特定します。どの列にいくつ欠損があるか、そして温度が異常に
大きい上位5件を実際に取り出します。"""),
                code("""
                    missing = df.isna().sum().sort_values(ascending=False)
                    display(missing[missing > 0].to_frame("欠損数"))
                    display(df.nlargest(5, "temperature_c")[["sample_id", "temperature_c", "reaction_time_h", "yield_pct"]])
                """),
                markdown("""### 出力の読み方

- **1つ目の表**：欠損のある列と件数。欠損の多い列は、後で「埋める／落とす／別扱い」の判断が要ります。
- **2つ目の表**：温度が高い順の5件。`180.0`のような**周囲から突出した値**があれば、入力ミスか特殊な実験かを疑い、`sample_id`を控えて確認先を考えます。
- ここでも即削除しないのが鉄則。**「誰に確認するか」「残した場合に何が起きるか」**まで考えてから対処します。"""),
                markdown("""## CHANGE

散布図の色分け（`hue`）を`catalyst`から`solvent`へ変え、見え方の違いを1つ挙げます。

## 注意

外れ値＝入力ミス、ではありません。本物の珍しい現象のこともあります。EDAの結論は「削除」ではなく、
**「確認すべき仮説」**の形で残します。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：印象を統計量で裏づける

図の印象は主観的です。ここでは4つの道具で客観化します：**相関**（直線的な関係）、
**相互情報量**（曲がった関係も拾う）、**欠損機構**（欠損の起こり方）、**多変量外れ値**（組み合わせの異常）。"""),
            markdown("""### 相関ヒートマップ：全列の関係を一望する

`corr()`は数値列すべての**相関係数**（-1〜+1）を計算します。+1に近いほど一緒に増え、-1に近いほど
片方が増えると片方が減る関係。色の濃淡で一望できます。ただし**相関は「直線的な」関係しか測れない**
ことに注意します。"""),
            code("""
                numeric_cols = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa", "yield_pct"]
                correlation = df[numeric_cols].corr()
                plt.figure(figsize=(8, 5))
                sns.heatmap(correlation, annot=True, fmt=".2f", cmap="coolwarm", center=0)
                plt.title("数値列の相関（因果ではない）")
                plt.tight_layout()
            """),
            markdown("""### 出力の読み方

- 対角線は自分自身との相関で必ず1.00。赤いマスほど正、青いマスほど負の相関。
- `temperature_c`と`yield_pct`の相関は**意外と弱い**はずです（山型の関係なので直線相関では捉えきれない）。
- **重要**：相関は因果ではありません。「AとBが一緒に動く」ことと「AがBの原因」は別物です。"""),
            markdown("""### 相互情報量：曲がった関係も拾う

温度のように「最適点で収率が最大」の山型は、相関では弱く見えます。**相互情報量**は直線に限らず
「片方を知るともう片方の予想がどれだけ絞れるか」を測るので、こうした関係を拾えます。相関と並べて読みます。"""),
            code("""
                from sklearn.feature_selection import mutual_info_regression

                mi_source = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
                mi_frame = df[mi_source + ["yield_pct"]].dropna()
                mi = mutual_info_regression(mi_frame[mi_source], mi_frame["yield_pct"], random_state=42)
                pearson = mi_frame[mi_source].corrwith(mi_frame["yield_pct"]).abs()
                compare = pd.DataFrame({"相互情報量": mi, "|相関|": pearson.to_numpy()}, index=mi_source)
                compare.sort_values("相互情報量", ascending=False).round(3)
            """),
            markdown("""### 出力の読み方

`temperature_c`は**相互情報量は大きいのに|相関|は小さい**、という食い違いが見えるはずです。これが
「相関だけで特徴量を捨ててはいけない」理由です。両方を見て、関係の形は散布図で確かめます。"""),
            markdown("""### 欠損の起こり方（欠損機構）を疑う

欠損はランダムとは限りません。**MCAR**（完全にランダム）、**MAR**（他の列で説明できる偏り）、
**MNAR**（値そのものに依存）で対処が変わります。ここでは「温度の欠損率が溶媒で偏るか」を見ます。"""),
            code("""
                miss = df.assign(temp_missing=df["temperature_c"].isna())
                by_solvent = miss.groupby("solvent", dropna=False)["temp_missing"].mean().round(3)
                print("溶媒別の温度欠損率:")
                print(by_solvent)
                print("溶媒でほぼ一定ならMCARに近い。偏るならMARを疑う。")
            """),
            markdown("""### 出力の読み方

溶媒によって温度欠損率が大きく違えば、欠損は溶媒と関係している（MARの疑い）＝
「一律に中央値で埋める」のが危ういサインです。値がほぼ一定なら、単純な補完でも大きな害は出にくいと判断できます。"""),
            markdown("""### 多変量外れ値：組み合わせの異常を探す

「温度は普通、時間も普通、でもその組み合わせは他にない」という試料は、1列ずつ見ても見つかりません。
`IsolationForest`は**複数列を同時に見て、周囲から孤立した点**を外れ値候補として検出します。"""),
            code("""
                from sklearn.ensemble import IsolationForest

                iso_cols = ["temperature_c", "reaction_time_h", "concentration_m", "yield_pct"]
                iso_data = df[iso_cols].fillna(df[iso_cols].median())
                flags = IsolationForest(contamination=0.03, random_state=42).fit_predict(iso_data)
                outliers = df.loc[flags == -1, ["sample_id", *iso_cols]]
                print("多変量外れ値候補:", len(outliers), "件")
                outliers.round(2)
            """),
            markdown("""### 出力の読み方

- `contamination=0.03`は「全体の約3%を外れ値候補とみなす」設定です（多すぎ・少なすぎると感じたら調整）。
- 出た試料を1件ずつ見て、**どの列の組み合わせが変か**を考えます。単変量の箱ひげ図では正常だった試料が混じっていれば、多変量で見る価値があった、ということです。
- ここでも自動削除はせず、確認対象のリストとして扱います。"""),
        ],
        [
            markdown("""## APPENDIX（任意・追加演習）

可視化の引き出しを増やします。90分の外の自習向けです。まず**pairplot**で、複数の数値列の関係を
一度に俯瞰します（散布図と分布のマトリクス）。"""),
            code("""
                subset = df[["temperature_c", "reaction_time_h", "yield_pct", "catalyst"]].dropna()
                sns.pairplot(subset, hue="catalyst", corner=True, plot_kws={"alpha": 0.5})
            """),
            markdown("""### 出力の読み方

対角線は各列の分布、対角線以外は2列の散布図で、色は触媒。**触媒ごとにかたまりができている**列の組が
あれば、それが効いている手がかり。多くの列を一気に眺めて当たりを付け、気になったペアを個別の図で
深掘りします（俯瞰→詳細の順）。"""),
            markdown("""### バイオリン図とカウント図

**バイオリン図**は箱ひげ図より分布の形（山が1つか2つか）が分かります。**カウント図**はカテゴリの件数。
分布の形と件数を押さえると、平均の解釈がぐっと安全になります。"""),
            code("""
                fig, axes = plt.subplots(1, 2, figsize=(12, 4))
                sns.violinplot(data=df, x="catalyst", y="yield_pct", ax=axes[0])
                axes[0].set_title("触媒別の収率分布（バイオリン）")
                sns.countplot(data=df, x="solvent", ax=axes[1])
                axes[1].set_title("溶媒の件数")
                plt.tight_layout()
            """),
            markdown("""### 出力の読み方

- **バイオリン**：横幅が太い高さに値が集まっています。二山（2つのふくらみ）なら、隠れた別グループの存在を疑います。
- **カウント図**：件数の少ない溶媒は、以降の群別集計で平均が不安定になりやすい箇所。分析前に把握しておきます。"""),
            markdown("""### 群別の目的変数と、目的変数との関連を棒で見る

「触媒別の活性率」と「収率との|相関|が強い列」を棒グラフで並べます。EDAの締めとして、
**目的変数（active/yield）に効きそうな列**の当たりを付けます。"""),
            code("""
                active_rate = df.groupby("catalyst")["active"].mean().sort_values(ascending=False)
                corr_target = df.select_dtypes("number").corr()["yield_pct"].drop("yield_pct").abs().sort_values(ascending=False)
                fig, axes = plt.subplots(1, 2, figsize=(12, 4))
                active_rate.plot.bar(ax=axes[0], title="触媒別の活性率")
                corr_target.plot.bar(ax=axes[1], title="収率との|相関|")
                plt.tight_layout()
            """),
            markdown("""### 出力の読み方

- **左**：触媒によって活性率が違えば、触媒は分類（active）に効く候補。
- **右**：収率との|相関|が高い列が、回帰（yield）で効く候補。ただし第4回本編のとおり、相関が低くても相互情報量が高い列（温度など）を見落とさないよう、相関の棒だけで判断しないこと。
- ここで挙がった候補列が、第5回以降の特徴量選びの出発点になります。"""),
        ],
    )

    # ---- 第5回 ----
    write_notebook(
        "05-problem-framing",
        notebook(
            "第5回：何を、いつ、何のために予測するか",
            "モデル構築より前に決めるべきことは何か。",
            [
                markdown("""## 「良いモデル」の前に「正しい問い」

初心者がいちばん飛ばしがちで、実は最も効くのがこの回です。**どんなに精度が高くても、問いの立て方が
間違っていれば役に立ちません**。モデルを組む前に、次を1文で言えるようにします。

> **誰が・いつ・何を予測し・その結果をどう使うか。**

例：*実験条件を決める時点で使える情報から収率を予測し、優先して試す条件を選ぶ。*

ここで決定的に大事なのが**予測時点**です。「いつ予測するか」を決めると、その時点で**まだ手に入って
いない情報は使えない**と分かります。実験後にしか得られない値を入力に混ぜると、練習では高得点でも
本番でまったく使えない「ズル（リーク）」になります。"""),
                common_load_cell(),
                markdown("""## 計画時に使える列／使えない列を仕分ける

このデータで「実験条件を決める時点」を予測時点とすると、収率・活性・純度・測定後シグナルは
**まだ存在しません**。使える列と使えない列を、はっきり2つのリストに分けます。この仕分けが
特徴量選びの土台になります。"""),
                code("""
                    available_at_planning = [
                        "scaffold_group", "solvent", "catalyst", "temperature_c", "reaction_time_h",
                        "concentration_m", "molecular_weight", "logp", "tpsa", "h_bond_donors", "rotatable_bonds",
                    ]
                    unavailable_at_planning = ["yield_pct", "active", "post_assay_signal", "purity_pct"]
                    print("計画時に使える列:", available_at_planning)
                    print("実験後に得られる列:", unavailable_at_planning)
                """),
                markdown("""### 読みどころ

`unavailable_at_planning`の列は「結果」や「結果に強く連動する測定値」です。これらを特徴量に入れると
リークになります。**列の名前ではなく「その値がいつ確定するか」で判断する**のがコツです。"""),
                markdown("""## TRY：まず「単純な基準（ベースライン）」を作る

複雑なモデルに進む前に、**平均値だけ／多数派だけ**を答える最も単純なモデルを作ります。これが
比較の出発点（ものさし）になります。以降のどのモデルも、まずこれを超えることが最低条件です。"""),
                code("""
                    from sklearn.dummy import DummyRegressor, DummyClassifier
                    from sklearn.metrics import mean_absolute_error, accuracy_score
                    from sklearn.model_selection import train_test_split

                    train, valid = train_test_split(df, test_size=0.25, random_state=42)
                    reg = DummyRegressor(strategy="mean").fit(train[["molecular_weight"]], train["yield_pct"])
                    cls = DummyClassifier(strategy="most_frequent").fit(train[["molecular_weight"]], train["active"])
                    print("平均収率だけのMAE:", round(mean_absolute_error(valid["yield_pct"], reg.predict(valid[["molecular_weight"]])), 2))
                    print("多数派だけの正解率:", round(accuracy_score(valid["active"], cls.predict(valid[["molecular_weight"]])), 3))
                """),
                markdown("""### 出力の読み方

- **MAE（平均絶対誤差）**：予測が平均どれだけ外れるか。単位は収率と同じ%。「平均値だけ」でこの誤差、というものさしです。
- **多数派だけの正解率**が高く出ることに驚くかもしれません。活性が少ないデータでは「全部を多数派と答える」だけで正解率が高くなります。**だから正解率は当てにならない**——第8回でF1を学ぶ動機になります。
- 本命モデルは、この2つの数字を**はっきり上回って初めて価値がある**と考えます。
- なお`Dummy`は答え(`y`)だけを見て予測するため、ここで渡している`molecular_weight`列の中身は使いません（形式的な引数です）。"""),
                markdown("""## CORE深掘り：リーク候補を自動で洗い出す

「どの列がリークか」を人手で全部見るのは大変です。目的変数と**極端に強く連動する列**は、結果由来の
情報が紛れている疑いがあります。それを見つける監査を関数にしておくと、自社データでも使い回せます。"""),
                code("""
                    def leakage_audit(frame, target: str, threshold: float = 0.9):
                        "目的変数と相関が極端に高い数値列を、リーク候補として洗い出す。"
                        numeric = frame.select_dtypes(include="number")
                        corr = numeric.corrwith(frame[target]).abs().drop(labels=[target], errors="ignore")
                        report = corr.sort_values(ascending=False).to_frame("|相関|")
                        report["リーク候補"] = report["|相関|"] >= threshold
                        return report.round(3)

                    display(leakage_audit(df, target="active", threshold=0.6))
                    print("post_assay_signalは測定後の値。相関が高くても計画時には使えない。")
                """),
                markdown("""### 出力の読み方と注意

- `active`との|相関|が高い順に並びます。`post_assay_signal`が上位に来るはず——これは**活性測定後の値**なので、計画時には存在せず、使えばリークです。
- ただしこの監査は**あくまで補助**。相関が低くてもリークする列（例：実験日から結果を推測できる場合）もあります。最終判断は「その値がいつ確定するか」で人が行います。
- `threshold`はリーク候補とみなす相関の閾値。厳しく見たいなら下げます。"""),
                markdown("""## TRY：自分のテーマを1枚に整理する

次の8点を、機密を書かずに埋めます。**利用者／判断／予測時点／目的変数／使える列／使えない列／
回帰か分類か／単純な基準**。埋まらない項目があれば、それが今いちばん詰めるべき点です。

## ASK COPILOT

Copilotには、曖昧な項目を勝手に埋めさせず「確認すべき質問」の形で返すよう頼みます。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：最適な閾値は「コスト」で決まる

分類モデルは確率を出し、ある**閾値**を超えたら「活性」と判定します。既定の0.5が最適とは限りません。
最適な閾値は指標ではなく、**誤りのコスト**で決まります。ここでは「見逃し（偽陰性）＝有望条件を逃す損失」が
「偽陽性＝無駄な追試」より10倍高い状況を想定し、期待コストが最小になる閾値を探します。"""),
            code("""
                import numpy as np
                from sklearn.model_selection import train_test_split
                from sklearn.pipeline import make_pipeline
                from sklearn.impute import SimpleImputer
                from sklearn.ensemble import RandomForestClassifier

                feat = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
                X_tr, X_te, y_tr, y_te = train_test_split(df[feat], df["active"], test_size=0.3, random_state=42, stratify=df["active"])
                clf = make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=200, max_depth=5, random_state=42)).fit(X_tr, y_tr)
                proba = clf.predict_proba(X_te)[:, 1]

                cost_fn, cost_fp = 10, 1  # 見逃し=有望条件を逃す損失、偽陽性=無駄な追試
                rows = []
                for t in np.linspace(0.1, 0.9, 17):
                    pred = (proba >= t).astype(int)
                    fp = int(((pred == 1) & (y_te == 0)).sum())
                    fn = int(((pred == 0) & (y_te == 1)).sum())
                    rows.append({"閾値": round(t, 2), "偽陽性": fp, "偽陰性": fn, "期待コスト": fp * cost_fp + fn * cost_fn})
                cost_table = pd.DataFrame(rows)
                best = cost_table.loc[cost_table["期待コスト"].idxmin(), "閾値"]
                display(cost_table)
                print("コスト最小の閾値:", best, " / 見逃しが高いほど閾値は下がる")
            """),
            markdown("""### 出力の読み方

- 閾値を下げると「活性」と判定する数が増え、**偽陰性（見逃し）は減るが偽陽性は増える**トレードオフが表で見えます。
- 見逃しのコストが高いので、**最適閾値は0.5より低め**に出るはずです。「とりあえず0.5」がいかに恣意的かが分かります。
- コストの比（10:1）を変えれば最適閾値も動きます。**閾値はモデルの外側で、目的に合わせて選ぶ**ものだと理解できます。"""),
            markdown("""### まとめ：指標は意思決定から逆算する

見逃しを避けたい探索段階なら**recall**寄り、追試コストが高い絞り込み段階なら**precision**寄り。
「良いスコア」を追うのではなく、「この予測で何を決め、間違えると何を失うか」から指標と閾値を選びます。
指標や閾値を選ぶときは、常にこの「何を決め、何を失うか」に立ち返ります。"""),
        ],
        [
            markdown("""## APPENDIX（任意・追加演習）

問題設定まわりのコードをもう少し。90分の外の自習向けです。まず**単純基準（Dummy）を戦略ごとに
比較**し、「どのベースラインを土俵にするか」を意識します。"""),
            code("""
                from sklearn.dummy import DummyRegressor, DummyClassifier
                from sklearn.metrics import mean_absolute_error, accuracy_score
                from sklearn.model_selection import train_test_split

                tr, va = train_test_split(df, test_size=0.25, random_state=42)
                print("=== 回帰の単純基準 ===")
                for strat in ["mean", "median"]:
                    d = DummyRegressor(strategy=strat).fit(tr[["molecular_weight"]], tr["yield_pct"])
                    print(f"{strat:14s} MAE={mean_absolute_error(va['yield_pct'], d.predict(va[['molecular_weight']])):.2f}")
                print("=== 分類の単純基準 ===")
                for strat in ["most_frequent", "stratified", "uniform"]:
                    d = DummyClassifier(strategy=strat, random_state=42).fit(tr[["molecular_weight"]], tr["active"])
                    print(f"{strat:14s} accuracy={accuracy_score(va['active'], d.predict(va[['molecular_weight']])):.3f}")
            """),
            markdown("""### 出力の読み方

- 回帰は`mean`と`median`でMAEが少し違います。分布が歪んでいると`median`が有利なことも。
- 分類の`most_frequent`は正解率が高く見えますが、これは第8回で学ぶ「不均衡の罠」。`stratified`/`uniform`はランダムに近い基準です。
- 本命モデルは、**これらのうち最も手強い基準**を超えて初めて価値があります。"""),
            markdown("""### 予測時点チェックを関数にする

第5回本編の「使える列／使えない列」を、候補リストから自動で仕分ける関数にします。自社データでも
使い回せる、実務的な安全装置です。"""),
            code("""
                def check_feature_timing(candidate_features, available_now, target):
                    "特徴量候補を『使える/使えない(リーク)』に仕分ける。"
                    rows = []
                    for col in candidate_features:
                        if col == target:
                            verdict = "目的変数(使わない)"
                        elif col in available_now:
                            verdict = "使える"
                        else:
                            verdict = "使えない(予測時点で未確定)"
                        rows.append({"列": col, "判定": verdict})
                    return pd.DataFrame(rows)

                check_feature_timing(
                    ["temperature_c", "logp", "yield_pct", "post_assay_signal", "active"],
                    available_now=available_at_planning,
                    target="active",
                )
            """),
            markdown("""### 出力の読み方

`yield_pct`や`post_assay_signal`が「使えない(予測時点で未確定)」と仕分けられます。列名を眺めるだけでなく、
**このチェックを通してから特徴量を確定する**運用にすれば、リークの多くを機械的に防げます。"""),
            markdown("""### 期待値で「試すか否か」を決める

活性確率を予測できたとして、「その条件を追試すべきか」を**期待利益**で判断する簡単な例です。
確率×利益からコストを引いて、プラスなら試す。第5回・第8回のコスト最適閾値の考え方の土台です。"""),
            code("""
                import numpy as np

                proba = np.array([0.10, 0.40, 0.60, 0.85])   # 各条件の活性確率（仮）
                gain_if_active, cost_of_test = 100, 20
                table = pd.DataFrame({"活性確率": proba})
                table["期待利益"] = proba * gain_if_active - cost_of_test
                table["試す?"] = table["期待利益"] > 0
                table.round(1)
            """),
            markdown("""### 出力の読み方

期待利益がプラスの条件だけ「試す?=True」になります。ここでは損益分岐の確率は`cost/gain=0.2`。
つまり**活性確率20%以上なら試す**が最適で、これがそのまま判定閾値になります。「閾値0.5」が絶対でない
理由が、利益の式から自然に出てくることを確認してください。"""),
        ],
    )

    # ---- 第6回 ----
    write_notebook(
        "06-validation-leakage",
        notebook(
            "第6回：モデルは本当に当たっているか",
            "手元のスコアをどこまで信じてよいか。",
            [
                markdown("""## 「手元のスコア」を疑えるようになる回

前の回で「ベースラインより高いか」を見ました。でも、その高いスコアは**信じてよいのか**？
この回のテーマはそこです。データサイエンスで最も高くつく失敗は、計算ミスではなく
**「当たっているつもり」で外すこと**。原因はたいてい次の2つです。

- **過学習**：学習データを覚えすぎ、未知データに弱い。
- **リーク（データ漏れ）**：予測時に手に入らない情報が学習に混ざり、練習だけ高得点になる。

まず、学習と検証を分けたデータを用意します（`dropna`で欠損行を落として単純化）。"""),
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
                markdown("""## TRY：木を深くすると「過学習」が見える

決定木の深さ（`max_depth`）を段階的に深くして、**学習データでの正解率**と**検証データでの正解率**を
並べます。深くするほど学習側は上がりますが、検証側はどこかで頭打ち・悪化します。この2つの差が
「覚えすぎ」の度合いです。"""),
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
                markdown("""### 出力の読み方

- `max_depth=None`（無制限）では**学習スコアが1.0近く**まで上がるのに、**検証スコアはそれほど伸びない**——典型的な過学習です。
- 検証スコアが最も高い深さの手前あたりが「ちょうど良い複雑さ」。「学習スコアの高さ」を実力だと勘違いしないことが、ここでの分かれ目です。
- 教訓：**必ず「未知データ役（検証）」で評価する**。学習データでの高得点は実力ではありません。"""),
                markdown("""## TRY：リーク列を入れると「不自然に」良くなる

わざと`post_assay_signal`（活性測定後の値）を特徴量に混ぜてみます。予測したい`active`と強く連動する
ため、検証スコアが不自然に跳ね上がります。**練習では高得点なのに本番で使えない**典型です。"""),
                code("""
                    leak_features = [*features, "post_assay_signal"]
                    leaked = df.dropna(subset=leak_features)
                    Xl_tr, Xl_va, yl_tr, yl_va = train_test_split(leaked[leak_features], leaked["active"], test_size=0.25, random_state=42, stratify=leaked["active"])
                    leaked_model = DecisionTreeClassifier(max_depth=3, random_state=42).fit(Xl_tr, yl_tr)
                    print("リーク列ありの検証スコア:", round(accuracy_score(yl_va, leaked_model.predict(Xl_va)), 3))
                    print("post_assay_signalは測定後の値。計画時の予測には使えません。")
                """),
                markdown("""### 出力の読み方

リーク列を入れた検証スコアは、リークなしのときより**明らかに高い**はずです。**「スコアが急に良くなったら喜ぶ前に疑う」**——高すぎるスコアはリークの最初のサインです。第5回のリーク監査と合わせて習慣にします。"""),
                markdown("""## CORE深掘り：前処理も「分割の内側」で行う

見落としやすいリークが**前処理リーク**です。標準化や欠損補完を**全データで先に**行うと、検証データの
情報（平均など）が学習へこっそり混ざります。正しくは、前処理も交差検証の**各分割の内側**で学習します。
`Pipeline`に前処理を入れると、これが自動で守られます。"""),
                code("""
                    from sklearn.preprocessing import StandardScaler
                    from sklearn.pipeline import make_pipeline
                    from sklearn.impute import SimpleImputer
                    from sklearn.linear_model import LogisticRegression
                    from sklearn.model_selection import cross_val_score

                    filled = clean[features].fillna(clean[features].median())
                    scaler_all = StandardScaler().fit(filled)               # 誤り：全データで学習
                    leaked_scores = cross_val_score(LogisticRegression(max_iter=1000), scaler_all.transform(filled), clean["active"], cv=5, scoring="f1")

                    right_pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=1000))
                    right_scores = cross_val_score(right_pipe, clean[features], clean["active"], cv=5, scoring="f1")
                    print("全データ前処理(楽観的) F1平均:", round(leaked_scores.mean(), 3))
                    print("Pipeline内前処理(正しい) F1平均:", round(right_scores.mean(), 3))
                """),
                markdown("""### 出力の読み方

このデータでは差は小さいかもしれませんが、ここで確かめたいのは**やり方が正しいかどうか**そのものです。全データで前処理する方式は
原理的に楽観へ偏ります。`Pipeline`にまとめれば、分割ごとに前処理を学習し直すので安全——だから第9回で
`Pipeline`を本格的に学びます。"""),
                markdown("""## CHALLENGE：似た試料を「両側に入れない」分割

同じ化合物系列（scaffold）の似た分子が学習側と検証側の両方に入ると、検証が甘くなります（実質カンニング）。
`GroupShuffleSplit`で**系列ごとまるごと**どちらかへ振り分けると、より本番に近い評価になります。"""),
                code("""
                    splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
                    train_idx, valid_idx = next(splitter.split(clean, groups=clean["scaffold_group"]))
                    print("学習側の系列:", sorted(clean.iloc[train_idx]["scaffold_group"].unique()))
                    print("検証側の系列:", sorted(clean.iloc[valid_idx]["scaffold_group"].unique()))
                """),
                markdown("""### 出力の読み方

学習側と検証側で**系列(scaffold_group)が重ならない**ことを確認します。新規骨格への予測力を測りたいなら、
この「群を跨がせない分割」が正しい評価です。ランダム分割より点数は下がりがちですが、それが**本当の実力**です。"""),
                markdown("""## CORE深掘り：学習・検証・テストの3つに分ける

ここまでは学習用と検証用の2つでした。実務では**3つ**に分けます。**検証(valid)は設定選びに何度でも使い**、
**テスト(test)は最後の1回だけ**触ります。何度も見た検証データには無意識に合わせ込んでしまうため、
「一度も見ていないテスト」で最終性能を確かめる、という役割分担です。"""),
                code("""
                    from sklearn.model_selection import train_test_split

                    # まずテストを切り分け（最後まで触らない）、残りを学習用と検証用へ
                    work, test_set = train_test_split(clean, test_size=0.2, random_state=42, stratify=clean["active"])
                    train_set, valid_set = train_test_split(work, test_size=0.25, random_state=42, stratify=work["active"])
                    print("学習用:", len(train_set), "件（モデルを学習）")
                    print("検証用:", len(valid_set), "件（設定選び・改善判断に何度でも使う）")
                    print("テスト用:", len(test_set), "件（最後の確認まで開かない）")
                """),
                markdown("""### 出力の読み方

3つの件数が表示されます。**検証とテストの違い**はサイズではなく**使い方**です。検証は改善のたびに何度でも
見てよい／テストは最後に1回だけ。この分担を守ると、「検証データに合わせ込んで実力を過大評価する」失敗を
防げます（この回の振り返り「検証とテストの違いは何か」は、このセルを指させればOKです）。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：分割方式で「楽観度」はこんなに変わる

評価とは「将来の使われ方を模擬すること」。だから分割方式の選択が結果を左右します。同じモデルを
3つの分割方式（ふつうのKFold／層化／系列で分けるGroup）で評価し、スコアがどう変わるかを見ます。"""),
            code("""
                from sklearn.model_selection import KFold, StratifiedKFold, GroupKFold, cross_val_score
                from sklearn.pipeline import make_pipeline
                from sklearn.impute import SimpleImputer
                from sklearn.tree import DecisionTreeClassifier

                estimator = make_pipeline(SimpleImputer(strategy="median"), DecisionTreeClassifier(max_depth=4, random_state=42))
                X_all, y_all, groups = df[features], df["active"], df["scaffold_group"]
                schemes = {
                    "KFold": cross_val_score(estimator, X_all, y_all, cv=KFold(5, shuffle=True, random_state=42), scoring="f1"),
                    "StratifiedKFold": cross_val_score(estimator, X_all, y_all, cv=StratifiedKFold(5, shuffle=True, random_state=42), scoring="f1"),
                    "GroupKFold(系列)": cross_val_score(estimator, X_all, y_all, cv=GroupKFold(5), groups=groups, scoring="f1"),
                }
                pd.DataFrame({name: {"平均": s.mean(), "標準偏差": s.std(), "最低": s.min()} for name, s in schemes.items()}).T.round(3)
            """),
            markdown("""### 出力の読み方

- **GroupKFold（系列）の平均が最も低く**出るのが普通です。似た試料を跨がせないぶん厳しく、これが新規骨格への実力に近い。
- 「どの分割が正しいか」は**将来の使い方**で決まります。新しい系列に使うならGroup、同じ系列内での予測ならKFoldでも可。
- 標準偏差（ばらつき）も見て、平均だけで判断しません。"""),
            markdown("""### ネストCV：設定選びと性能報告を分ける

`max_depth`などの設定を「検証スコアが最高になるよう」選び、その同じ検証スコアを性能として報告すると、
**出来すぎの数字**になります。これを防ぐのがネストCV：**内側のCVで設定を選び、外側のCVで評価**します。"""),
            code("""
                from sklearn.model_selection import RandomizedSearchCV
                from sklearn.ensemble import RandomForestClassifier

                pipe = make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(random_state=42))
                param_dist = {
                    "randomforestclassifier__n_estimators": [100, 200, 300],
                    "randomforestclassifier__max_depth": [3, 4, 6, None],
                    "randomforestclassifier__min_samples_leaf": [1, 2, 4],
                }
                inner = StratifiedKFold(3, shuffle=True, random_state=1)
                outer = StratifiedKFold(5, shuffle=True, random_state=2)
                search = RandomizedSearchCV(pipe, param_dist, n_iter=8, cv=inner, scoring="f1", random_state=42)
                nested = cross_val_score(search, df[features], df["active"], cv=outer, scoring="f1")
                print("ネストCVの外側F1:", nested.round(3))
                print("楽観の少ない推定 平均±SD:", round(nested.mean(), 3), "±", round(nested.std(), 3))
            """),
            markdown("""### 出力の読み方

外側5分割それぞれで「内側で設定を選び直し→未見の外側で評価」しています。ここで出る平均が、
**設定選びの下駄を履いていない、より正直な性能**です。単純なグリッド探索の最高スコアより低めに
出るのが健全で、その差が「探索による楽観」の大きさです。"""),
            markdown("""### adversarial validation：学習とテストは似ているか

もう1つの落とし穴が**分布ずれ**（学習データとテストデータの傾向が違う）です。「その行が学習か
テストか」を当てる分類器を作り、そのAUC（当てやすさ）で分布の近さを測ります。"""),
            code("""
                train_c = pd.read_csv(DATA / "local_competition" / "train.csv")
                test_c = pd.read_csv(DATA / "local_competition" / "test.csv")
                adv_features = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
                combined = pd.concat([
                    train_c[adv_features].assign(is_test=0),
                    test_c[adv_features].assign(is_test=1),
                ], ignore_index=True)
                adv_model = make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=200, random_state=42))
                auc = cross_val_score(adv_model, combined[adv_features], combined["is_test"], cv=5, scoring="roc_auc")
                print("adversarial validation AUC:", round(auc.mean(), 3))
                print("0.5付近なら分布は近い。0.8以上なら分布ずれを疑う。")
            """),
            markdown("""### 出力の読み方

- **AUC≈0.5**：学習とテストが見分けられない＝分布が近い。手元のCVは信頼できます。
- **AUC≫0.5（0.8以上など）**：見分けがつく＝分布がずれており、手元のCVは本番を過大評価しがち。
- このデータは同じ生成過程なのでAUCは0.5付近のはず。実データでこの値が高ければ、時系列や機器差など「ずれの原因」を探します。"""),
        ],
        [
            markdown("""## APPENDIX（任意・追加演習）

交差検証の中身を、あえて手作りして仕組みを体で理解します。90分の外の自習向けです。
`cross_val_score`が内部でやっていることを、`for`ループで書き下します。"""),
            code("""
                import numpy as np
                from sklearn.tree import DecisionTreeClassifier
                from sklearn.metrics import f1_score

                data = df.dropna(subset=features).reset_index(drop=True)
                Xa, ya = data[features], data["active"]
                k = 5
                fold_id = np.arange(len(Xa)) % k          # 位置でfoldを割り当てる（デモ用）
                scores = []
                for f in range(k):
                    is_valid = fold_id == f
                    m = DecisionTreeClassifier(max_depth=4, random_state=42).fit(Xa[~is_valid], ya[~is_valid])
                    scores.append(f1_score(ya[is_valid], m.predict(Xa[is_valid])))
                print("手作りk-fold F1:", [round(s, 3) for s in scores])
                print("平均:", round(np.mean(scores), 3))
            """),
            markdown("""### 出力の読み方

「4つのfoldで学習→残り1つで検証」を5回繰り返し、平均しています。これが`cross_val_score`の正体です。
中身が分かると、**分割の乱数や層化（stratify）を変えると平均が動く**ことも納得できます。"""),
            markdown("""### 時系列分割：未来で過去を検証しない

`experiment_date`で並べ、`TimeSeriesSplit`で「過去で学習→未来で検証」を繰り返します。実運用が
「過去データで学習し、これから来る試料を予測する」形なら、この分割が最も現実に近い評価です。"""),
            code("""
                from sklearn.model_selection import TimeSeriesSplit, cross_val_score
                from sklearn.pipeline import make_pipeline
                from sklearn.impute import SimpleImputer

                time_sorted = df.sort_values("experiment_date")
                est = make_pipeline(SimpleImputer(strategy="median"), DecisionTreeClassifier(max_depth=4, random_state=42))
                tscv = TimeSeriesSplit(n_splits=5)
                ts_scores = cross_val_score(est, time_sorted[features], time_sorted["active"], cv=tscv, scoring="f1")
                print("時系列分割F1:", ts_scores.round(3), " 平均:", round(ts_scores.mean(), 3))
            """),
            markdown("""### 出力の読み方

各foldは「それまでの期間」で学習し「直後の期間」で検証します。前半のfoldは学習データが少なく不安定に
なりがち。時間で性能が変わるなら、ランダム分割より厳しい（現実的な）数字が出ます。"""),
            markdown("""### shuffleの有無で結果は変わる

`KFold`の`shuffle`を切り替えて比較します。データが何らかの順序（日付・バッチ順など）で並んでいると、
`shuffle=False`は偏った分割になり、スコアが不安定・楽観/悲観に振れることがあります。"""),
            code("""
                from sklearn.model_selection import KFold

                for shuffle in [False, True]:
                    kf = KFold(5, shuffle=shuffle, random_state=42 if shuffle else None)
                    s = cross_val_score(est, df[features], df["active"], cv=kf, scoring="f1")
                    print(f"shuffle={str(shuffle):5s}: {s.round(3)}  平均={s.mean():.3f}")
            """),
            markdown("""### 出力の読み方

2つの平均やばらつきが違えば、**データの並び順が結果に影響している**証拠。ふつうは`shuffle=True`が無難ですが、
時系列データでは`shuffle`してはいけません（未来が学習に混ざる）。「どう並んでいるか」を意識して分割を選びます。"""),
        ],
    )

    # ---- 第7回 ----
    write_notebook(
        "07-regression",
        notebook(
            "第7回：数値を予測する—回帰",
            "連続値の予測モデルを、何と比べ、不確かさをどう示すか。",
            [
                markdown("""## 回帰＝「数値そのもの」を予測する

ここまでは活性の有無（0/1）でしたが、この回は**収率（%）という連続値**を予測します。これを
**回帰**と呼びます。回帰でいちばん大事な問いは「その予測は**何と比べて**良いのか」。だから今回も
**平均値だけを返すベースライン**を必ず土俵に上げます。

まず下準備。日本語フォント設定と、使うモデルの読み込み、学習/検証の分割をまとめて行います。"""),
                common_load_cell(),
                font_cell("""
                    from sklearn.model_selection import train_test_split
                    from sklearn.impute import SimpleImputer
                    from sklearn.pipeline import make_pipeline
                    from sklearn.dummy import DummyRegressor
                    from sklearn.linear_model import LinearRegression
                    from sklearn.tree import DecisionTreeRegressor
                    from sklearn.ensemble import RandomForestRegressor

                    features = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
                    X_train, X_valid, y_train, y_valid = train_test_split(df[features], df["yield_pct"], test_size=0.25, random_state=42)
                """),
                markdown("""## TRY：4モデルを交差検証で、3つの指標で比べる

回帰の代表的な指標を先に押さえます。

- **MAE（平均絶対誤差）**：平均で何%外すか。単位が収率と同じで**いちばん直感的**。
- **RMSE**：大きな外れを二乗で重く見る。「たまの大外し」を嫌う場面向け。
- **R²（決定係数）**：平均値予測と比べてどれだけ説明できたか（1に近いほど良い、0は平均値並み）。

`neg_...`はsklearnの都合で「大きいほど良い」に符号反転された指標名。表示時に`-`で元へ戻します。
（scikit-learnの`scoring`は「大きいほど良い」に統一されているため、誤差系の指標は符号が反転しています。）

コード中の`make_pipeline(SimpleImputer(...), モデル)`は、**欠損補完とモデルを1つにまとめて「1個のモデル」の
ように扱う**ための道具です。こうすると`fit`/`predict`や交差検証がまとめて安全に回せます。仕組みは第9回で
詳しく学ぶので、ここでは「前処理とモデルをセットにする書き方」とだけ捉えて大丈夫です。"""),
                code("""
                    from sklearn.model_selection import cross_validate, KFold

                    models = {
                        "平均値": DummyRegressor(),
                        "線形回帰": make_pipeline(SimpleImputer(strategy="median"), LinearRegression()),
                        "決定木": make_pipeline(SimpleImputer(strategy="median"), DecisionTreeRegressor(max_depth=4, random_state=42)),
                        "Random Forest": make_pipeline(SimpleImputer(strategy="median"), RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42)),
                    }
                    cv = KFold(5, shuffle=True, random_state=42)
                    scoring = {"MAE": "neg_mean_absolute_error", "RMSE": "neg_root_mean_squared_error", "R2": "r2"}
                    rows = []
                    for name, estimator in models.items():
                        res = cross_validate(estimator, df[features], df["yield_pct"], cv=cv, scoring=scoring)
                        rows.append({"モデル": name, "MAE": -res["test_MAE"].mean(), "RMSE": -res["test_RMSE"].mean(), "R2": res["test_R2"].mean()})
                    pd.DataFrame(rows).sort_values("MAE").round(3)
                """),
                markdown("""### 出力の読み方

- MAEの小さい順に並びます。**「平均値」より各モデルがどれだけMAEを下げたか**が価値です。下げ幅が小さいなら、その特徴量では収率を説明しきれていません。
- MAEとRMSEの差が大きいモデルは、**たまに大きく外している**サイン（RMSEが大外れを強調するため）。
- R²が0近くなら「平均値と大差ない」、負なら「平均値より悪い」。**まずベースライン超え**を確認します。
- なお、この`cross_validate`は内部でデータを分割し直して評価します。上のセルで作った`X_train`/`X_valid`はここでは使わず、この後の**残差図**（予測と実測を見る図）で使います。"""),
                markdown("""## 予測と実測、そして「残差」を絵で見る

数字だけでなく図で確かめます。左は**予測と実測の散布図**（点が対角線に乗るほど良い）、右は
**残差図**（実測−予測を予測値に対してプロット）。残差は0の周りに**模様なくばらける**のが理想です。
偏りや傾きがあれば、モデルが取りこぼした構造があります。"""),
                code("""
                    rf = make_pipeline(SimpleImputer(strategy="median"), RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42)).fit(X_train, y_train)
                    pred = rf.predict(X_valid)
                    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
                    axes[0].scatter(y_valid, pred, alpha=0.6)
                    axes[0].plot([y_valid.min(), y_valid.max()], [y_valid.min(), y_valid.max()], "--")
                    axes[0].set(xlabel="実測収率", ylabel="予測収率", title="予測と実測")
                    axes[1].scatter(pred, y_valid - pred, alpha=0.6)
                    axes[1].axhline(0, linestyle="--")
                    axes[1].set(xlabel="予測収率", ylabel="残差（実測-予測）", title="残差")
                    plt.tight_layout()
                """),
                markdown("""### 出力の読み方

- **左**：点が破線（予測＝実測）に近いほど良い。高収率の領域で点が下に外れていれば、**高い収率を低めに予測しがち**という癖です。
- **右**：残差が予測値によって偏る（例：予測が大きいほど残差が下がる）なら、モデルが端の領域を苦手にしています。**きれいな水平の帯**が理想。
- 図は「どこで外すか」を教えてくれます。次のセルで、実際に大きく外した試料を取り出します。"""),
                markdown("""## 大きく外した試料を名指しで調べる

平均のMAEでは見えない「個別の大外し」を確認します。絶対誤差の大きい上位8件を、系列や触媒つきで
取り出すと、**特定の条件で外していないか**の手がかりになります。"""),
                code("""
                    errors = df.loc[y_valid.index, ["sample_id", "scaffold_group", "catalyst", "yield_pct"]].copy()
                    errors["予測"] = pred
                    errors["絶対誤差"] = (errors["yield_pct"] - errors["予測"]).abs()
                    errors.nlargest(8, "絶対誤差").round(2)
                """),
                markdown("""### 出力の読み方

大外し8件に**同じ系列や同じ触媒が偏っていないか**を見ます。偏っていれば、その条件を表す特徴量が
足りない可能性（第11回の特徴量設計の動機）。ばらばらなら、単なるノイズかもしれません。

## CHANGE

`max_depth=6`を`3`や`10`へ変え、MAEの表・残差図・大外し試料が**どう連動して動くか**を観察します。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：伸び悩みの原因と、予測の不確かさ

発展として3つ。**学習曲線**（データを増やせば改善するか）、**群別残差**（どの系列で系統的に外すか）、
**予測区間**（1点の予測に幅を添える）です。"""),
            markdown("""### 学習曲線：データ不足か、表現力不足か

「もっとデータを集めれば精度が上がる？」に答える図です。学習データ量を増やしながら、学習MAEと
検証MAEの推移を描きます。2本が近づいて高止まりなら**データ追加は効きにくい**（特徴量やモデルを
見直すべき）。2本が離れて検証MAEがまだ下がりそうなら**データ追加が効く**サインです。"""),
            code("""
                import numpy as np
                from sklearn.model_selection import learning_curve

                sizes, train_scores, valid_scores = learning_curve(
                    make_pipeline(SimpleImputer(strategy="median"), RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42)),
                    df[features], df["yield_pct"], cv=5, scoring="neg_mean_absolute_error",
                    train_sizes=np.linspace(0.2, 1.0, 5),
                )
                plt.figure(figsize=(7, 4))
                plt.plot(sizes, -train_scores.mean(1), "o-", label="学習MAE")
                plt.plot(sizes, -valid_scores.mean(1), "o-", label="検証MAE")
                plt.xlabel("学習データ件数"); plt.ylabel("MAE"); plt.legend(); plt.title("学習曲線")
                plt.tight_layout()
                print("2本が高止まりで近いなら、データ追加より特徴量やモデルを見直す。")
            """),
            markdown("""### 出力の読み方

- 右端（全データ使用）で**検証MAEがまだ下降中**なら、データを増やす価値あり。**水平に寝ている**なら頭打ち。
- 学習MAEと検証MAEの**縦の隙間**が過学習の程度。隙間が大きいほど「覚えすぎ」寄りです。"""),
            markdown("""### 群別に残差を見る：どの系列で偏るか

全体のMAEが良くても、特定の化合物系列だけ系統的に外していることがあります。系列ごとに件数・MAE・
**平均残差**（符号つき）を出すと、「この系列を平均的に低く見積もっている」といった偏りが見えます。"""),
            code("""
                errors["残差"] = errors["yield_pct"] - errors["予測"]
                group_error = errors.groupby("scaffold_group").agg(件数=("残差", "size"), MAE=("絶対誤差", "mean"), 平均残差=("残差", "mean"))
                display(group_error.sort_values("MAE", ascending=False).round(2))
                print("平均残差が正なら、その系列を平均的に過小予測している。")
            """),
            markdown("""### 出力の読み方

**平均残差が0から大きく離れた系列**が要注意。正なら過小予測、負なら過大予測です。件数が少ない系列は
偶然も大きいので、件数と併せて読みます。系統的な偏りは、その系列を表す特徴量の不足を示唆します。"""),
            markdown("""### 予測区間：1点でなく「幅」で答える

「収率は62%」より「10〜90%の確率で50〜74%」の方が、意思決定に誠実なことがあります。**分位点回帰**で
下限（10%点）と上限（90%点）を別々に予測し、実測が本当にその区間に入る割合（**被覆率**）を検証します。"""),
            code("""
                from sklearn.ensemble import HistGradientBoostingRegressor

                low = HistGradientBoostingRegressor(loss="quantile", quantile=0.1, max_iter=200, random_state=42).fit(X_train, y_train)
                high = HistGradientBoostingRegressor(loss="quantile", quantile=0.9, max_iter=200, random_state=42).fit(X_train, y_train)
                low_pred, high_pred = low.predict(X_valid), high.predict(X_valid)
                coverage = ((y_valid.to_numpy() >= low_pred) & (y_valid.to_numpy() <= high_pred)).mean()
                print(f"10-90%予測区間の実測被覆率: {coverage:.1%}（理想は約80%）")
                pd.DataFrame({"実測": y_valid.to_numpy()[:8], "下限": low_pred[:8].round(1), "上限": high_pred[:8].round(1)})
            """),
            markdown("""### 出力の読み方

- 10〜90%区間なので、被覆率は**理想80%**に近いほど区間が正直。大きく下回れば区間が狭すぎ（自信過剰）、上回れば広すぎです。
- 表の8件で、**実測が下限〜上限に収まっているか**を目で確認します。幅の広い試料はモデルが自信を持てていない試料です。"""),
        ],
        [
            markdown("""## APPENDIX（任意・追加演習）

線形モデルの正則化や非線形化を試します。90分の外の自習向けです。まず**RidgeとLasso**を、正則化の
強さ`alpha`を変えて比較します（`alpha`が大きいほど係数を抑え、過学習を防ぐ）。"""),
            code("""
                import numpy as np
                from sklearn.linear_model import Ridge, Lasso
                from sklearn.preprocessing import StandardScaler
                from sklearn.model_selection import cross_val_score, KFold

                cv = KFold(5, shuffle=True, random_state=42)
                rows = []
                for alpha in [0.01, 0.1, 1.0, 10.0]:
                    for name, reg in {"Ridge": Ridge(alpha=alpha), "Lasso": Lasso(alpha=alpha, max_iter=5000)}.items():
                        pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), reg)
                        mae = -cross_val_score(pipe, df[features], df["yield_pct"], cv=cv, scoring="neg_mean_absolute_error").mean()
                        rows.append({"モデル": name, "alpha": alpha, "MAE": mae})
                pd.DataFrame(rows).pivot(index="alpha", columns="モデル", values="MAE").round(3)
            """),
            markdown("""### 出力の読み方

`alpha`を変えるとMAEが変わり、最適な強さがあることが分かります。強すぎると単純になりすぎ（未学習）、
弱すぎると過学習寄り。RidgeとLassoで最適`alpha`が違うのも普通です。**正則化は複雑さを調整するダイヤル**です。"""),
            markdown("""### 多項式特徴量で「曲がり」を線形モデルに教える

線形回帰は直線しか引けませんが、`PolynomialFeatures`で二乗や交互作用の列を足すと、曲がった関係も
表せます。次数を上げすぎると過学習するので、交差検証で確かめます。"""),
            code("""
                from sklearn.preprocessing import PolynomialFeatures
                from sklearn.linear_model import LinearRegression

                for degree in [1, 2, 3]:
                    pipe = make_pipeline(
                        SimpleImputer(strategy="median"), StandardScaler(),
                        PolynomialFeatures(degree, include_bias=False), LinearRegression(),
                    )
                    mae = -cross_val_score(pipe, df[features], df["yield_pct"], cv=cv, scoring="neg_mean_absolute_error").mean()
                    print(f"多項式次数{degree}: MAE={mae:.3f}")
            """),
            markdown("""### 出力の読み方

次数2で、温度の山型（第4回）を線形モデルが表せるようになり、MAEが下がることが多いはず。ただし次数3で
悪化したら過学習のサイン。「複雑にすれば良い」ではなく、**交差検証が下がる範囲でだけ複雑にする**が原則です。"""),
            markdown("""### 部分依存プロット：モデルは各変数をどう使っているか

`PartialDependenceDisplay`は、「他を平均的に保ったまま、ある変数を動かすと予測がどう変わるか」を
描きます。モデルが温度の山型を学べているかを、目で確認できます。"""),
            code("""
                from sklearn.inspection import PartialDependenceDisplay

                rf = make_pipeline(SimpleImputer(strategy="median"), RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42)).fit(df[features], df["yield_pct"])
                PartialDependenceDisplay.from_estimator(rf, df[features], ["temperature_c", "concentration_m"])
                plt.tight_layout()
            """),
            markdown("""### 出力の読み方

温度の曲線が**山型**（中ほどで予測収率が最大）になっていれば、モデルは第4回で見た構造を学べています。
部分依存プロットは、ブラックボックスに見える木モデルの「考え方」を説明する強力な道具で、
研究者への説明資料としても有効です。"""),
        ],
    )

    # ---- 第8回 ----
    write_notebook(
        "08-classification",
        notebook(
            "第8回：クラスを予測する—分類",
            "正解率だけで十分なのはどんなときか。",
            [
                markdown("""## 「正解率」だけ見ると、なぜ危ないのか

第5回で「多数派と答えるだけで正解率が高くなる」ことを見ました。この回はその続きで、
**正解率（accuracy）に代わる読み方**を身につけます。鍵になるのが4つの結果です。

- **真陽性(TP)**：活性を活性と当てた／**真陰性(TN)**：非活性を非活性と当てた
- **偽陽性(FP)**：非活性を活性と誤った（無駄な追試）／**偽陰性(FN)**：活性を見逃した（機会損失）

この4つを表にしたのが**混同行列**です。まずロジスティック回帰を学習し、各試料の**活性確率**を出します。"""),
                common_load_cell(),
                font_cell("""
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
                markdown("""## TRY：閾値0.5で混同行列と3指標を読む

確率が0.5以上なら「活性」と判定し、結果を混同行列で見ます。同時に3つの指標を出します。

- **precision（適合率）**：活性と判定したうち、本当に活性だった割合（＝空振りの少なさ）。
- **recall（再現率）**：本当の活性のうち、見つけられた割合（＝見逃しの少なさ）。
- **F1**：precisionとrecallのバランス（両方が高いときだけ高くなる）。"""),
                code("""
                    prediction = (probability >= 0.5).astype(int)
                    print("accuracy:", round(accuracy_score(y_valid, prediction), 3))
                    print("precision:", round(precision_score(y_valid, prediction), 3))
                    print("recall:", round(recall_score(y_valid, prediction), 3))
                    print("F1:", round(f1_score(y_valid, prediction), 3))
                    ConfusionMatrixDisplay.from_predictions(y_valid, prediction, display_labels=["非活性", "活性"], cmap="Blues")
                    plt.title("混同行列")
                """),
                markdown("""### 出力の読み方

- 混同行列は**左上=TN、右下=TP**が当たり、**右上=FP、左下=FN**が外れ。色が濃い（数が多い）マスに注目します。
- **accuracyは高いのにrecallが低い**、という組み合わせが起きがちです。これは「非活性はよく当てるが、肝心の活性を見逃している」状態。活性が少ないデータでは、accuracyが良く見えてもこの罠にはまります。
- 「何を重視するか」で読む指標が変わる、というのが今回いちばん覚えておいてほしい点です。"""),
                markdown("""## TRY：判定の「閾値」を動かしてみる

0.5は絶対ではありません。閾値を下げると「活性」と判定する数が増え、**recallは上がるがprecisionは下がる**、
というトレードオフが起きます。0.3・0.5・0.7で指標がどう動くか並べます。"""),
                code("""
                    rows = []
                    for threshold in [0.3, 0.5, 0.7]:
                        pred = (probability >= threshold).astype(int)
                        rows.append({"閾値": threshold, "precision": precision_score(y_valid, pred), "recall": recall_score(y_valid, pred), "F1": f1_score(y_valid, pred)})
                    pd.DataFrame(rows).round(3)
                """),
                markdown("""### 出力の読み方

- 閾値を下げる（0.3）と**recallが上がりprecisionが下がる**、上げる（0.7）と逆。表で必ずこの向きになるはずです。
- **見逃しを避けたい場面は閾値を下げ、空振りを避けたい場面は上げる**。閾値はモデルの外側で、目的に合わせて選ぶダイヤルです（第5回のコスト最適閾値につながります）。"""),
                markdown("""## CORE深掘り：不均衡データではPR-AUCを見る

「閾値をいくつにするか」を決める前に、モデルの**確率の質そのもの**を1つの数字で測りたい。不均衡データ
（活性が少ない）では、ROC-AUCよりも**PR-AUC（適合率-再現率曲線の面積）**の方が実態を映します。"""),
                code("""
                    from sklearn.metrics import average_precision_score
                    print("活性の割合:", round(df["active"].mean(), 3))
                    print("PR-AUC(平均適合率):", round(average_precision_score(y_valid, probability), 3))
                    print("常に多数派と予測したときのaccuracy:", round((y_valid == y_valid.mode()[0]).mean(), 3))
                """),
                markdown("""### 出力の読み方

- 「活性の割合」が小さいのに「多数派予測のaccuracy」が高い——**accuracyの水増し**を数字で確認できます。
- **PR-AUC**は「活性の割合」を基準線とし、それを大きく上回るほど、モデルが活性をうまく上位に並べていると読めます。閾値を決めずにモデルの良さを比べたいときの主指標です。"""),
                markdown("""## 話し合い

「見逃し（FN）と空振り（FP）の、どちらがこのテーマでは高くつくか？」を5人で言葉にします。
探索段階なら見逃しを嫌ってrecall寄り、確証段階なら空振りを嫌ってprecision寄り。**正解は場面で変わります。**"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：確率を「信じてよいか」と、不均衡対策

確率をコストの計算（第5回）に使うなら、その確率が**較正**されている——「0.8と言ったら本当に約80%」で
ある必要があります。ここでは較正の測り方と直し方、そして少数クラスへの対処を扱います。"""),
            markdown("""### 較正：予測確率と実際の頻度は一致しているか

**信頼度図**は、予測確率（横軸）に対して実際の活性率（縦軸）を描き、対角線に近いほど較正が良い、と
読みます。**Brierスコア**は較正のズレを1つの数字にしたもの（小さいほど良い）。`CalibratedClassifierCV`で
較正し直し、前後を比べます。"""),
            code("""
                from sklearn.calibration import CalibratedClassifierCV, calibration_curve
                from sklearn.metrics import brier_score_loss

                base_clf = make_pipeline(SimpleImputer(strategy="median"), LogisticRegression(max_iter=1000)).fit(X_train, y_train)
                cal_clf = CalibratedClassifierCV(base_clf, method="isotonic", cv=5).fit(X_train, y_train)
                plt.figure(figsize=(6, 5))
                for name, clf in {"未較正": base_clf, "較正後": cal_clf}.items():
                    p = clf.predict_proba(X_valid)[:, 1]
                    print(f"{name}: Brier={brier_score_loss(y_valid, p):.3f}（小さいほど良い）")
                    frac, mean_pred = calibration_curve(y_valid, p, n_bins=5)
                    plt.plot(mean_pred, frac, "o-", label=name)
                plt.plot([0, 1], [0, 1], "--", color="gray")
                plt.xlabel("予測確率"); plt.ylabel("実際の頻度"); plt.legend(); plt.title("信頼度図")
                plt.tight_layout()
            """),
            markdown("""### 出力の読み方

- 折れ線が**対角線（点線）に近い**ほど較正が良好。対角線から膨らんでいれば、その確率帯で自信過剰／過小です。
- Brierが較正後に下がっていれば改善成功。ただし小さいデータでは較正が不安定なこともあるので、図と数字の両方で判断します。
- なお`base_clf`は「未較正」の比較用に学習しています。`CalibratedClassifierCV`は`cv=5`を指定しているため内部でモデルを学習し直します（`base_clf`の学習結果そのものは較正には使いません）。"""),
            markdown("""### コスト行列で閾値を決める（較正済み確率で）

第5回と同じ考え方を、較正した確率に適用します。見逃し(FN)が空振り(FP)の8倍高いとして、期待コストが
最小の閾値を探します。**較正済みの確率**を使うことで、コスト計算の前提が整います。"""),
            code("""
                import numpy as np
                proba_cal = cal_clf.predict_proba(X_valid)[:, 1]
                cost_fn, cost_fp = 8, 1
                rows = []
                for t in np.linspace(0.1, 0.9, 17):
                    pred = (proba_cal >= t).astype(int)
                    fp = int(((pred == 1) & (y_valid == 0)).sum())
                    fn = int(((pred == 0) & (y_valid == 1)).sum())
                    rows.append({"閾値": round(t, 2), "偽陽性": fp, "偽陰性": fn, "期待コスト": fp * cost_fp + fn * cost_fn})
                table = pd.DataFrame(rows)
                print("コスト最小の閾値:", table.loc[table["期待コスト"].idxmin(), "閾値"])
                table
            """),
            markdown("""### 出力の読み方

見逃しのコストが高いので、最適閾値は**0.5より低め**に出ます。「0.5で判定」がいかに恣意的かを、
ここでも数字で確認できます。コスト比を変えれば最適点も動きます。"""),
            markdown("""### class_weight：少数クラスの誤りを重く扱う

閾値調整とは別に、**学習の時点で**少数クラス（活性）の誤りを重く扱う方法があります。`class_weight="balanced"`は
少数クラスを自動で重み付けします。recall（見逃しの少なさ）がどう変わるかを見ます。"""),
            code("""
                for label, weight in {"weightなし": None, "balanced": "balanced"}.items():
                    clf = make_pipeline(SimpleImputer(strategy="median"), LogisticRegression(max_iter=1000, class_weight=weight)).fit(X_train, y_train)
                    pred = clf.predict(X_valid)
                    print(f"{label:10s} F1={f1_score(y_valid, pred):.3f}  recall={recall_score(y_valid, pred):.3f}")
            """),
            markdown("""### 出力の読み方

`balanced`にすると**recallが上がりやすい**（活性を見つけにいく）反面、precisionやF1は下がることもあります。
「閾値で調整」と「重みで調整」は似た効果を持つ別の道具。どちらが目的に合うかを、指標を見て選びます。"""),
        ],
        [
            markdown("""## APPENDIX（任意・追加演習）

分類の評価を、曲線と閾値でさらに掘り下げます。90分の外の自習向けです。まず2モデルの
**適合率-再現率曲線**と**ROC曲線**を並べます。"""),
            code("""
                from sklearn.linear_model import LogisticRegression
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay

                candidates = {
                    "ロジスティック": make_pipeline(SimpleImputer(strategy="median"), LogisticRegression(max_iter=1000)),
                    "Random Forest": make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=200, max_depth=5, random_state=42)),
                }
                fig, axes = plt.subplots(1, 2, figsize=(12, 4))
                for name, est in candidates.items():
                    est.fit(X_train, y_train)
                    PrecisionRecallDisplay.from_estimator(est, X_valid, y_valid, ax=axes[0], name=name)
                    RocCurveDisplay.from_estimator(est, X_valid, y_valid, ax=axes[1], name=name)
                axes[0].set_title("適合率-再現率曲線"); axes[1].set_title("ROC曲線")
                axes[1].plot([0, 1], [0, 1], "--", color="gray")
                plt.tight_layout()
            """),
            markdown("""### 出力の読み方

- **PR曲線**は右上に張り付くほど良い。不均衡データでは、この曲線とその面積(PR-AUC)がROCより実態を映します。
- **ROC曲線**は左上に張り付くほど良い。凡例のAUCで一目比較できます。
- 2モデルの曲線が交差するなら、**どの動作点（閾値）で使うかによって優劣が変わる**ということです。"""),
            markdown("""### 目標recallを満たす閾値を逆算する

「活性の見逃しは9割以上防ぎたい（recall≧0.9）」のような要件から、それを満たしつつprecisionが最大の
閾値を選びます。要件を先に決め、閾値を後から合わせる実務的なやり方です。"""),
            code("""
                import numpy as np
                from sklearn.metrics import precision_recall_curve

                proba = candidates["Random Forest"].predict_proba(X_valid)[:, 1]
                prec, rec, thr = precision_recall_curve(y_valid, proba)
                target_recall = 0.9
                ok = rec[:-1] >= target_recall
                if ok.any():
                    idx = np.argmax(np.where(ok, prec[:-1], -1))
                    print(f"recall>={target_recall} を満たす閾値: {thr[idx]:.3f}  precision={prec[idx]:.3f}  recall={rec[idx]:.3f}")
                else:
                    print("目標recallを満たす点がありません")
            """),
            markdown("""### 出力の読み方

選ばれた閾値は0.5より低いはず（見逃しを減らすには「活性」と判定する範囲を広げる）。その代償に
precisionが下がります。**要件→閾値**の順で決めると、恣意的な0.5から卒業できます。"""),
            markdown("""### 交差検証で混同行列を集計する

1回の検証ではなく、`cross_val_predict`で全データのOOF予測を作り、混同行列を集計します。1回分より
安定した内訳が見えます。"""),
            code("""
                from sklearn.model_selection import cross_val_predict, StratifiedKFold
                from sklearn.metrics import confusion_matrix

                oof = cross_val_predict(
                    make_pipeline(SimpleImputer(strategy="median"), LogisticRegression(max_iter=1000)),
                    df[features], df["active"], cv=StratifiedKFold(5, shuffle=True, random_state=42),
                )
                cm = confusion_matrix(df["active"], oof)
                display(pd.DataFrame(cm, index=["実:非活性", "実:活性"], columns=["予:非活性", "予:活性"]))
            """),
            markdown("""### 出力の読み方

全420件を1件ずつ「その行を学習に使わないモデル」で予測した集計です。右上（偽陽性）と左下（偽陰性）の
大きさを比べ、**このモデルがどちらの誤りをしやすいか**を把握します。改善の方向づけに使えます。"""),
        ],
    )

    # ---- 第9回 ----
    write_notebook(
        "09-preprocessing-pipeline",
        notebook(
            "第9回：前処理をPipelineにまとめる",
            "数値列とカテゴリ列を、安全に同じモデルへ入れるにはどうするか。",
            [
                markdown("""## なぜ「Pipeline」が必要なのか

これまで欠損を`fillna`で埋めたり、数値だけを使ったりしてきました。実データでは**数値列と
カテゴリ列（文字）が混在**し、それぞれ別の下ごしらえが要ります。

- 数値列 → 欠損を埋める＋尺度を揃える（標準化）
- カテゴリ列 → 欠損を埋める＋数値へ変換（One-Hot：各カテゴリを0/1の列にする）

これらを手作業でやると、**第6回で学んだ前処理リーク**（検証情報の漏れ）を起こしがちです。そこで
`Pipeline`と`ColumnTransformer`を使い、**前処理からモデルまでを1つの部品**にまとめます。こうすると
交差検証や予測のたびに、前処理が正しく分割の内側で学習されます。

まず数値列・カテゴリ列を決め、学習/検証に分けます。"""),
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
                markdown("""## TRY：列ごとの前処理を組み立てて、モデルまで繋ぐ

各部品の役割：

- `numeric_process`：数値列の下ごしらえ（欠損補完→標準化）を並べた小さなPipeline。
- `categorical_process`：カテゴリ列の下ごしらえ（欠損補完→One-Hot）。
- `ColumnTransformer`：「この列たちには数値処理、あの列たちにはカテゴリ処理」と**列ごとに担当を割り当てる**部品。
- 最後に`Pipeline([("前処理", preprocess), ("予測", ロジスティック回帰)])`で**前処理＋モデルを一体化**。

`model.fit`一発で、前処理もモデルもまとめて学習されます。"""),
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
                    model = Pipeline([("前処理", preprocess), ("予測", LogisticRegression(max_iter=1000))])
                    model.fit(X_train, y_train)
                    print(classification_report(y_valid, model.predict(X_valid), target_names=["非活性", "活性"]))
                """),
                markdown("""### 出力の読み方

`classification_report`は、クラスごとにprecision・recall・F1と件数(support)を並べた総合成績表です。

- **活性クラスの行**を重点的に見ます（少数派で難しいため）。第8回で学んだとおり、accuracyより各クラスのrecall/precisionが実態を映します。
- 大事なのは点数そのものより、**文字列カテゴリを含む表をエラーなく1つのモデルへ通せた**こと。手作業のOne-Hotより安全で短いです。

補足：ここでは`scaffold_group`（化合物系列）もカテゴリ列の例として入れていますが、第6回のとおり本来は
**系列を跨がない分割（GroupKFold）とセットで扱うべき列**です。この回はPipelineの組み方の説明が目的なので
乱数分割のまま使っていますが、実データで系列をカテゴリ特徴量にするときは、この点に注意してください。"""),
                markdown("""## 未知カテゴリが来ても止まらない

本番では、学習時に無かった溶媒名が来ることがあります。`OneHotEncoder(handle_unknown="ignore")`の
おかげで、未知カテゴリでもエラーにならず予測できます。わざと存在しない溶媒名を入れて確かめます。"""),
                code("""
                    unknown = X_valid.iloc[[0]].copy()
                    unknown["solvent"] = "New-Solvent"
                    print("未知カテゴリを含む予測:", model.predict(unknown)[0])
                """),
                markdown("""### 出力の読み方

エラーで止まらず予測が返れば成功です。`handle_unknown="ignore"`が無いと、未知カテゴリで例外が出て
本番が止まります。ここで身につけてほしいのは、**「本番で起きうる入力」を想定して前処理を設計する**という実務感覚です。"""),
                markdown("""## CORE深掘り：変換後は列が増える。その姿を見る

One-Hotはカテゴリごとに0/1の列を作るので、**列数が増えます**。`get_feature_names_out`で変換後の列名を、
`transform`で実際の数値を確認し、Pipelineの中で何が起きているかを可視化します。"""),
                code("""
                    names = model.named_steps["前処理"].get_feature_names_out()
                    transformed = model.named_steps["前処理"].transform(X_train.head(3))
                    if hasattr(transformed, "toarray"):
                        transformed = transformed.toarray()
                    print("元の列数:", X_train.shape[1], "→ 変換後:", transformed.shape[1])
                    pd.DataFrame(transformed, columns=names, index=X_train.head(3).index).iloc[:, :10].round(2)
                """),
                markdown("""### 出力の読み方

- **元の列数 → 変換後**で列が増えているのは、カテゴリがOne-Hotで展開されたため。列名に`カテゴリ列__solvent_EtOH`のような名前が付きます。
- 数値列は標準化され、**平均0付近・小さめの値**になっています。One-Hot列は0か1。「モデルが実際に見ている数字」はこの姿です。

## CHANGE

数値の欠損補完を`median`から`mean`へ変え、成績を比べます。変更は`SimpleImputer(strategy=...)`の**1か所だけ**。Pipelineだと変更点が1か所に集約され、実験が管理しやすくなります。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：自作の前処理を作り、前処理も探索対象にする

sklearnに用意された変換だけでなく、**自分の化学知識を前処理として書く**ことができます。また、
「どの補完戦略が良いか」のような前処理の選択も、モデルの設定と同じく**交差検証で選べます**。"""),
            markdown("""### 自作変換器：`fit`と`transform`を持つ部品を書く

`BaseEstimator, TransformerMixin`を継承し、`fit`（学習することがあれば覚える）と`transform`（変換する）を
実装すれば、**Pipelineに差し込める自分だけの前処理**になります。ここでは「分子量あたりのTPSA」と
「最適温度からの距離」を足す変換器を作ります。"""),
            code("""
                from sklearn.base import BaseEstimator, TransformerMixin
                import numpy as np

                class ChemRatioFeatures(BaseEstimator, TransformerMixin):
                    "分子量あたりのTPSAと、最適温度78℃からの距離を足す自作変換器。"
                    def fit(self, X, y=None):
                        return self
                    def transform(self, X):
                        X = X.copy()
                        X["tpsa_per_mw"] = X["tpsa"] / X["molecular_weight"].replace(0, np.nan)
                        X["temp_distance"] = (X["temperature_c"] - 78).abs()
                        return X

                ChemRatioFeatures().fit_transform(df[["tpsa", "molecular_weight", "temperature_c"]].head()).round(3)
            """),
            markdown("""### 出力の読み方

元の3列に、新しい2列（`tpsa_per_mw`・`temp_distance`）が加わっています。`fit`は何も学習せず自身を返す
だけ（この変換は統計量を使わないため）。この形にしておくと、`Pipeline`へ入れて**分割の内側で**適用でき、
第11回の特徴量設計をリークなく行えます。"""),
            markdown("""### 前処理の設定を`GridSearchCV`で選ぶ

`Pipeline`の各部品の設定には`前処理__数値列__欠損補完__strategy`のように**アンダースコア2つ**で
辿り着けます。この記法を使い、補完戦略（median/mean）を交差検証で比較して自動選択します。"""),
            code("""
                from sklearn.model_selection import GridSearchCV

                grid_pipe = Pipeline([("前処理", preprocess), ("予測", LogisticRegression(max_iter=1000))])
                param_grid = {"前処理__数値列__欠損補完__strategy": ["median", "mean"]}
                search = GridSearchCV(grid_pipe, param_grid, cv=5, scoring="f1")
                search.fit(X_train, y_train)
                print("最良設定:", search.best_params_)
                print("最良CV F1:", round(search.best_score_, 3))
            """),
            markdown("""### 出力の読み方

`best_params_`が選ばれた補完戦略、`best_score_`がそのときの交差検証F1です。ポイントは、**前処理も
モデル設定と同じ土俵で、リークなく比較・選択できる**こと。Pipelineにまとめておいたからこそ可能になります。"""),
        ],
        [
            markdown("""## APPENDIX（任意・追加演習）

Pipelineをさらに実務的に使い込みます。90分の外の自習向けです。まず`make_column_selector`で、
**列の型（数値/文字）から自動で担当を振り分ける**書き方。列名を手で並べる手間が消えます。"""),
            code("""
                from sklearn.pipeline import make_pipeline
                from sklearn.compose import make_column_selector, make_column_transformer

                auto_pre = make_column_transformer(
                    (make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), make_column_selector(dtype_include="number")),
                    (make_pipeline(SimpleImputer(strategy="most_frequent"), OneHotEncoder(handle_unknown="ignore")), make_column_selector(dtype_include="object")),
                )
                auto_model = make_pipeline(auto_pre, LogisticRegression(max_iter=1000)).fit(X_train, y_train)
                print("列の型で自動振り分けした検証精度:", round(auto_model.score(X_valid, y_valid), 3))
            """),
            markdown("""### 出力の読み方

`make_column_selector(dtype_include="number")`が数値列を、`"object"`が文字列列を自動で拾います。列が
増減しても書き換え不要。実データで列数が多いときに効きます。`.score`は分類では既定でaccuracyを返します。"""),
            markdown("""### 前処理とモデルを「まとめて」探索する

前処理の設定とモデルのハイパーパラメータを、1つの`GridSearchCV`で同時に探します。すべてPipelineの
内側なので、リークなく公平に比較できます。"""),
            code("""
                from sklearn.model_selection import GridSearchCV
                from sklearn.ensemble import RandomForestClassifier

                full = Pipeline([("前処理", preprocess), ("予測", RandomForestClassifier(random_state=42))])
                grid = {
                    "前処理__数値列__欠損補完__strategy": ["median", "mean"],
                    "予測__max_depth": [4, 6, None],
                    "予測__n_estimators": [200, 300],
                }
                search = GridSearchCV(full, grid, cv=5, scoring="f1")
                search.fit(X_train, y_train)
                print("最良設定:", search.best_params_)
                print("最良CV F1:", round(search.best_score_, 3))
            """),
            markdown("""### 出力の読み方

前処理（補完戦略）とモデル（深さ・木の本数）の**最良の組み合わせ**が一度に選ばれます。組合せは
2×3×2=12通り×5分割=60回の学習。前処理も探索対象にできるのが、Pipeline最大の利点です。"""),
            markdown("""### 学習済みPipelineを保存して再利用する

選ばれた最良のPipelineを`joblib`で保存し、読み直しても同じ予測になることを確かめます。前処理ごと
保存されるので、配布先は`predict`するだけです（第15回の永続化の先取り）。"""),
            code("""
                import joblib
                import numpy as np

                path = ROOT / "workspace" / "pipeline_09.joblib"
                joblib.dump(search.best_estimator_, path)
                loaded = joblib.load(path)
                assert np.array_equal(search.best_estimator_.predict(X_valid), loaded.predict(X_valid)), "保存前後で予測が不一致"
                print("保存・読込で同じ予測:", path)
            """),
            markdown("""### 出力の読み方

`assert`が通れば、前処理込みのPipelineが丸ごと保存・復元できたということ。「モデルだけ保存して前処理を
忘れる」という実務で頻発する事故を、Pipeline化で防げます。"""),
        ],
    )

    # ---- 第10回 ----
    write_notebook(
        "10-model-comparison",
        notebook(
            "第10回：モデル対決",
            "複雑なモデルは本当にいつも優れているか。",
            [
                markdown("""## 「複雑なモデルほど強い」は本当か

新しいモデルを次々試したくなりますが、この回で確かめるのは**「複雑さは必ずしも勝たない」**という
実感です。大事なのは勝ち負けそのものより、**フェアな比べ方**を身につけること。フェアな比較には
3つの「同じ」が要ります：**同じ分割・同じ指標・同じ前処理**。

まず、単純〜複雑まで5つのモデルを1つの辞書にまとめます。前処理が要るモデルは`make_pipeline`で
前処理込みにしてあるので、どれも同じ`X_train`をそのまま渡せます。"""),
                common_load_cell(),
                code("""
                    import time
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
                        "Gradient Boosting": HistGradientBoostingClassifier(max_iter=200, random_state=42),
                    }
                """),
                markdown("""## TRY：同じ土俵で、F1と学習時間を並べる

5モデルを同じデータで学習し、**検証F1**と**学習にかかった秒数**を並べます。性能だけでなく
**コスト（時間）**も一緒に見るのが実務的な比較です。"""),
                code("""
                    rows = []
                    for name, model in models.items():
                        start = time.perf_counter()
                        model.fit(X_train, y_train)
                        elapsed = time.perf_counter() - start
                        rows.append({"モデル": name, "検証F1": f1_score(y_valid, model.predict(X_valid)), "学習秒": elapsed})
                    pd.DataFrame(rows).sort_values("検証F1", ascending=False).round({"検証F1": 3, "学習秒": 4})
                """),
                markdown("""### 出力の読み方

- **Dummyが最下位**なのは当然。他がDummyをどれだけ引き離すかが価値です。
- **最も複雑なモデルが1位とは限りません**。線形モデルが健闘したり、木モデルと僅差だったりします。差が小さいなら、**速くて説明しやすいモデル**を選ぶ理由になります。
- ただし、これは**1回の分割の結果**。順位が分割運で入れ替わるかもしれません。次で交差検証により安定性を確かめます。"""),
                markdown("""## CORE深掘り：交差検証で「安定して強いか」を見る

1回の勝敗は運に左右されます。交差検証で**平均F1・ばらつき(標準偏差)・最低F1**を出し、
「平均が高い」だけでなく「**転んでも大崩れしない**（最低F1が高い）」モデルを評価します。"""),
                code("""
                    from sklearn.model_selection import StratifiedKFold, cross_val_score

                    cv = StratifiedKFold(5, shuffle=True, random_state=42)
                    stability = []
                    for name, estimator in models.items():
                        scores = cross_val_score(estimator, df[features], df["active"], cv=cv, scoring="f1")
                        stability.append({"モデル": name, "F1平均": scores.mean(), "F1標準偏差": scores.std(), "最低F1": scores.min()})
                    pd.DataFrame(stability).sort_values("F1平均", ascending=False).round(3)
                """),
                markdown("""### 出力の読み方

- **F1平均**で総合力、**F1標準偏差**で安定度、**最低F1**で最悪ケースを見ます。
- 平均が僅差なら、**標準偏差が小さい方**が実務では安心。平均1位でも最低F1が極端に低いモデルは、条件次第で大外しする危険があります。
- 1回の分割（前セル）と順位が入れ替わることもあります。だから**単発の勝敗で決めない**——これがこの回の教訓です。"""),
                markdown("""## 5人の担当

Dummy / Logistic / Tree / Random Forest / Gradient Boosting を1人ずつ担当し、
**スコア・学習時間・説明しやすさ・安定性**を1行で共有します。「どれが最強か」ではなく
「**この用途にはどれが妥当か**」を言葉にするのがゴールです。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：その差は「偶然」か、そして束ねる価値

上位2モデルのF1差が0.01だったとして、それは本物の差でしょうか、それとも分割運でしょうか。
ここでは**反復交差検証＋統計的検定**で差の確からしさを測り、次に複数モデルを**束ねる**価値を見ます。"""),
            markdown("""### 反復CV＋Wilcoxon検定：差は偶然でないか

分割の乱数を変えて交差検証を何度も繰り返し（反復CV）、上位2モデルのスコア列を**対応のある検定
（Wilcoxon）**で比べます。p値が小さいほど「差は偶然では説明しにくい」と読めます。"""),
            code("""
                import numpy as np
                from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
                from scipy.stats import wilcoxon

                rcv = RepeatedStratifiedKFold(n_splits=5, n_repeats=4, random_state=42)
                dist = {name: cross_val_score(est, df[features], df["active"], cv=rcv, scoring="f1") for name, est in models.items()}
                summary = pd.DataFrame({name: {"F1平均": s.mean(), "F1_SD": s.std()} for name, s in dist.items()}).T.sort_values("F1平均", ascending=False)
                display(summary.round(3))
                top2 = summary.index[:2].tolist()
                stat, p = wilcoxon(dist[top2[0]], dist[top2[1]])
                print(f"{top2[0]} vs {top2[1]} のWilcoxon検定 p={p:.3f}（小さいほど差が偶然でない）")
            """),
            markdown("""### 出力の読み方

- **p値が0.05より大きい**なら、上位2モデルの差は「偶然の範囲」かもしれず、**わざわざ複雑な方を選ぶ理由は弱い**。
- p値が小さくても、差の**大きさ**（実務的な意味があるか）は別問題。「統計的に有意」と「実務的に重要」は違う、という感覚を持ちます。
- 補足：反復交差検証のスコアは同じデータを使い回すため完全には独立でなく、素朴な検定のp値は**楽観的（有意に出やすい）**になりがちです。ここでは大まかな目安として読み、断定の根拠には使いません。"""),
            markdown("""### 投票・スタッキングで束ねる

間違え方の違うモデルを組み合わせると、単体より安定することがあります。**Voting**は予測確率の平均、
**Stacking**は各モデルの予測を入力に上位モデルで統合します。単体最良と比べます。"""),
            code("""
                from sklearn.ensemble import VotingClassifier, StackingClassifier
                from sklearn.linear_model import LogisticRegression

                estimators = [(name, est) for name, est in models.items() if name != "Dummy"]
                ensembles = {
                    "Voting(soft)": VotingClassifier(estimators, voting="soft"),
                    "Stacking": StackingClassifier(estimators, final_estimator=LogisticRegression(max_iter=1000), cv=5),
                }
                for name, est in ensembles.items():
                    scores = cross_val_score(est, df[features], df["active"], cv=StratifiedKFold(5, shuffle=True, random_state=42), scoring="f1")
                    print(f"{name:14s} F1平均={scores.mean():.3f} ± {scores.std():.3f}")
                print("最良単体:", summary.index[0], "F1平均=", round(summary.iloc[0, 0], 3))
            """),
            markdown("""### 出力の読み方

束ねたモデルが最良単体を**明確に上回るとは限りません**。束ねる価値が出るのは、元のモデルたちが
「互いに違う間違え方」をするとき。差がわずかなら、運用の手間を考えて単体を選ぶのも正解です。"""),
            markdown("""### 任意：勾配ブースティング専用ライブラリ

XGBoostが入っていれば試します（`uv sync --extra advanced`）。無い環境では自動でメッセージを出して
スキップし、sklearnの`HistGradientBoosting`で代用できます。"""),
            code("""
                try:
                    from xgboost import XGBClassifier
                    xgb = XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.1, random_state=42, eval_metric="logloss")
                    scores = cross_val_score(xgb, df[features].fillna(df[features].median()), df["active"], cv=5, scoring="f1")
                    print("XGBoost F1平均:", round(scores.mean(), 3))
                except ImportError:
                    print("XGBoostは任意です（uv sync --extra advanced）。HistGradientBoostingで代用できます。")
            """),
            markdown("""### 出力の読み方

XGBoostのF1が、既に見たGradient Boostingと**近い値**になるはずです。「専用ライブラリ＝必ず勝つ」では
ありません。ライブラリの新しさより、**フェアな比較の枠組み**の方がずっと大事だと、あらためて分かります。"""),
        ],
        [
            markdown("""## APPENDIX（任意・追加演習）

モデル比較をさらに多面的に。90分の外の自習向けです。まず2モデルの**学習曲線**を並べ、
「データ追加が効くタイプか」を比べます。"""),
            code("""
                import numpy as np
                import matplotlib.pyplot as plt
                from sklearn.model_selection import learning_curve

                fig, axes = plt.subplots(1, 2, figsize=(12, 4))
                for ax, name in zip(axes, ["Logistic", "Random Forest"]):
                    sizes, tr, va = learning_curve(models[name], df[features], df["active"], cv=5, scoring="f1", train_sizes=np.linspace(0.2, 1.0, 5))
                    ax.plot(sizes, tr.mean(1), "o-", label="学習")
                    ax.plot(sizes, va.mean(1), "o-", label="検証")
                    ax.set_title(name); ax.set_xlabel("学習件数"); ax.set_ylabel("F1"); ax.legend()
                plt.tight_layout()
            """),
            markdown("""### 出力の読み方

- 線形モデル（Logistic）は学習と検証の差が小さい（過学習しにくい）が頭打ちも早い傾向。
- Random Forestは差が大きい（表現力が高く過学習寄り）が、データを増やすと伸びる余地があることも。
- **モデルによってデータ追加の効き方が違う**。増やすか、特徴量を工夫するかの判断材料になります。"""),
            markdown("""### 複数指標を一度に比べる

F1だけでなく、precision・recall・ROC-AUCも同時に交差検証で出します。用途によって重視する指標が
違う（第8回）ので、多面的に見て選びます。"""),
            code("""
                from sklearn.model_selection import cross_validate, StratifiedKFold

                cv = StratifiedKFold(5, shuffle=True, random_state=42)
                scoring = ["f1", "precision", "recall", "roc_auc"]
                rows = []
                for name, est in models.items():
                    if name == "Dummy":
                        continue
                    res = cross_validate(est, df[features], df["active"], cv=cv, scoring=scoring)
                    rows.append({"モデル": name, **{m: res[f"test_{m}"].mean() for m in scoring}})
                pd.DataFrame(rows).round(3)
            """),
            markdown("""### 出力の読み方

あるモデルはrecallが高くprecisionが低い、別のモデルは逆、ということが起きます。**単一のF1では隠れる
個性**が見えます。「見逃しを避けたい」ならrecall列、「空振りを避けたい」ならprecision列で選びます。"""),
            markdown("""### 性能とコストの釣り合い（木の本数）

木の本数（`n_estimators`）を増やすと精度は上がりやすい一方、学習時間も延びます。どこで頭打ちになるかを
見て、**費用対効果**で選びます。"""),
            code("""
                import time
                from sklearn.pipeline import make_pipeline
                from sklearn.impute import SimpleImputer
                from sklearn.metrics import f1_score

                rows = []
                for n in [50, 100, 200, 400]:
                    est = make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=n, max_depth=6, random_state=42))
                    t = time.perf_counter(); est.fit(X_train, y_train); sec = time.perf_counter() - t
                    rows.append({"n_estimators": n, "学習秒": sec, "検証F1": f1_score(y_valid, est.predict(X_valid))})
                pd.DataFrame(rows).round({"学習秒": 4, "検証F1": 3})
            """),
            markdown("""### 出力の読み方

F1はある本数で頭打ちになり、その先は時間だけ延びるはず。**「もう増やしても得しない」点**を見つけるのが
チューニングの勘所。本番のデータ量ではこの差が大きくなるので、小さいうちに感覚をつかんでおきます。"""),
        ],
    )

    # ---- 第11回 ----
    write_notebook(
        "11-feature-engineering",
        notebook(
            "第11回：化学の知識を特徴量にする",
            "研究者の知識を、モデルへ渡せる形にするにはどうするか。",
            [
                markdown("""## 特徴量設計＝あなたの化学知識をモデルへ渡す

モデルは与えられた列しか見ません。**「最適温度から離れるほど収率が落ちる」**という知識を持っていても、
`temperature_c`の生の値だけでは、モデルがその山型を学ぶのは大変です。そこで、知識を**計算式**にして
新しい列（特徴量）として渡します。これが特徴量設計です。

鉄則が2つあります。
1. **予測時点で計算できること**（第5回。実験後の値から作らない）。
2. **追加の効果は、同じ検証条件で前後比較して確かめる**（思い込みで良し悪しを決めない）。"""),
                common_load_cell(),
                markdown("""## TRY：仮説を計算式にする

2つの仮説を式にします。**「最適温度78℃からの距離」**（離れるほど収率減、という山型を直接表す）と、
**「単位時間あたりの濃度」**（濃度と時間の兼ね合い）。どちらも計画時に計算できる値です。"""),
                code("""
                    engineered = df.copy()
                    engineered["temperature_distance"] = (engineered["temperature_c"] - 78).abs()
                    engineered["concentration_per_hour"] = engineered["concentration_m"] / engineered["reaction_time_h"]
                    engineered[["temperature_c", "temperature_distance", "concentration_per_hour"]].head()
                """),
                markdown("""### 読みどころ

`temperature_distance`は、78℃から上下どちらに離れても大きくなる値（絶対値）。第4回で見た「温度と収率の
山型」を、モデルにとって学びやすい**単調な形**に翻訳しています。生の温度より効くかどうかは、次で検証します。"""),
                markdown("""## アブレーション：追加の効果を「同じ条件」で確かめる

**アブレーション**とは、要素を足し引きして寄与を測る比較のこと。特徴量を追加する前後で、
**同じモデル・同じ交差検証**でMAEを比べます。これをやらずに「良さそうだから採用」は禁物です。"""),
                code("""
                    from sklearn.model_selection import cross_val_score, KFold
                    from sklearn.pipeline import make_pipeline
                    from sklearn.impute import SimpleImputer
                    from sklearn.ensemble import RandomForestRegressor

                    base = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
                    added = [*base, "temperature_distance", "concentration_per_hour"]
                    cv = KFold(5, shuffle=True, random_state=42)
                    for label, cols in {"追加前": base, "追加後": added}.items():
                        est = make_pipeline(SimpleImputer(strategy="median"), RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42))
                        scores = cross_val_score(est, engineered[cols], engineered["yield_pct"], cv=cv, scoring="neg_mean_absolute_error")
                        print(f"{label}: MAE={-scores.mean():.3f} ± {scores.std():.3f}")
                """),
                markdown("""### 出力の読み方

- 「追加後」のMAEが「追加前」より**下がっていれば**、その特徴量は効いています。**ばらつき(±)より大きく**下がっているかも見ます（±の中の差は誤差かも）。
- 効かない・悪化することもあります。それも立派な結果——**「この仮説はこのモデルには効かなかった」**と分かるのが検証の価値です。悪化した実験も記録します（第12回）。"""),
                markdown("""## CORE深掘り：関連の強い特徴量を選ぶ（相互情報量）

特徴量が増えると、効かない列がノイズになることも。**相互情報量（第4回）**で目的変数との関連が強い順に
並べ、上位k個を選びます。相関と違い、山型のような非線形の関連も拾えます。"""),
                code("""
                    from functools import partial
                    from sklearn.feature_selection import SelectKBest, mutual_info_regression

                    # random_stateを固定しないとMIの推定値は実行ごとに変わる（第4回と同じ作法）
                    mi_score = partial(mutual_info_regression, random_state=42)
                    sel_data = engineered[added].fillna(engineered[added].median())
                    selector = SelectKBest(mi_score, k=4).fit(sel_data, engineered["yield_pct"])
                    pd.DataFrame({"特徴量": added, "MIスコア": selector.scores_, "選択": selector.get_support()}).sort_values("MIスコア", ascending=False).round(3)
                """),
                markdown("""### 出力の読み方（結果は素直に受け止める）

MIスコアの高い順に並び、上位4つに「選択=True」が付きます。ここで大事なのは、**自作の`temperature_distance`が
必ず上位に来るとは限らない**ことです。実際、このデータの単変量MIでは上位に来ないことがあります。相互情報量は
**1列ずつ単独で**目的変数との関連を測るため、「他の列と組み合わせて効く」種類の特徴量を低く見積もることがあります。
思い込みで良し悪しを決めず、数字を見る。そして次のDEEP DIVE/APPENDIXで、**別の見方（並べ替え重要度）だと結論が
変わる**ことを実際に確かめます。`random_state`を固定しているのは、固定しないとMIの推定値が毎回変わるためです。"""),
                markdown("""## CHALLENGE：RDKitでSMILESから記述子を計算する

分子量やLogPは、本来は分子構造（SMILES）から計算できます。RDKitが入っていれば、エタノールの
記述子を実際に計算してみます。無い環境では自動でスキップし、計算済みの列で本編を進められます。"""),
                code("""
                    try:
                        from rdkit import Chem
                        from rdkit.Chem import Descriptors, Crippen
                        molecule = Chem.MolFromSmiles("CCO")
                        print("エタノールの分子量:", round(Descriptors.MolWt(molecule), 2))
                        print("エタノールのLogP:", round(Crippen.MolLogP(molecule), 2))
                    except ImportError:
                        print("RDKitは任意（uv sync --extra chemistry）。計算済みmolecular_weight/logp/tpsaで本編を進められます。")
                """),
                markdown("""### 読みどころ

RDKitが動けば、SMILES（`CCO`＝エタノール）から分子量やLogPが再現されます。**「記述子＝構造から計算できる
特徴量」**だと腹落ちします。RDKitは発展扱いなので、無くても計算済みの列で全く問題ありません。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：リークしやすい特徴量と、賢い選択

強力だが**リークしやすい**特徴量の代表が**target encoding**（カテゴリを目的変数の平均で置き換える）です。
やり方を誤ると、第6回で学んだリークを自ら仕込むことになります。安全なやり方を身につけます。"""),
            markdown("""### target encoding：全データ平均は「リーク」、OOFなら安全

「系列ごとの平均収率」を特徴量にしたいとします。**全データの平均**で作ると、各行の答えが自分の特徴量に
混ざりリークします。正しくは、第6回の交差検証と同じ発想で、**その行を含まない分割の平均**で作ります
（OOF＝out-of-fold）。両者でMAEを比べ、リークが楽観を生むことを確かめます。"""),
            code("""
                import numpy as np
                from sklearn.model_selection import KFold, cross_val_score
                from sklearn.linear_model import Ridge

                def oof_target_encode(frame, col, target, n_splits=5, seed=42):
                    "分割の内側で平均を学習するリーク安全なtarget encoding。"
                    encoded = pd.Series(index=frame.index, dtype=float)
                    global_mean = frame[target].mean()
                    for tr, va in KFold(n_splits, shuffle=True, random_state=seed).split(frame):
                        means = frame.iloc[tr].groupby(col)[target].mean()
                        encoded.iloc[va] = frame.iloc[va][col].map(means).fillna(global_mean).to_numpy()
                    return encoded

                leaky = df["scaffold_group"].map(df.groupby("scaffold_group")["yield_pct"].mean())
                safe = oof_target_encode(df, "scaffold_group", "yield_pct")
                num_cols = ["temperature_c", "concentration_m", "logp"]
                X_num = df[num_cols].fillna(df[num_cols].median())
                for label, enc in {"リークあり(全データ平均)": leaky, "OOF(安全)": safe}.items():
                    feats = X_num.assign(scaffold_te=enc.to_numpy())
                    scores = cross_val_score(Ridge(), feats, df["yield_pct"], cv=5, scoring="neg_mean_absolute_error")
                    print(f"{label}: MAE={-scores.mean():.3f}")
                print("リークありは楽観的に見えることがある。実運用の性能はOOFに近い。")
            """),
            markdown("""### 出力の読み方

「リークあり」のMAEが「OOF」より**小さく（良く）見える**ことがあります。しかしそれは幻——本番では
その行の答えは手に入りません。**実運用の実力はOFFの側**。強力な特徴量ほど、作り方のリークに注意します。"""),
            markdown("""### RFECV：交差検証つきで特徴量を絞り込む

`RFECV`は、重要度の低い特徴量を1つずつ削りながら交差検証し、**性能が最も良くなる特徴量の組**を
自動で選びます。人手の取捨選択より客観的です。ここでは**係数の大きさで重要度を測る線形モデル(Ridge)**で
回します（後述のとおり、木モデルはノイズに強すぎてRFECVが列を削らないことが多いため）。尺度をそろえてから
かけます。"""),
            code("""
                import numpy as np
                from sklearn.feature_selection import RFECV
                from sklearn.linear_model import Ridge
                from sklearn.preprocessing import StandardScaler

                # わざと「無意味な列」を混ぜて、RFECVがそれを削れるかを確かめる
                rng = np.random.default_rng(0)
                rfe_data = engineered[added].fillna(engineered[added].median()).copy()
                rfe_data["noise"] = rng.normal(size=len(rfe_data))     # 目的変数と無関係な乱数列
                rfe_data["logp_copy"] = rfe_data["logp"]                # 既存列の複製（冗長）
                scaled = pd.DataFrame(StandardScaler().fit_transform(rfe_data), columns=rfe_data.columns, index=rfe_data.index)
                rfecv = RFECV(Ridge(alpha=1.0), cv=5, scoring="neg_mean_absolute_error", min_features_to_select=2)
                rfecv.fit(scaled, engineered["yield_pct"])
                print("元の列数:", scaled.shape[1], "→ 選ばれた列数:", rfecv.n_features_)
                pd.DataFrame({"特徴量": rfe_data.columns, "残す": rfecv.support_, "順位": rfecv.ranking_}).sort_values("順位")
            """),
            markdown("""### 出力の読み方

- `残す=True`が採用列、`順位=1`が最重要グループ。**わざと混ぜた`noise`（乱数）と`logp_copy`（複製）が削られていれば**、RFECVが「役に立たない列を見抜いて外す」働きをしていると確認できます。
- 木モデル(RandomForest)ではなく線形モデル(Ridge)を使ったのは、**木モデルはノイズ列があっても性能が落ちにくく、RFECVが何も削らないことが多い**ため。**推定器を変えると選択結果も変わる**——特徴量選択も「どの手法で測るか」に依存する、という点も併せて押さえます。
- 選択も交差検証の内側で行うことで、選びすぎ（過学習）を避けています。"""),
        ],
        [
            markdown("""## APPENDIX（任意・追加演習）

特徴量づくりの引き出しを増やします。90分の外の自習向けです。まず**交互作用特徴量**——2つの列の
掛け算で「組み合わせの効果」を表します（温度×濃度など）。"""),
            code("""
                from sklearn.preprocessing import PolynomialFeatures

                cols = ["temperature_c", "concentration_m"]
                pair = engineered[cols].fillna(engineered[cols].median())
                inter = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
                out = inter.fit_transform(pair)
                display(pd.DataFrame(out, columns=inter.get_feature_names_out(), index=pair.index).head())
            """),
            markdown("""### 出力の読み方

元の2列に加え、`temperature_c concentration_m`（掛け算）の列ができます。`interaction_only=True`なので
二乗は作らず組み合わせだけ。「片方が高いときだけもう片方が効く」ような関係を、モデルへ渡せます。"""),
            markdown("""### 連続値を区間に区切る（ビニング）

温度のような連続値を4区間に区切ると、非線形な効果を扱いやすくなったり、解釈しやすくなったりします。
`KBinsDiscretizer`（分位点で等件数に区切る）を使い、区間ごとの平均収率を見ます。"""),
            code("""
                from sklearn.preprocessing import KBinsDiscretizer

                temp = engineered[["temperature_c"]].fillna(engineered["temperature_c"].median())
                binner = KBinsDiscretizer(n_bins=4, encode="ordinal", strategy="quantile")
                engineered["temp_bin"] = binner.fit_transform(temp).astype(int)
                display(engineered.groupby("temp_bin")["yield_pct"].mean().round(1))
            """),
            markdown("""### 出力の読み方

区間0（低温）〜3（高温）ごとの平均収率が出ます。中間の区間で収率が高い（山型）なら、第4回で見た
温度の効果と一致。ビニングは効果を見せやすい一方、情報を捨てる面もあるので、元の連続値と併用も検討します。"""),
            markdown("""### 作った特徴量の効き目を、並べ替え重要度で確かめる

第1・12回で使った並べ替え重要度を、この回で作った特徴量を含めた全体に適用します。自作特徴量が
上位に来るかを、holdoutで公平に確認します。"""),
            code("""
                from sklearn.inspection import permutation_importance
                from sklearn.model_selection import train_test_split
                from sklearn.ensemble import RandomForestRegressor

                Xe = engineered[added].fillna(engineered[added].median())
                Xtr, Xva, ytr, yva = train_test_split(Xe, engineered["yield_pct"], test_size=0.25, random_state=42)
                rf = RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42).fit(Xtr, ytr)
                perm = permutation_importance(rf, Xva, yva, scoring="neg_mean_absolute_error", n_repeats=15, random_state=42)
                pd.DataFrame({"特徴量": added, "重要度": perm.importances_mean}).sort_values("重要度", ascending=False).round(3)
            """),
            markdown("""### 出力の読み方：3つの見方が食い違うのは正常

ここでは`temperature_distance`が**上位に来ることがあります**。ところが同じ回のCOREでは、相互情報量(MI)で
同じ列が**下位**、アブレーションでは追加しても**MAEがほとんど改善しない**——3つの見方で結論が食い違います。
矛盾ではなく、**それぞれ別の問いに答えているから**です。

- **アブレーション**：その列を入れるか抜くかで最終性能がどう動くか。他の列で代用が効くと、抜いても悪化せず「効果なし」に見える。
- **相互情報量**：その列を単独で見たときの関連の強さ。組み合わせて効く効果は測れない。
- **並べ替え重要度**：学習済みモデルが実際にその列に依存しているか。`temperature_distance`は`temperature_c`から作った相関の強い列なので、モデルがどちらを使うかで重要度が振れやすい。

教訓は2つ。**(1) 1つの指標だけで特徴量の良し悪しを断じない。(2) 元の列と強く相関する派生列（今回の距離特徴量）は、
重要度が不安定になりやすい。** 「作る→交差検証で効果を確かめる→複数の見方で解釈する」という一巡こそが、
思い込みを避ける特徴量設計です。"""),
        ],
    )

    # ---- 第12回 ----
    write_notebook(
        "12-experiment-cycle",
        notebook(
            "第12回：改善実験を小さく回す",
            "改善した理由を後から説明できる実験とは何か。",
            [
                markdown("""## 「なんとなく良くなった」を卒業する

改善は勢いでやると、後で「なぜ良くなったのか」を説明できません。この回のテーマは、**理由を後から
説明できる実験のやり方**です。次の原則が効きます。

1. **一度に変えるのは1つだけ**（複数変えると、どれが効いたか分からない）。
2. **比較条件は固定**（同じ分割・同じ指標）。
3. **結果は平均とばらつきで残す**（1回のスコアで一喜一憂しない）。
4. **良くなった実験も悪くなった実験も記録する**（消さない）。

まず、実験の土台（データ・交差検証）を用意します。"""),
                common_load_cell(),
                code("""
                    from sklearn.model_selection import cross_validate, StratifiedKFold
                    from sklearn.impute import SimpleImputer
                    from sklearn.pipeline import make_pipeline
                    from sklearn.ensemble import RandomForestClassifier
                    from sklearn.inspection import permutation_importance

                    features = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
                    X, y = df[features], df["active"]
                    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
                """),
                markdown("""## TRY：1要素だけ変えて、実験ログに残す

`max_depth`**だけ**を変えた3つの実験を回し、結果を表（実験ログ）にします。他の設定は固定。
学習F1と検証F1平均を両方残すのは、**過学習の度合い**（第6回）も一緒に記録するためです。"""),
                code("""
                    rows = []
                    for depth in [3, 6, None]:
                        model = make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=150, max_depth=depth, random_state=42))
                        scores = cross_validate(model, X, y, cv=cv, scoring="f1", return_train_score=True)
                        rows.append({"実験名": f"depth={depth}", "変更点": "max_depthのみ",
                                     "学習F1": scores["train_score"].mean(), "検証F1平均": scores["test_score"].mean(),
                                     "検証F1標準偏差": scores["test_score"].std()})
                    experiment_log = pd.DataFrame(rows)
                    experiment_log.round(3)
                """),
                markdown("""### 出力の読み方

- **検証F1平均が最も高い深さ**が候補。ただし**検証F1標準偏差**が大きいなら、その優位は不安定かもしれません。
- 差が標準偏差より小さいなら「実質同じ」と読み、より単純な（浅い）設定を選ぶのが無難です。
- `depth=None`で学習F1が跳ね上がり検証F1が伸びないなら、過学習。**表1つで「効果」と「過学習」を同時に管理**できます。"""),
                markdown("""## 実験ログの最小項目

同期回でも自習でも、次を1行で残せば十分です。

- **実験名 / 変えたもの（1つ）/ 固定した比較条件 / 結果の平均とばらつき / 気づき / 次の仮説**

Copilotには次の実験案を出してもらってもよいですが、**優先順位と「予測時点で妥当か」の判断は人**が行います。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：探索を自動化し、正直な推定を得る

手で`max_depth`を変えるのは学習には良いですが、設定が増えると大変です。**探索の自動化**と、
第6回で学んだ**ネストCV（正直な推定）**、そして**重要度を区間で読む**ことを扱います。"""),
            markdown("""### RandomizedSearchCV：設定を自動で探す

複数の設定候補から無作為に組み合わせを試し、交差検証で最良を選びます。総当たり（GridSearch）より
少ない回数で広く探せるのが利点。`n_iter`が試行回数です。"""),
            code("""
                from sklearn.model_selection import RandomizedSearchCV

                pipe = make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(random_state=42))
                param_dist = {
                    "randomforestclassifier__n_estimators": [100, 200, 300],
                    "randomforestclassifier__max_depth": [3, 4, 6, None],
                    "randomforestclassifier__min_samples_leaf": [1, 2, 4],
                    "randomforestclassifier__max_features": ["sqrt", "log2", None],
                }
                search = RandomizedSearchCV(pipe, param_dist, n_iter=10, cv=cv, scoring="f1", random_state=42)
                search.fit(X, y)
                print("最良設定:", search.best_params_)
                print("探索内での最良CV F1:", round(search.best_score_, 3))
            """),
            markdown("""### 出力の読み方と、大事な注意

`best_params_`が選ばれた設定、`best_score_`がそのCF1です。**ただしこの`best_score_`をそのまま「性能」として
報告してはいけません**。たくさん試して一番良かった数字なので、下駄を履いています。次で正直な推定に直します。"""),
            markdown("""### ネストCV：探索の下駄を脱いだ推定

「探索」を1つのモデルとみなし、その外側でもう一段の交差検証をかけます。各外側分割で設定を選び直し、
未見のデータで評価するので、**探索による楽観が乗らない正直な性能**が得られます。"""),
            code("""
                from sklearn.model_selection import cross_val_score

                outer = StratifiedKFold(5, shuffle=True, random_state=7)
                nested = cross_val_score(search, X, y, cv=outer, scoring="f1")
                print("ネストCV外側F1:", nested.round(3))
                print("楽観の少ない推定:", round(nested.mean(), 3), "±", round(nested.std(), 3), " ← 探索内スコアより低いのが普通")
            """),
            markdown("""### 出力の読み方

ネストCVの平均は、前セルの`best_score_`より**少し低い**のが普通で、その差が「探索による楽観」の大きさです。
論文や報告に載せるなら、こちらの正直な数字を使います。"""),
            markdown("""### 並べ替え重要度は「区間」で読む

第1回で見た並べ替え重要度を、今度は**ばらつき（±2SD）つき**で読みます。下限が0を跨ぐ特徴量は
「効いているとは言い切れない」。評価は学習に使っていない**holdout**で行い、公平性を保ちます。"""),
            code("""
                from sklearn.model_selection import train_test_split

                X_fit, X_holdout, y_fit, y_holdout = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
                best = make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)).fit(X_fit, y_fit)
                perm = permutation_importance(best, X_holdout, y_holdout, scoring="f1", n_repeats=30, random_state=42)
                importance = pd.DataFrame({
                    "特徴量": features,
                    "重要度平均": perm.importances_mean,
                    "下限(平均-2SD)": perm.importances_mean - 2 * perm.importances_std,
                }).sort_values("重要度平均", ascending=False)
                importance["0を跨ぐ"] = importance["下限(平均-2SD)"] <= 0
                importance.round(4)
            """),
            markdown("""### 出力の読み方

- `0を跨ぐ=True`の特徴量は、**寄与があるとは断言できない**（ばらつきの範囲に0が入る）。
- 上位で`0を跨ぐ=False`の特徴量が、自信を持って「効いている」と言える列。ここから**反証可能な次の仮説**
（「この列を強める特徴量を足したら改善するのでは？」）を1つ立てて、COREの実験ログへ戻ります。これが改善サイクルです。"""),
        ],
        [
            markdown("""## APPENDIX（任意・追加演習）

実験の回し方を仕組み化します。90分の外の自習向けです。まず**実験を1行で記録する関数**を作り、
複数の設定を回してログに溜めます。手作業のコピペより、記録漏れが減ります。"""),
            code("""
                from sklearn.model_selection import cross_val_score

                experiment_log = []
                def run_experiment(name, estimator, note=""):
                    "設定を交差検証で評価し、実験ログへ1行追加して返す。"
                    scores = cross_val_score(estimator, X, y, cv=cv, scoring="f1")
                    row = {"実験名": name, "F1平均": round(scores.mean(), 3), "F1_SD": round(scores.std(), 3), "気づき": note}
                    experiment_log.append(row)
                    return row

                run_experiment("depth3", make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=150, max_depth=3, random_state=42)), "浅め")
                run_experiment("depth6", make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42)), "標準")
                run_experiment("leaf4", make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=150, max_depth=6, min_samples_leaf=4, random_state=42)), "葉を大きく")
                pd.DataFrame(experiment_log)
            """),
            markdown("""### 出力の読み方

3つの実験がログにたまり、F1平均・ばらつき・気づきが1表に。**変更点と結果がセットで残る**ので、後から
「なぜこの設定にしたか」を説明できます。関数化しておくと、実験のたびに1行呼ぶだけで済みます。"""),
            markdown("""### 検証曲線：1つの設定を動かして最適点を探す

`validation_curve`は、1つのハイパーパラメータ（ここでは`max_depth`）を動かし、学習と検証のスコア推移を
描きます。最適な複雑さが視覚的に分かります。"""),
            code("""
                import matplotlib.pyplot as plt
                from sklearn.model_selection import validation_curve

                depths = [2, 3, 4, 6, 8, 12]
                tr, va = validation_curve(
                    make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=150, random_state=42)),
                    X, y, param_name="randomforestclassifier__max_depth", param_range=depths, cv=cv, scoring="f1",
                )
                plt.plot(depths, tr.mean(1), "o-", label="学習")
                plt.plot(depths, va.mean(1), "o-", label="検証")
                plt.xlabel("max_depth"); plt.ylabel("F1"); plt.legend(); plt.title("検証曲線")
                plt.tight_layout()
            """),
            markdown("""### 出力の読み方

学習F1は深さとともに上がり続けますが、検証F1は途中で頭打ち・下降します。**検証F1が最大になる手前**が
最適な深さ。2本の乖離が広がるほど過学習が進んでいる、という第6回の読み方がそのまま使えます。"""),
            markdown("""### 実験ログをファイルに残す

ログをCSVに保存し、読み直します。セッションをまたいで実験を積み上げられ、再現性（第15回）にもつながります。"""),
            code("""
                out = ROOT / "workspace" / "experiment_log.csv"
                pd.DataFrame(experiment_log).to_csv(out, index=False)
                reloaded = pd.read_csv(out)
                print("保存＆再読込した実験ログ:", out)
                display(reloaded)
            """),
            markdown("""### 出力の読み方

`workspace/experiment_log.csv`に保存され、読み直しても同じ内容。**記録を残す文化**が、思いつきの改善を
再現可能な知見へ変えます。良い変更も悪い変更も、まずログに残すことを、この回でいちばんの習慣にしてください。"""),
        ],
    )

    # ---- 第13回 ----
    write_notebook(
        "13-kaggle-kickoff",
        notebook(
            "第13回：Kaggleに入って最初の提出を作る",
            "コンペの説明を、ローカルの分析手順へどう翻訳するか。",
            [
                markdown("""## コンペは「これまでの総合演習」

Kaggle（や、この教材のローカル模擬コンペ）は、第1〜12回で学んだことを1本の流れにする総合演習です。
新しい手法は増えません。大事なのは、**コンペの説明を、いつもの分析手順へ翻訳する**こと。

最初に必ず4点を確認します：**目的（何を予測）／評価指標／データ（trainとtestの違い）／提出形式**。
まずデータを開いて形を見ます。"""),
                code("""
                    import pandas as pd
                    train = pd.read_csv(DATA / "local_competition" / "train.csv")
                    test = pd.read_csv(DATA / "local_competition" / "test.csv")
                    sample = pd.read_csv(DATA / "local_competition" / "sample_submission.csv")
                    print("train:", train.shape, "test:", test.shape, "提出見本:", sample.shape)
                    display(train.head(3))
                    display(sample.head(3))
                """),
                markdown("""### 出力の読み方

- **trainには`active`列があり、testには無い**はずです。testの答えは伏せられていて、提出して初めて採点されます。
- **提出見本(sample_submission)**は「こういう形で出してね」という雛形。列名と行数を必ずこれに合わせます。
- trainとtestの行数を足すと、第3回で見た元データの件数に対応します。"""),
                markdown("""## コンペ説明（この模擬コンペの4点）

- **目的**：実験計画時の情報から活性`active`（0/1）を予測する
- **指標**：F1（第8回。活性が少ないのでaccuracyでなくF1）
- **データ**：`train.csv`には答えあり、`test.csv`には無し
- **提出形式**：`sample_id`と`active`の2列

Kaggle Titanicを使う場合も、最初にこの4点（目的・指標・train/test・提出形式）を同じように確認します。"""),
                markdown("""## ベースラインを作る（第9回のPipelineを再利用）

第9回で学んだ`ColumnTransformer`＋`Pipeline`をそのまま使い、数値もカテゴリも安全に1つのモデルへ通します。
`sample_id`や実験後の列など、**使ってはいけない列を`drop_columns`で外す**のがポイント（第5回のリーク回避）。
まずローカルの検証F1で当たりを付けます。"""),
                code("""
                    from sklearn.model_selection import train_test_split
                    from sklearn.compose import ColumnTransformer
                    from sklearn.pipeline import Pipeline
                    from sklearn.impute import SimpleImputer
                    from sklearn.preprocessing import OneHotEncoder
                    from sklearn.ensemble import RandomForestClassifier
                    from sklearn.metrics import f1_score

                    target = "active"
                    # batch_id（実験バッチの通し番号）とexperiment_dateは、活性とは無関係な「ID的な列」。
                    # 特徴量に入れるとノイズになり、One-Hotで列だけ増えるので外す（第5回の予測時点の考え方）。
                    drop_columns = ["sample_id", "experiment_date", "batch_id", "smiles", target]
                    features = [column for column in train.columns if column not in drop_columns]
                    numeric = train[features].select_dtypes(include="number").columns.tolist()
                    categorical = [column for column in features if column not in numeric]
                    preprocess = ColumnTransformer([
                        ("数値", SimpleImputer(strategy="median"), numeric),
                        ("カテゴリ", Pipeline([("補完", SimpleImputer(strategy="most_frequent")), ("one_hot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
                    ])
                    model = Pipeline([("前処理", preprocess), ("モデル", RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42))])
                    X_train, X_valid, y_train, y_valid = train_test_split(train[features], train[target], test_size=0.25, random_state=42, stratify=train[target])
                    model.fit(X_train, y_train)
                    print("ローカル検証F1:", round(f1_score(y_valid, model.predict(X_valid)), 3))
                """),
                markdown("""### 出力の読み方と、`scaffold_group`の注意

このローカル検証F1が、あなたの**最初のものさし**です。以降の改善は、必ずこの値と比べます。
「提出して順位が上がったか」だけでなく、**手元の検証がどう動いたか**を先に見る習慣が、コンペで
崩れないコツです（次のDEEP DIVEのCV-LBの話につながります）。

補足：ここでは`scaffold_group`（化合物系列）をカテゴリ特徴量として使っていますが、第6回のとおり本来は
**系列を跨がない分割（GroupKFold）とセットで扱うべき列**です。乱数分割のまま使うと評価が楽観的に
なり得ます。余力があれば、この列を外す・またはGroup分割にすると手元スコアがどう変わるか試してください。"""),
                markdown("""## TRY：提出CSVを作り、機械的に検査する

提出でいちばん多い失敗は、モデルの精度ではなく**フォーマットのミス**（列名・行数・余計なindex列）。
`assert`で自動チェックしてから保存します。`index=False`で余計な行番号列を混ぜないことも重要です。"""),
                code("""
                    model.fit(train[features], train[target])
                    submission = pd.DataFrame({"sample_id": test["sample_id"], "active": model.predict(test[features])})
                    assert list(submission.columns) == ["sample_id", "active"]
                    assert len(submission) == len(test)
                    assert submission["sample_id"].is_unique
                    output = ROOT / "workspace" / "submission_baseline.csv"
                    submission.to_csv(output, index=False)
                    print("保存先:", output)
                    submission.head()
                """),
                markdown("""### 出力の読み方

3つの`assert`を通ってCSVが保存されれば、形式は合格。`workspace/`に出力されるので、Kaggleが使える人は
これをアップロードします。使えない場合は、講師がローカルで採点します（第14回）。

## CHANGE

提出前に変えるのは**1点だけ**（第12回の原則）。例：`max_depth=6`を`3`へ変え、ローカル検証F1がどう動くか
確認してから提出します。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：手元でLeaderboardを予想する（OOF）と、提出を守る

コンペで沼にはまる典型が「提出回数を無駄遣いして、手元で何も分かっていない」状態です。
**OOF予測**で手元にLeaderboard相当の推定を持ち、**提出バリデータ**で形式ミスを防ぎます。"""),
            markdown("""### OOF予測：提出せずにスコアを見積もる

`cross_val_predict`は、各行を「その行を学習に使っていないモデル」で予測します（OOF＝out-of-fold）。
これを全部集めれば、**提出しなくても**手元でLeaderboardに近いF1を推定できます。提出回数の節約になります。"""),
            code("""
                from sklearn.model_selection import cross_val_predict, StratifiedKFold
                from sklearn.metrics import f1_score

                oof = cross_val_predict(model, train[features], train[target], cv=StratifiedKFold(5, shuffle=True, random_state=42))
                print("OOF F1:", round(f1_score(train[target], oof), 3))
                print("この値は、公開スコアの当たりを付ける手元の推定として使える。")
            """),
            markdown("""### 出力の読み方

このOOF F1と、実際に提出したときのスコア（LB）を比べます。**両者が近ければ**手元の検証は信頼でき、
改善の判断を手元だけで進められます。**大きく食い違えば**、分布ずれ（第6回のadversarial validation）や
リークを疑います。この差を**CV-LBギャップ**と呼びます。"""),
            markdown("""### 提出バリデータを「テスト」する

第2回で学んだ「テストで守る」を提出に適用します。検査関数を書くだけでなく、**わざと壊した提出**を
渡して、すべての`assert`がちゃんと弾くかを確かめます。関数が本当に機能する保証になります。"""),
            code("""
                def validate_submission(sub, test, expected=("sample_id", "active")):
                    "提出CSVの列・行数・ID一致・値域を検査する。問題があればAssertionError。"
                    expected = list(expected)
                    assert list(sub.columns) == expected, "列名または順序が違います"
                    assert len(sub) == len(test), "行数がtestと一致しません"
                    assert sub[expected[0]].is_unique, "IDが重複しています"
                    assert sub[expected[0]].tolist() == test[expected[0]].tolist(), "IDの順序がtestと一致しません"
                    assert sub[expected[1]].isin([0, 1]).all(), "予測値は0/1にしてください"
                    return "提出形式OK"

                print(validate_submission(submission, test))
                broken = submission.copy()
                broken.loc[broken.index[0], "active"] = 5
                try:
                    validate_submission(broken, test)
                except AssertionError as error:
                    print("異常を検出:", error)
            """),
            markdown("""### 出力の読み方

正しい提出は「提出形式OK」を返し、`active`に5を混ぜた壊れた提出は「異常を検出: 予測値は0/1に…」で
弾かれます。**弾かれることを確認して初めて**、検査関数は信頼できます。本番の提出前に必ず通す関数として
手元に残しておきましょう。"""),
        ],
        [
            markdown("""## APPENDIX（任意・追加演習）

提出づくりを効率化します。90分の外の自習向けです。まず**どんなモデルでも提出CSVを作る関数**を用意し、
複数モデルの提出を量産します。"""),
            code("""
                from sklearn.base import clone
                from sklearn.linear_model import LogisticRegression

                def make_submission(estimator, name):
                    "モデルを全trainで学習し、testを予測して提出CSVを保存する。"
                    est = clone(estimator).fit(train[features], train[target])
                    sub = pd.DataFrame({"sample_id": test["sample_id"], "active": est.predict(test[features])})
                    path = ROOT / "workspace" / f"submission_{name}.csv"
                    sub.to_csv(path, index=False)
                    print(f"{name}: 保存 {path.name}  陽性率={sub['active'].mean():.3f}")
                    return sub

                make_submission(model, "rf")
                _ = make_submission(Pipeline([("前処理", preprocess), ("モデル", LogisticRegression(max_iter=1000))]), "logit")
            """),
            markdown("""### 出力の読み方

2つの提出が`workspace/`に保存されます。**陽性率**（活性と予測した割合）がモデル間で大きく違うなら、
判定の癖が違うということ。`clone`で毎回まっさらなモデルから学習しているので、状態の混ざりがありません。"""),
            markdown("""### どの特徴量が効いているか（提出モデルの中身）

提出に使ったRandom Forestの特徴量重要度を、Pipelineの中から取り出します。One-Hot後の列名で表示されます。"""),
            code("""
                fitted = model.named_steps["モデル"]
                names = model.named_steps["前処理"].get_feature_names_out()
                imp = pd.DataFrame({"特徴量": names, "重要度": fitted.feature_importances_}).sort_values("重要度", ascending=False)
                display(imp.head(10).round(3))
            """),
            markdown("""### 出力の読み方

上位の特徴量が、モデルが判定に使っている主な手がかりです。第1・12回のとおり不純度重要度は偏りが
あるので、余裕があれば並べ替え重要度でも確認します。化学的に納得できる列が上位なら、ひとまず安心です。"""),
            markdown("""### OOFとholdout、2つの手元推定を比べる

提出せずに性能を見積もる方法は複数あります。**OOF**（第13回本編）と、単純な**holdout**（1回の取り置き）を
比べ、両者が近いかを確認します。近ければ手元の検証は安定しています。"""),
            code("""
                from sklearn.model_selection import cross_val_predict, train_test_split, StratifiedKFold
                from sklearn.metrics import f1_score

                oof = cross_val_predict(clone(model), train[features], train[target], cv=StratifiedKFold(5, shuffle=True, random_state=42))
                Xh_tr, Xh_va, yh_tr, yh_va = train_test_split(train[features], train[target], test_size=0.25, random_state=0, stratify=train[target])
                hold = clone(model).fit(Xh_tr, yh_tr)
                print("OOF F1     :", round(f1_score(train[target], oof), 3))
                print("holdout F1 :", round(f1_score(yh_va, hold.predict(Xh_va)), 3))
            """),
            markdown("""### 出力の読み方

2つが近ければ、手元の推定は信頼できます。OOFは全データを検証に使えるぶん安定しやすく、holdoutは
1回きりなので振れやすい。**複数の見積もりが一致するか**を確認する習慣が、コンペでも実務でも効きます。"""),
        ],
    )

    # ---- 第14回 ----
    write_notebook(
        "14-kaggle-improvement",
        notebook(
            "第14回：Kaggle改善会",
            "限られた時間で、次に何を試すか。",
            [
                markdown("""## 改善会：限られた時間で「次の一手」を選ぶ

ベースラインができたら、次は改善です。ただし時間は有限。**闇雲に試すのではなく、分担して1人1変更**を
検証し、良かったものだけを統合します。ここでも第12回の原則（1度に1つ、同じ条件、記録を残す）が効きます。

いちばん大事な心得：**手元の検証（ローカル）とLeaderboardの両方を見る**こと。Leaderboardだけを追うと、
公開スコアに過剰適合して最終順位を落とします。まず、答え合わせ用の`answers`も含めてデータを読みます。"""),
                code("""
                    import pandas as pd
                    train = pd.read_csv(DATA / "local_competition" / "train.csv")
                    test = pd.read_csv(DATA / "local_competition" / "test.csv")
                    answers = pd.read_csv(DATA / "local_competition" / "instructor_answers.csv")
                """),
                markdown("""## 5人の担当

1人1テーマに分かれます：**1. 欠損補完 / 2. 特徴量（最適温度からの距離）/ 3. モデルの深さ /
4. 判定閾値 / 5. 誤分類の確認**。全員が同じ`random_state=42`とF1を使い、**担当箇所以外は変えない**——
こうすると「誰の変更が効いたか」を後で切り分けられます。"""),
                markdown("""## 改善案を1つ組んで、ローカルで検証する

この例では2〜3の担当（特徴量追加＋浅い木＋`class_weight`）を1つの案にまとめています。第11回の
`temperature_distance`を足し、第8回の`class_weight="balanced"`で少数クラスを重視。まずローカル検証F1で
ベースラインと比べます。"""),
                code("""
                    from sklearn.model_selection import train_test_split
                    from sklearn.compose import ColumnTransformer
                    from sklearn.pipeline import Pipeline
                    from sklearn.impute import SimpleImputer
                    from sklearn.preprocessing import OneHotEncoder
                    from sklearn.ensemble import RandomForestClassifier
                    from sklearn.metrics import f1_score

                    improved_train = train.copy()
                    improved_test = test.copy()
                    for frame in [improved_train, improved_test]:
                        frame["temperature_distance"] = (frame["temperature_c"] - 78).abs()
                    target = "active"
                    # batch_id・experiment_dateは活性と無関係なID的な列なので特徴量から外す（第13回と同じ方針）
                    ignored = ["sample_id", "experiment_date", "batch_id", "smiles", target]
                    features = [c for c in improved_train.columns if c not in ignored]
                    numeric = improved_train[features].select_dtypes(include="number").columns.tolist()
                    categorical = [c for c in features if c not in numeric]
                    preprocess = ColumnTransformer([
                        ("数値", SimpleImputer(strategy="median"), numeric),
                        ("カテゴリ", Pipeline([("補完", SimpleImputer(strategy="most_frequent")), ("one_hot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), categorical),
                    ])
                    model = Pipeline([("前処理", preprocess), ("モデル", RandomForestClassifier(n_estimators=300, max_depth=3, class_weight="balanced", random_state=42))])
                    X_train, X_valid, y_train, y_valid = train_test_split(improved_train[features], improved_train[target], test_size=0.25, random_state=42, stratify=improved_train[target])
                    model.fit(X_train, y_train)
                    print("改善案のローカルF1:", round(f1_score(y_valid, model.predict(X_valid)), 3))
                """),
                markdown("""### 出力の読み方

このローカルF1を、第13回のベースライン（`submission_baseline`を作ったときの検証F1）と比べます。
**上がっていれば採用候補**。ただし1回の分割なので、余裕があれば交差検証（第10回）で確かめると確実です。"""),
                markdown("""## 模擬Leaderboardで答え合わせする

この教材では講師が`answers`（正解）を持っており、ローカルで「提出したつもり」の採点ができます。
全データで学習し直してtestを予測し、`answers`と突き合わせて**模擬Leaderboard F1**を出します。"""),
                code("""
                    model.fit(improved_train[features], improved_train[target])
                    improved_submission = pd.DataFrame({"sample_id": improved_test["sample_id"], "active": model.predict(improved_test[features])})
                    merged = answers.merge(improved_submission, on="sample_id", suffixes=("_true", "_pred"))
                    print("模擬Leaderboard F1:", round(f1_score(merged["active_true"], merged["active_pred"]), 3))
                """),
                markdown("""### 出力の読み方と実験ログ

- **ローカルF1と模擬LB F1が近い**なら、手元の検証は信頼できます。**大きく食い違う**なら、過剰適合や分布ずれを疑います。
- 改善しても悪化しても、`変更点 / ローカルF1 / 模擬LB F1 / 気づき`を1行で記録します。
- **Leaderboardだけ上がってローカルが下がった案は要注意**（公開スコアへの過剰適合の疑い）。良い変更だけを慎重に統合します。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：単体を超える3つの技

上位を狙うときの定番を3つ。**OOFスタッキング**（違うモデルを束ねる）、**分布ずれの点検**
（train/testが似ているか）、**シード平均**（乱数の偶然を薄める）です。いずれも第6・10回の応用です。"""),
            markdown("""### OOFスタッキング：違うモデルの予測を束ねる

第10回のスタッキングを、コンペ流に手作りします。3つのモデルの**OOF確率**（第13回）を作り、それらを
入力にした上位モデル（ロジスティック回帰）で統合します。OOFを使うのは、束ねる段階でリークしないためです。"""),
            code("""
                from sklearn.model_selection import cross_val_predict, StratifiedKFold
                from sklearn.pipeline import make_pipeline
                from sklearn.compose import ColumnTransformer
                from sklearn.impute import SimpleImputer
                from sklearn.preprocessing import OneHotEncoder
                from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
                from sklearn.linear_model import LogisticRegression
                from sklearn.metrics import f1_score

                pre = ColumnTransformer([
                    ("n", SimpleImputer(strategy="median"), numeric),
                    ("c", make_pipeline(SimpleImputer(strategy="most_frequent"), OneHotEncoder(handle_unknown="ignore", sparse_output=False)), categorical),
                ])
                members = {
                    "rf": make_pipeline(pre, RandomForestClassifier(n_estimators=300, max_depth=4, random_state=42)),
                    "hgb": make_pipeline(pre, HistGradientBoostingClassifier(max_iter=200, random_state=42)),
                    "logit": make_pipeline(pre, LogisticRegression(max_iter=1000)),
                }
                skf = StratifiedKFold(5, shuffle=True, random_state=42)
                oof = {}
                for name, est in members.items():
                    oof[name] = cross_val_predict(est, improved_train[features], improved_train[target], cv=skf, method="predict_proba")[:, 1]
                    print(f"{name:6s} OOF F1:", round(f1_score(improved_train[target], (oof[name] >= 0.5).astype(int)), 3))
                meta_X = pd.DataFrame(oof)
                stack_oof = cross_val_predict(LogisticRegression(max_iter=1000), meta_X, improved_train[target], cv=skf, method="predict_proba")[:, 1]
                print("スタッキング OOF F1:", round(f1_score(improved_train[target], (stack_oof >= 0.5).astype(int)), 3))
            """),
            markdown("""### 出力の読み方

各モデル単体のOOF F1と、スタッキングのOOF F1を比べます。**スタッキングが単体最良を上回れば**束ねた
価値あり。ほぼ同じなら、モデルたちが似た間違え方をしている（束ねる旨みが少ない）ということ。第10回と
同じ教訓：束ねは万能ではありません。"""),
            markdown("""### 分布ずれを点検する（adversarial validation）

第6回の手法をコンペに適用。trainとtestを見分ける分類器のAUCで、両者の分布の近さを測ります。
AUCが高ければ、ローカル検証がLeaderboardとずれる原因になります。"""),
            code("""
                from sklearn.model_selection import cross_val_score

                combined = pd.concat([
                    improved_train[numeric].assign(is_test=0),
                    improved_test[numeric].assign(is_test=1),
                ], ignore_index=True)
                adv = make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=200, random_state=42))
                auc = cross_val_score(adv, combined[numeric], combined["is_test"], cv=5, scoring="roc_auc")
                print("adversarial validation AUC:", round(auc.mean(), 3), "（0.5付近なら分布は近い）")
            """),
            markdown("""### 出力の読み方

AUCが0.5付近なら、train/testは似ていて手元CVは信頼できます。高ければ、CV-LBギャップの一因。実データの
コンペでは、AUCを上げている列を特定して扱いを見直す、といった対処につなげます。"""),
            markdown("""### シード平均：乱数の運を薄める

同じモデルでも`random_state`を変えると予測が少し変わります。複数シードの確率を平均すると、**乱数由来の
ばらつきが打ち消し合い**、安定した予測になります。少ない手間で効きやすい定番テクです。"""),
            code("""
                import numpy as np

                probs = []
                for seed in [0, 1, 2, 3, 4]:
                    est = make_pipeline(pre, RandomForestClassifier(n_estimators=300, max_depth=4, random_state=seed)).fit(improved_train[features], improved_train[target])
                    probs.append(est.predict_proba(improved_test[features])[:, 1])
                ensemble_pred = (np.mean(probs, axis=0) >= 0.5).astype(int)
                seed_merged = answers.merge(pd.DataFrame({"sample_id": improved_test["sample_id"], "active": ensemble_pred}), on="sample_id", suffixes=("_true", "_pred"))
                print("5シード平均の模擬LB F1:", round(f1_score(seed_merged["active_true"], seed_merged["active_pred"]), 3))
            """),
            markdown("""### 出力の読み方

5シード平均の模擬LB F1が、単一シードのときより**わずかに高く・安定**していれば成功。派手さは
ありませんが、こうした地味で確実な積み上げが、コンペでも実務でも効きます。「1回の高スコア」より
「**再現できる改善**」を選ぶ——これが今日いちばん持ち帰ってほしい姿勢です。"""),
        ],
        [
            markdown("""## APPENDIX（任意・追加演習）

改善の詰めを、OOFを使って安全に行います（すべて上のDEEP DIVEで作った`oof`を再利用）。90分の外の
自習向けです。まず**2モデルの重み付き平均（ブレンド）**の最適な重みを、OOF上で探します。"""),
            code("""
                import numpy as np
                from sklearn.metrics import f1_score

                y_true = improved_train[target]
                best = None
                for w in np.linspace(0, 1, 11):
                    blend = w * oof["rf"] + (1 - w) * oof["hgb"]
                    f1 = f1_score(y_true, (blend >= 0.5).astype(int))
                    if best is None or f1 > best[1]:
                        best = (round(w, 1), round(f1, 3))
                print(f"rf重み={best[0]} のときOOF F1最大={best[1]}")
            """),
            markdown("""### 出力の読み方

重み0はhgbのみ、1はrfのみ、途中が混合。**単体より混合が良い重み**が見つかれば、ブレンドの価値あり。
OOFで重みを決めるのは、テストに触れずに（リークなく）調整するためです。ただし重みを探しすぎると
OOFに過剰適合するので、探索は粗め（ここは11点）にとどめます。"""),
            markdown("""### 判定閾値もOOFで最適化する

第8回の閾値調整を、OOF確率に対して行います。0.5に固定せず、F1が最大になる閾値を手元で選びます。"""),
            code("""
                rows = []
                for t in np.linspace(0.2, 0.8, 13):
                    rows.append({"閾値": round(t, 2), "F1": f1_score(y_true, (oof["rf"] >= t).astype(int))})
                tbl = pd.DataFrame(rows)
                print("OOFでF1最大の閾値:", tbl.loc[tbl["F1"].idxmax(), "閾値"])
                tbl.round(3)
            """),
            markdown("""### 出力の読み方

F1が最大になる閾値が0.5とずれるなら、閾値調整で無料の改善が得られます。**OOFで選んだ閾値を、最終提出に
だけ適用**します（検証に使った同じデータで選んで報告しない、という第6・12回の原則を守ります）。"""),
            markdown("""### 誤分類を群別に分析する

どの化合物系列でよく間違えるかを、OOF予測で集計します。特定の系列に誤りが偏るなら、その系列を
表す特徴量の不足や、データ不足を疑います。次の改善仮説のきっかけになります。"""),
            code("""
                val = improved_train[["scaffold_group", target]].copy()
                val["oof_pred"] = (oof["rf"] >= 0.5).astype(int)
                val["誤り"] = val[target] != val["oof_pred"]
                by_group = val.groupby("scaffold_group").agg(件数=("誤り", "size"), 誤り数=("誤り", "sum"), 誤り率=("誤り", "mean"))
                display(by_group.sort_values("誤り率", ascending=False).round(3))
            """),
            markdown("""### 出力の読み方

誤り率の高い系列が、モデルの弱点。件数が十分あるのに誤り率が高い系列は、**その系列に効く特徴量を
足す**（第11回）か、**分割を系列単位にする**（第6回）といった次の一手につながります。エラー分析は、
闇雲なチューニングより効く改善のきっかけです。"""),
        ],
    )

    # ---- 第15回 ----
    write_notebook(
        "15-show-and-tell",
        notebook(
            "第15回：Show & Tellと自社データへの橋渡し",
            "自社データで始めるなら、最初の小さな一歩は何か。",
            [
                markdown("""## 最終回：成果を「伝え」、自社データへ「橋渡し」する

最後は、作ったものを人に伝え、次の一歩へつなぐ回です。データサイエンスは「良いモデルを作って終わり」
ではなく、**「使われて初めて価値になる」**。ここまで学んだことを、発表と持ち帰りの形にまとめます。

まず**再現性**の確認から。第14回のNotebookを`Kernel`→`Restart Kernel and Run All Cells`で頭から実行し、
同じ提出CSVができることを確かめます（第12回の再現性の実践）。次のセルは、発表で共有できる基本の数字を出します。"""),
                code("""
                    import pandas as pd
                    experiment_data = pd.read_csv(DATA / "compound_experiments.csv")
                    print("共有する候補")
                    print("データ件数:", len(experiment_data))
                    print("活性率:", round(experiment_data["active"].mean(), 3))
                    print("収率の中央値:", experiment_data["yield_pct"].median())
                """),
                markdown("""### 読みどころ

こうした基本統計（件数・活性率・中央値）は、発表の最初に置くと聞き手が状況をつかめます。**派手な
モデルより、まずデータの素性を1〜2行で言える**ことが、信頼される発表の土台です。"""),
                markdown("""## 1人5分のShow & Tell

次のうち1つを選んで共有します：**面白かった図 / 改善した実験 / 悪化したが学びがあった実験 /
Copilotへの良かった聞き方 / 自社テーマへ持ち帰りたい考え方**。

完成度は競いません。むしろ**「悪化したが学びがあった実験」**の共有が、チーム全体の学びになります
（うまくいかない筋を先に潰せる）。「1回の高スコア」より「再現できる気づき」を持ち寄ります。"""),
                markdown("""## 自社テーマ1枚シート

この教材の集大成として、自分のテーマを1枚に落とします。機密情報や実データは書かず、一般化した
表現で。**第5回の問題設定がここに戻ってきます**——予測時点と使えない情報を、もう一度自分の言葉で。

| 項目 | 記入内容 |
|---|---|
| 利用者と判断 | 誰が何を決めるか |
| 予測時点 | いつ予測するか |
| 目的変数 | 何を予測するか |
| 説明変数候補 | その時点で得られる情報 |
| 使えない情報 | 未来情報、測定後情報、機密上使えない情報 |
| 評価方法 | 指標と分割単位 |
| 単純な基準 | 平均、最頻値、現在の判断方法など |
| 最初の実験 | 1〜2週間で試せる小さな範囲 |

この1枚が、勉強会後に自社データで踏み出す**最初の一歩の設計図**になります。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：発表で終わらせない——再現・共有・安全な運用

発展として、実務で「モデルを渡す」ときに必要な3つを扱います。**永続化**（保存して再利用）、
**モデルカード**（使い方の説明書）、**適用領域**（予測してよい範囲）。どれも「モデルを安全に使ってもらう」
ための工夫です。"""),
            markdown("""### 永続化：学習済みモデルをファイルに保存する

毎回学習し直すのは非効率で、再現性も損なわれます。`joblib`で学習済みPipelineを**丸ごと保存**し、
読み直しても**同じ予測**になることを`assert`で確かめます。前処理も一緒に保存される点が重要です。"""),
            code("""
                import joblib
                import numpy as np
                import pandas as pd
                from sklearn.pipeline import make_pipeline
                from sklearn.impute import SimpleImputer
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.model_selection import train_test_split

                data = pd.read_csv(DATA / "compound_experiments.csv")
                feat = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
                X_tr, X_te, y_tr, y_te = train_test_split(data[feat], data["active"], test_size=0.25, random_state=42, stratify=data["active"])
                final = make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=200, max_depth=5, random_state=42)).fit(X_tr, y_tr)
                path = ROOT / "workspace" / "final_model.joblib"
                joblib.dump(final, path)
                reloaded = joblib.load(path)
                assert np.array_equal(final.predict(X_te), reloaded.predict(X_te)), "保存前後で予測が一致しません"
                print("保存し読み直しても同じ予測:", path)
            """),
            markdown("""### 読みどころ

`assert`が通り「同じ予測」と出れば、保存→配布→再利用の流れが安全に回ることの確認になります。
`Pipeline`ごと保存するので、**受け取った人は前処理を意識せず`predict`するだけ**。第9回でPipelineに
まとめた恩恵がここで効きます。"""),
            markdown("""### モデルカード：使い方の説明書を関数で作る

モデルは「精度の数字」だけ渡してもトラブルの元です。**誰向けか・何を決めるためか・限界・禁止事項**を
1枚にまとめた**モデルカード**を、関数で自動生成します。第5回の問題設定が、そのまま説明書になります。"""),
            code("""
                from sklearn.metrics import f1_score

                def build_model_card(name, estimator, X_valid, y_valid, notes) -> pd.DataFrame:
                    "モデルの用途と評価をまとめた1枚のカードを作る。"
                    pred = estimator.predict(X_valid)
                    items = {
                        "モデル名": name,
                        "検証F1": round(f1_score(y_valid, pred), 3),
                        "想定利用者": notes["利用者"],
                        "支援する判断": notes["判断"],
                        "既知の限界": notes["限界"],
                        "使ってはいけない条件": notes["禁止"],
                    }
                    return pd.DataFrame({"項目": list(items), "内容": list(items.values())})

                build_model_card("活性スクリーナ", reloaded, X_te, y_te, {
                    "利用者": "実験担当者", "判断": "追試する候補の優先順位",
                    "限界": "新規scaffoldでは精度低下の可能性", "禁止": "測定後の列を入力に使うこと",
                })
            """),
            markdown("""### 読みどころ

出来上がったカードには、性能（F1）と**使う上での注意**が並びます。特に「使ってはいけない条件（測定後の
列を入力にしない）」は、第5〜6回のリークの教訓そのもの。**精度より先に限界を書く**のが、信頼される
モデル提供者の作法です。"""),
            markdown("""### 適用領域：予測してよい範囲を数値化する

モデルは、学習データと似た試料には強いですが、かけ離れた試料では当てになりません。学習データからの
**近傍距離**を測り、遠すぎる（範囲外の）試料を「要確認」に自動で仕分けます。95%点を閾値にします。"""),
            code("""
                from sklearn.neighbors import NearestNeighbors
                from sklearn.preprocessing import StandardScaler

                train_filled = X_tr.fillna(X_tr.median())
                scaler = StandardScaler().fit(train_filled)
                nn = NearestNeighbors(n_neighbors=5).fit(scaler.transform(train_filled))
                train_dist = nn.kneighbors(scaler.transform(train_filled))[0].mean(axis=1)
                threshold = np.quantile(train_dist, 0.95)
                valid_dist = nn.kneighbors(scaler.transform(X_te.fillna(X_tr.median())))[0].mean(axis=1)
                out_of_domain = valid_dist > threshold
                print(f"適用領域外と判定された検証試料: {int(out_of_domain.sum())} / {len(valid_dist)} 件")
                print("範囲外は予測を鵜呑みにせず、要確認に回す運用が考えられる。")
            """),
            markdown("""### 読みどころ、そして全15回のまとめ

範囲外と判定された試料は、予測を鵜呑みにせず人が確認する——これが**安全にAIを使う**ということです。

全15回を貫いた芯は1つ：**「良いスコア」ではなく「意味のある予測」**。予測時点を決め、ベースラインと比べ、
リークを避け、正しく評価し、1つずつ改善を記録し、限界とともに伝える。この習慣こそが、皆さんが自社
データへ持ち帰るいちばんの財産です。お疲れさまでした。"""),
        ],
        [
            markdown("""## APPENDIX（任意・追加演習）

「渡せる成果物」を実際に書き出します。90分の外の自習向けです。まず**モデルカードをMarkdown＋JSONで
保存**し、第三者が読める形にします。"""),
            code("""
                import json

                card = build_model_card("活性スクリーナ", reloaded, X_te, y_te, {
                    "利用者": "実験担当者", "判断": "追試候補の優先順位",
                    "限界": "新規scaffoldで精度低下の可能性", "禁止": "測定後の列を入力に使うこと",
                })
                lines = ["# モデルカード", ""]
                for _, r in card.iterrows():
                    lines.append(f"- **{r['項目']}**: {r['内容']}")
                (ROOT / "workspace" / "model_card.md").write_text("\\n".join(lines), encoding="utf-8")

                meta = {"features": feat, "n_train": int(len(X_tr)), "model": "RandomForest(max_depth=5)"}
                (ROOT / "workspace" / "model_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
                print("保存: workspace/model_card.md, workspace/model_meta.json")
                print("\\n".join(lines))
            """),
            markdown("""### 出力の読み方

`model_card.md`は人が読む説明書、`model_meta.json`は機械が読む来歴（使った特徴量・学習件数・モデル種別）。
モデルと一緒にこの2つを残すと、**半年後の自分や引き継ぎ先が再現・判断できます**。"""),
            markdown("""### ドリフトを模擬する：入力がずれたら「監視」で気づけるか

運用後、測定装置のずれなどで入力分布が変わる（ドリフト）ことがあります。テストの温度を+20℃ずらし、
**正解ラベルが無くても異常に気づけるか**を確かめます。運用中は正解（活性の実測）がすぐには手に入らない
ため、F1のような指標は即座には測れません。だからこそ、正解なしで検知できる監視が重要になります。"""),
            code("""
                import numpy as np
                from sklearn.model_selection import cross_val_score
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.metrics import f1_score

                drift = X_te.copy()
                drift["temperature_c"] = drift["temperature_c"] + 20

                # (1) 正解が無くても分かる変化：予測の陽性率
                print(f"予測の陽性率: {reloaded.predict(X_te).mean():.3f} → {reloaded.predict(drift).mean():.3f}")

                # (2) 監視：元データとドリフト後を見分けられるか（adversarial validation, 第6回）
                cols = X_te.columns.tolist()
                combined = pd.concat([X_te.assign(is_drift=0), drift.assign(is_drift=1)], ignore_index=True)
                filled = combined[cols].fillna(combined[cols].median())
                auc = cross_val_score(RandomForestClassifier(n_estimators=200, random_state=42), filled, combined["is_drift"], cv=5, scoring="roc_auc").mean()
                print(f"監視AUC: {auc:.3f}（0.5=変化なし / 1.0に近い=明確な分布変化）")

                # 参考：正解が手に入ればF1でも確認できる（運用中は正解が遅れて届く）
                print(f"参考F1: {f1_score(y_te, reloaded.predict(X_te)):.3f} → {f1_score(y_te, reloaded.predict(drift)):.3f}")
            """),
            markdown("""### 出力の読み方

- **監視AUCが0.5をはっきり上回る**なら、元データとドリフト後をモデルが見分けられる＝入力分布が変化した、という警報です。温度を+20℃ずらしたので、AUCは0.5より明確に高く出るはずです（1に近いほど変化が大きい）。
- **予測の陽性率**の変化も、正解ラベル無しで「何かが変わった」と気づける手がかりです。
- 一方、**参考F1は運用中すぐには測れません**（正解が遅れて届くため）。しかもこのデータ・特徴量では変化が小さく、性能指標だけに頼ると見逃しかねません。だからこそ、正解なしで異常を検知するadversarial validation（第6回）のような監視が実務で効きます。"""),
            markdown("""### 成績表をファイルに書き出す

`classification_report`を表として保存します。発表資料や引き継ぎに添付できる、機械可読な成績表です。"""),
            code("""
                from sklearn.metrics import classification_report

                rep = classification_report(y_te, reloaded.predict(X_te), target_names=["非活性", "活性"], output_dict=True)
                rep_df = pd.DataFrame(rep).T.round(3)
                rep_df.to_csv(ROOT / "workspace" / "classification_report.csv")
                display(rep_df)
            """),
            markdown("""### 出力の読み方、そしてこの教材の終わりに

クラスごとのprecision/recall/F1と全体のaccuracyが表になり、CSVで保存されます。数字だけを渡すのではなく、
**モデルカード（用途と限界）＋メタ情報（来歴）＋成績表**をひとまとめに渡す——ここまでできれば、
「作って終わり」から「使ってもらえる」への橋を渡せています。全15回、おつかれさまでした。"""),
        ],
    )

    # ---- 任意：Kaggle Titanic ----
    write_named_notebook("05-ship-and-operate", "titanic_optional.ipynb", notebook(
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
            markdown("""## 提出後\n\nLeaderboardの点数だけで良し悪しを決めず、ローカル検証、変更点、結果を実験ログへ残します。Kaggle上の他者Notebookは、自分のベースラインを提出した後に読みます。"""),
        ],
    ))


def main() -> None:
    df = make_dataset()
    write_data(df)
    build_notebooks()        # 旧15回分をモジュールとして登録し、titanic_optionalも書き出す
    assemble_courses()       # 登録済みモジュールを5回のlesson.ipynbへ統合して書き出す
    print(f"generated: {len(df)} rows and {len(COURSE_GROUPS)} lesson notebooks")


if __name__ == "__main__":
    main()
