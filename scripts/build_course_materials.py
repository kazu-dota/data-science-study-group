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
            "推論：学習済みモデルを未知データへ使う処理",
            "並べ替え重要度：列を崩したときの性能低下で測る寄与",
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

            上から順に実行してください。`TRY`は全員、`CHANGE`は値を1つ変える練習、
            `CHALLENGE`は余裕がある人向けです。`DEEP DIVE`は経験者や自習向けの発展です。
            分からないコードは、セル全体ではなく気になる数行をM365 Copilotへ貼って相談します。
            """
        ).format(title=title, question=question)
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


def write_notebook(folder: str, content: dict, deep_dive_cells: list[dict]) -> None:
    meta = LESSON_META[folder]
    objectives = "\n".join(f"- {item}" for item in meta["objectives"])
    terms = "\n".join(f"- {item}" for item in meta["terms"])
    pitfalls = "\n".join(f"- {item}" for item in meta["pitfalls"])
    self_study = "\n".join(f"- {item}" for item in meta["self_study"])
    check = "\n".join(f"{index}. {item}" for index, item in enumerate(meta["check"], start=1))
    # 複数行の変数を差し込む前にテンプレートをdedentする（f-string内展開だとdedentが効かないため）。
    guide = markdown(
        dedent(
            """
            ## この回でできるようになること

            {objectives}

            ### 進み方

            `CORE`は同期90分で扱う本線、`DEEP DIVE`は時間があれば扱う深掘り、
            `SELF-STUDY`は任意自習です。すべて終わらなくても次回へ進めます。
            経験者は`CORE`を早めに終え、`DEEP DIVE`を5人で分担して読むと深まります。

            ### 先に押さえる言葉

            {terms}

            > **実行前の30秒予想**：今日の問いに、今の言葉で仮の答えを書いてから始めます。
            """
        ).format(objectives=objectives, terms=terms)
    )
    wrap_up = markdown(
        dedent(
            """
            ## よくある誤り

            {pitfalls}

            ## SELF-STUDY（任意・30〜60分）

            {self_study}

            成果は完成したコードでなくても、予想・変更点・出力・解釈を4行で残せば十分です。

            ## 振り返りチェック

            {check}

            答えに詰まった項目が、次に見返す場所です。暗記ではなくNotebookの該当セルを指せればOKです。
            """
        ).format(pitfalls=pitfalls, self_study=self_study, check=check)
    )
    content["cells"] = [
        content["cells"][0],
        content["cells"][1],
        guide,
        *content["cells"][2:],
        *deep_dive_cells,
        wrap_up,
    ]
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


FONT_SNIPPET = """
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
                common_load_cell(),
                markdown("""## まず完成済みモデルを動かす\n\n`X`は特徴量、`y`は目的変数です。単純なベースラインと比べ、モデルが本当に価値を出しているかを最初に確かめます。"""),
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
                markdown("""## TRY：1試料の予測を見る\n\n予測`0`は非活性、`1`は活性です。確率は確信度であり、真実そのものではありません。"""),
                code("""
                    one_sample = X_valid.iloc[[0]]
                    display(one_sample)
                    print("予測クラス:", model.predict(one_sample)[0])
                    print("活性である確率:", round(model.predict_proba(one_sample)[0, 1], 3))
                """),
                markdown("""## CORE深掘り：評価を関数に切り出す\n\n同じ評価を何度も書かず、型ヒントとassertで最小の検証を付けた関数にまとめます。"""),
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
                markdown("""## CHANGE\n\n`max_depth=4`を`2`や`8`へ変え、ベースラインとの差がどう動くか記録します。\n\n## ASK COPILOT\n\n`fit`と`predict_proba`の違いを、測定装置の校正と未知試料の測定にたとえて説明してもらいます。\n\n## まとめ\n\n- 特徴量はモデルへ渡す情報、目的変数は予測したい答え\n- 評価はベースラインと比べ、関数にまとめて再利用する"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：木の深さと汎化を交差検証で読む\n\n単一の検証スコアは分割運に左右されます。交差検証で学習F1と検証F1の差（過学習）を見ます。"""),
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
            markdown("""### 特徴量重要度は2種類を併読する\n\n不純度重要度は高カーディナリティ列へ偏ります。列を崩して性能低下を測る並べ替え重要度と一緒に読みます。"""),
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
            markdown("""## CHALLENGE：予測確率は当たっているか（較正）\n\n「確率0.8」の試料が本当に約80%活性かを、確率帯ごとの実際の活性率で確かめます。"""),
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
        ],
    )

    # ---- 第2回 ----
    write_notebook(
        "02-python-with-copilot",
        notebook(
            "第2回：Pythonを読み、Copilotと少し変える",
            "分からないコードを、どうやって小さく理解し、安全に書き換えるか。",
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
                        label = "高温条件" if temperature >= 75 else "低温条件"
                        print(temperature, label)
                """),
                markdown("""## 関数に型ヒントとdocstringを付ける\n\n引数と戻り値の型、目的を明示すると、読み手（と生成AI）が誤解しにくくなります。"""),
                code("""
                    def celsius_to_kelvin(celsius: float) -> float:
                        "摂氏をケルビンへ変換する。"
                        return celsius + 273.15

                    converted = [celsius_to_kelvin(value) for value in temperatures]
                    print(converted)
                    help(celsius_to_kelvin)
                """),
                markdown("""## TRY：エラーを省略せず読む\n\nエラー名とメッセージの末尾に、原因へ近い情報があります。"""),
                code("""
                    try:
                        temperatures[10]
                    except Exception as error:
                        print(type(error).__name__)
                        print(error)
                """),
                markdown("""## CHANGE\n\n`temperatures`へ温度を1つ追加し、表示と変換結果を確認します。\n\n## ASK COPILOT\n\n気になるセルを貼り、「各行の実行後に変数の型と中身がどうなるか表で説明して」と依頼します。提案は1つずつ試します。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：テストで守る小さなユーティリティ\n\n実行できることと、正しいことは別です。境界値・異常値を先に決め、防御的な関数を書きます。"""),
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
            markdown("""### assertで期待結果を先に固定する\n\nIQR法で外れ値を除く関数を書き、正常・空・NaN混在の3ケースを先に書いてから検証します。"""),
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
            markdown("""## CHALLENGE：関数の性質を調べる\n\n外れ値を除いた後もう一度適用すると、さらに減るでしょうか（冪等か）。四分位が動くため、必ずしも一致しません。"""),
            code("""
                rng = np.random.default_rng(0)
                sample = rng.normal(50, 5, 200).tolist()
                once = drop_outliers_iqr(sample)
                twice = drop_outliers_iqr(once)
                print("1回適用後の件数:", len(once))
                print("2回目でさらに減った件数:", len(once) - len(twice))
                print("2回目で変化なし(冪等):", once == twice)
            """),
        ],
    )

    # ---- 第3回 ----
    write_notebook(
        "03-pandas",
        notebook(
            "第3回：pandasで表データに触る",
            "初めて見る表データを受け取ったら、最初に何を見るか。",
            [
                common_load_cell(),
                markdown("""## TRY：最初の健康診断\n\n形・型・欠損・ユニーク数・要約統計を1度に確認します。"""),
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
                markdown("""## 行と列を選ぶ（locとquery）\n\n条件を文字列で書けるqueryは、複数条件を読みやすくします。"""),
                code("""
                    columns = ["sample_id", "solvent", "catalyst", "temperature_c", "yield_pct", "active"]
                    display(df.loc[:4, columns])
                    subset = df.query("catalyst == 'Cat-A' and temperature_c >= 80")[columns]
                    print("Cat-Aかつ80℃以上:", len(subset), "件")
                    subset.head()
                """),
                markdown("""## TRY：カテゴリごとに比べる\n\n平均だけでなく件数とばらつきも一緒に見ます。"""),
                code("""
                    solvent_summary = (
                        df.groupby("solvent", dropna=False)
                          .agg(件数=("sample_id", "size"), 平均収率=("yield_pct", "mean"),
                               収率SD=("yield_pct", "std"), 活性率=("active", "mean"))
                          .sort_values("平均収率", ascending=False)
                    )
                    solvent_summary.round(2)
                """),
                markdown("""## CHANGE\n\n`solvent`を`catalyst`や`scaffold_group`へ変えます。順位が変わる理由は、データだけから断定せず仮説として書きます。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：pivot_table・pipe・ベクトル化\n\n多軸の集計、処理をつなぐ書き方、速度の3点を扱います。"""),
            code("""
                pivot = pd.pivot_table(df, index="catalyst", columns="solvent", values="yield_pct", aggfunc=["count", "mean"])
                pivot.round(1)
            """),
            markdown("""### pipeで処理を関数としてつなぐ\n\n中間変数を増やさず、意図を関数名で表せます（元データは変更しない）。"""),
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
            markdown("""## CHALLENGE：applyとベクトル化の速度差\n\n行ごとのapplyは読みやすい反面、遅くなりがちです。同じ結果をベクトル化で書き、時間を比べます。"""),
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
        ],
    )

    # ---- 第4回 ----
    write_notebook(
        "04-eda",
        notebook(
            "第4回：データ探偵—分布・欠損・外れ値",
            "モデルを作る前に、データの怪しいところをどう見つけるか。",
            [
                common_load_cell(),
                font_cell("""
                    import seaborn as sns
                    sns.set_theme(style="whitegrid")
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
                markdown("""## CHANGE\n\n色分けを`catalyst`から`solvent`へ変えます。\n\n## 注意\n\n外れ値は入力ミスとは限りません。「誰に確認するか」「残す場合に何が起きるか」まで考えます。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：相関・相互情報量・欠損機構・多変量外れ値\n\n図の印象を、統計量と手法で裏づけます。"""),
            code("""
                numeric_cols = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa", "yield_pct"]
                correlation = df[numeric_cols].corr()
                plt.figure(figsize=(8, 5))
                sns.heatmap(correlation, annot=True, fmt=".2f", cmap="coolwarm", center=0)
                plt.title("数値列の相関（因果ではない）")
                plt.tight_layout()
            """),
            markdown("""### 相関では見えない関係を相互情報量で拾う\n\n温度は最適点で収率が最大になる山型のため、直線的な相関は弱くても相互情報量は大きく出ます。"""),
            code("""
                from sklearn.feature_selection import mutual_info_regression

                mi_source = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
                mi_frame = df[mi_source + ["yield_pct"]].dropna()
                mi = mutual_info_regression(mi_frame[mi_source], mi_frame["yield_pct"], random_state=42)
                pearson = mi_frame[mi_source].corrwith(mi_frame["yield_pct"]).abs()
                compare = pd.DataFrame({"相互情報量": mi, "|相関|": pearson.to_numpy()}, index=mi_source)
                compare.sort_values("相互情報量", ascending=False).round(3)
            """),
            markdown("""### 欠損の起こり方を疑う\n\n欠損率が他の列で偏るなら、ランダムでない欠損（MAR）を疑います。"""),
            code("""
                miss = df.assign(temp_missing=df["temperature_c"].isna())
                by_solvent = miss.groupby("solvent", dropna=False)["temp_missing"].mean().round(3)
                print("溶媒別の温度欠損率:")
                print(by_solvent)
                print("溶媒でほぼ一定ならMCARに近い。偏るならMARを疑う。")
            """),
            markdown("""### 多変量外れ値\n\n単変量では正常でも、組み合わせが異常な試料をIsolationForestで探します。"""),
            code("""
                from sklearn.ensemble import IsolationForest

                iso_cols = ["temperature_c", "reaction_time_h", "concentration_m", "yield_pct"]
                iso_data = df[iso_cols].fillna(df[iso_cols].median())
                flags = IsolationForest(contamination=0.03, random_state=42).fit_predict(iso_data)
                outliers = df.loc[flags == -1, ["sample_id", *iso_cols]]
                print("多変量外れ値候補:", len(outliers), "件")
                outliers.round(2)
            """),
        ],
    )

    # ---- 第5回 ----
    write_notebook(
        "05-problem-framing",
        notebook(
            "第5回：何を、いつ、何のために予測するか",
            "モデル構築より前に決めるべきことは何か。",
            [
                common_load_cell(),
                markdown("""## 予測問題を1文にする\n\n例：**実験条件を決める時点で使える情報から収率を予測し、優先して実施する条件を選ぶ。**\n\n`post_assay_signal`・`purity_pct`・`yield_pct`は実験後の値なので、この時点の説明変数にはできません。"""),
                code("""
                    available_at_planning = [
                        "scaffold_group", "solvent", "catalyst", "temperature_c", "reaction_time_h",
                        "concentration_m", "molecular_weight", "logp", "tpsa", "h_bond_donors", "rotatable_bonds",
                    ]
                    unavailable_at_planning = ["yield_pct", "active", "post_assay_signal", "purity_pct"]
                    print("計画時に使える列:", available_at_planning)
                    print("実験後に得られる列:", unavailable_at_planning)
                """),
                markdown("""## TRY：単純な予測を基準にする"""),
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
                markdown("""## CORE深掘り：リーク候補を自動で洗い出す\n\n目的変数と極端に相関する列は、測定後情報が紛れ込んでいないか疑います。監査を関数にしておくと、自社データでも使い回せます。"""),
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
                markdown("""## TRY：自分のテーマを整理する\n\n利用者・判断・予測時点・目的変数・使える列・使えない列・回帰/分類・単純基準の8点を1枚に書きます。\n\n## ASK COPILOT\n\n曖昧な点は推測で埋めず、確認質問として返すよう依頼します。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：コスト行列から最適な閾値を決める\n\n最適な閾値は指標ではなく、誤りのコストで決まります。見逃し（偽陰性）が高くつく状況を想定します。"""),
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
            markdown("""### 指標は意思決定から逆算する\n\n見逃しを避けたい探索段階ならrecall寄り、追試コストが高い絞り込み段階ならprecision寄り。「良いスコア」ではなく「どう使うか」で選びます。"""),
        ],
    )

    # ---- 第6回 ----
    write_notebook(
        "06-validation-leakage",
        notebook(
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
                    Xl_tr, Xl_va, yl_tr, yl_va = train_test_split(leaked[leak_features], leaked["active"], test_size=0.25, random_state=42, stratify=leaked["active"])
                    leaked_model = DecisionTreeClassifier(max_depth=3, random_state=42).fit(Xl_tr, yl_tr)
                    print("リーク列ありの検証スコア:", round(accuracy_score(yl_va, leaked_model.predict(Xl_va)), 3))
                    print("post_assay_signalは測定後の値。計画時の予測には使えません。")
                """),
                markdown("""## CORE深掘り：前処理は分割の内側で行う\n\n全データで標準化してから分割すると、検証情報が学習へ漏れます。Pipelineに入れると各分割の内側で学習されます。"""),
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
                markdown("""## CHALLENGE：化合物系列を跨がせない分割"""),
                code("""
                    splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
                    train_idx, valid_idx = next(splitter.split(clean, groups=clean["scaffold_group"]))
                    print("学習側の系列:", sorted(clean.iloc[train_idx]["scaffold_group"].unique()))
                    print("検証側の系列:", sorted(clean.iloc[valid_idx]["scaffold_group"].unique()))
                """),
            ],
        ),
        [
            markdown("""## DEEP DIVE：CV方式の比較・ネストCV・分布ずれ\n\n評価は「将来の使われ方」を模擬します。分割方式で楽観度がどう変わるかを見ます。"""),
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
            markdown("""### ネストCV：探索と評価を分ける\n\n同じ分割で設定を選び性能も報告すると過大評価します。内側で探索、外側で評価すると楽観が減ります。"""),
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
            markdown("""### adversarial validation：学習とテストは似ているか\n\n学習かテストかを当てる分類器のAUCが高いほど、分布がずれています。"""),
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
        ],
    )

    # ---- 第7回 ----
    write_notebook(
        "07-regression",
        notebook(
            "第7回：数値を予測する—回帰",
            "連続値の予測モデルを、何と比べ、不確かさをどう示すか。",
            [
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
                markdown("""## TRY：4モデルを交差検証で比べる\n\n1回の分割ではなく交差検証で、MAE・RMSE・R²を同時に読みます。"""),
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
                markdown("""## 予測と実測、残差を見る"""),
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
                code("""
                    errors = df.loc[y_valid.index, ["sample_id", "scaffold_group", "catalyst", "yield_pct"]].copy()
                    errors["予測"] = pred
                    errors["絶対誤差"] = (errors["yield_pct"] - errors["予測"]).abs()
                    errors.nlargest(8, "絶対誤差").round(2)
                """),
                markdown("""## CHANGE\n\n`max_depth=6`を`3`や`10`へ変え、MAEだけでなく残差図と大きく外した試料も比べます。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：学習曲線・群別残差・予測区間\n\nデータ不足か表現力不足か、そして点予測に不確かさをどう添えるかを扱います。"""),
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
            markdown("""### 群別に残差を見る\n\n全体のMAEが良くても、特定の化合物系列で系統的に外していることがあります。"""),
            code("""
                errors["残差"] = errors["yield_pct"] - errors["予測"]
                group_error = errors.groupby("scaffold_group").agg(件数=("残差", "size"), MAE=("絶対誤差", "mean"), 平均残差=("残差", "mean"))
                display(group_error.sort_values("MAE", ascending=False).round(2))
                print("平均残差が正なら、その系列を平均的に過小予測している。")
            """),
            markdown("""### 予測区間で不確かさを示す\n\n分位点回帰で10%と90%の予測を作り、実測がその区間に入る割合（被覆率）を確かめます。"""),
            code("""
                from sklearn.ensemble import HistGradientBoostingRegressor

                low = HistGradientBoostingRegressor(loss="quantile", quantile=0.1, max_iter=200, random_state=42).fit(X_train, y_train)
                high = HistGradientBoostingRegressor(loss="quantile", quantile=0.9, max_iter=200, random_state=42).fit(X_train, y_train)
                low_pred, high_pred = low.predict(X_valid), high.predict(X_valid)
                coverage = ((y_valid.to_numpy() >= low_pred) & (y_valid.to_numpy() <= high_pred)).mean()
                print(f"10-90%予測区間の実測被覆率: {coverage:.1%}（理想は約80%）")
                pd.DataFrame({"実測": y_valid.to_numpy()[:8], "下限": low_pred[:8].round(1), "上限": high_pred[:8].round(1)})
            """),
        ],
    )

    # ---- 第8回 ----
    write_notebook(
        "08-classification",
        notebook(
            "第8回：クラスを予測する—分類",
            "正解率だけで十分なのはどんなときか。",
            [
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
                    rows = []
                    for threshold in [0.3, 0.5, 0.7]:
                        pred = (probability >= threshold).astype(int)
                        rows.append({"閾値": threshold, "precision": precision_score(y_valid, pred), "recall": recall_score(y_valid, pred), "F1": f1_score(y_valid, pred)})
                    pd.DataFrame(rows).round(3)
                """),
                markdown("""## CORE深掘り：不均衡ではPR-AUCを見る\n\n陰性が多いデータではaccuracyが高く見えます。適合率-再現率曲線の面積（PR-AUC）が実態を映します。"""),
                code("""
                    from sklearn.metrics import average_precision_score
                    print("活性の割合:", round(df["active"].mean(), 3))
                    print("PR-AUC(平均適合率):", round(average_precision_score(y_valid, probability), 3))
                    print("常に多数派と予測したときのaccuracy:", round((y_valid == y_valid.mode()[0]).mean(), 3))
                """),
                markdown("""## 話し合い\n\n見逃したくない探索段階ならrecall、追試コストが高い絞り込み段階ならprecision。正解は利用場面で変わります。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：確率の較正・コスト最適閾値・不均衡対策\n\n確率をコスト計算へ使うなら、まず較正（予測確率と実頻度の一致）が前提です。"""),
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
            markdown("""### コスト行列で閾値を決める"""),
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
            markdown("""### class_weightで少数クラスを重くする"""),
            code("""
                for label, weight in {"weightなし": None, "balanced": "balanced"}.items():
                    clf = make_pipeline(SimpleImputer(strategy="median"), LogisticRegression(max_iter=1000, class_weight=weight)).fit(X_train, y_train)
                    pred = clf.predict(X_valid)
                    print(f"{label:10s} F1={f1_score(y_valid, pred):.3f}  recall={recall_score(y_valid, pred):.3f}")
            """),
        ],
    )

    # ---- 第9回 ----
    write_notebook(
        "09-preprocessing-pipeline",
        notebook(
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
                    model = Pipeline([("前処理", preprocess), ("予測", LogisticRegression(max_iter=1000))])
                    model.fit(X_train, y_train)
                    print(classification_report(y_valid, model.predict(X_valid), target_names=["非活性", "活性"]))
                """),
                markdown("""## 未知カテゴリでも予測できるか"""),
                code("""
                    unknown = X_valid.iloc[[0]].copy()
                    unknown["solvent"] = "New-Solvent"
                    print("未知カテゴリを含む予測:", model.predict(unknown)[0])
                """),
                markdown("""## CORE深掘り：変換後の列名と列数を確認する\n\nOne-Hotで列が増えます。`get_feature_names_out`で変換後の姿を見ます。"""),
                code("""
                    names = model.named_steps["前処理"].get_feature_names_out()
                    transformed = model.named_steps["前処理"].transform(X_train.head(3))
                    if hasattr(transformed, "toarray"):
                        transformed = transformed.toarray()
                    print("元の列数:", X_train.shape[1], "→ 変換後:", transformed.shape[1])
                    pd.DataFrame(transformed, columns=names, index=X_train.head(3).index).iloc[:, :10].round(2)
                """),
                markdown("""## CHANGE\n\n数値の欠損補完を`median`から`mean`へ変え、同じ検証データで比べます。変更はPipelineの1か所だけにします。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：自作変換器と前処理の探索\n\n意味のある特徴量を作る自作変換器を書き、前処理そのものをハイパーパラメータとして探索します。"""),
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
            markdown("""### 前処理の設定をGridSearchで選ぶ\n\n補完戦略のような前処理の選択も、交差検証で選べます。"""),
            code("""
                from sklearn.model_selection import GridSearchCV

                grid_pipe = Pipeline([("前処理", preprocess), ("予測", LogisticRegression(max_iter=1000))])
                param_grid = {"前処理__数値列__欠損補完__strategy": ["median", "mean"]}
                search = GridSearchCV(grid_pipe, param_grid, cv=5, scoring="f1")
                search.fit(X_train, y_train)
                print("最良設定:", search.best_params_)
                print("最良CV F1:", round(search.best_score_, 3))
            """),
        ],
    )

    # ---- 第10回 ----
    write_notebook(
        "10-model-comparison",
        notebook(
            "第10回：モデル対決",
            "複雑なモデルは本当にいつも優れているか。",
            [
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
                markdown("""## TRY：同じ分割・同じ指標で比較"""),
                code("""
                    rows = []
                    for name, model in models.items():
                        start = time.perf_counter()
                        model.fit(X_train, y_train)
                        elapsed = time.perf_counter() - start
                        rows.append({"モデル": name, "検証F1": f1_score(y_valid, model.predict(X_valid)), "学習秒": elapsed})
                    pd.DataFrame(rows).sort_values("検証F1", ascending=False).round({"検証F1": 3, "学習秒": 4})
                """),
                markdown("""## CORE深掘り：交差検証で安定性を見る\n\n1回の勝敗ではなく、平均・標準偏差・最低F1で安定性を比べます。"""),
                code("""
                    from sklearn.model_selection import StratifiedKFold, cross_val_score

                    cv = StratifiedKFold(5, shuffle=True, random_state=42)
                    stability = []
                    for name, estimator in models.items():
                        scores = cross_val_score(estimator, df[features], df["active"], cv=cv, scoring="f1")
                        stability.append({"モデル": name, "F1平均": scores.mean(), "F1標準偏差": scores.std(), "最低F1": scores.min()})
                    pd.DataFrame(stability).sort_values("F1平均", ascending=False).round(3)
                """),
                markdown("""## 5人の担当\n\nDummy / Logistic / Tree / Random Forest / Gradient Boosting を1人ずつ担当し、スコアだけでなく学習時間・説明しやすさ・安定性を1行で共有します。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：反復CVと検定・投票・スタッキング\n\n平均差が偶然かを検定で確かめ、複数モデルを束ねる価値を評価します。"""),
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
            markdown("""### 投票とスタッキングで束ねる\n\n間違え方が違うモデルを束ねると、単体より安定することがあります。"""),
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
            markdown("""### 任意：勾配ブースティング専用ライブラリ\n\nXGBoostが入っていれば試します。無ければsklearnのHistGradientBoostingで代用します。"""),
            code("""
                try:
                    from xgboost import XGBClassifier
                    xgb = XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.1, random_state=42, eval_metric="logloss")
                    scores = cross_val_score(xgb, df[features].fillna(df[features].median()), df["active"], cv=5, scoring="f1")
                    print("XGBoost F1平均:", round(scores.mean(), 3))
                except ImportError:
                    print("XGBoostは任意です（uv sync --extra advanced）。HistGradientBoostingで代用できます。")
            """),
        ],
    )

    # ---- 第11回 ----
    write_notebook(
        "11-feature-engineering",
        notebook(
            "第11回：化学の知識を特徴量にする",
            "研究者の知識を、モデルへ渡せる形にするにはどうするか。",
            [
                common_load_cell(),
                markdown("""## TRY：仮説を計算式にする\n\n最適温度78℃からの距離と、単位時間あたりの濃度という2つの仮説特徴量を作ります。"""),
                code("""
                    engineered = df.copy()
                    engineered["temperature_distance"] = (engineered["temperature_c"] - 78).abs()
                    engineered["concentration_per_hour"] = engineered["concentration_m"] / engineered["reaction_time_h"]
                    engineered[["temperature_c", "temperature_distance", "concentration_per_hour"]].head()
                """),
                markdown("""## 同じ検証条件でアブレーションする\n\n1回の分割ではなく交差検証で、追加前後のMAEを比べます。"""),
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
                markdown("""## CORE深掘り：相互情報量で特徴量を選ぶ\n\n目的変数との関連が強い列を選びます（非線形も拾えます）。"""),
                code("""
                    from sklearn.feature_selection import SelectKBest, mutual_info_regression

                    sel_data = engineered[added].fillna(engineered[added].median())
                    selector = SelectKBest(mutual_info_regression, k=4).fit(sel_data, engineered["yield_pct"])
                    pd.DataFrame({"特徴量": added, "MIスコア": selector.scores_, "選択": selector.get_support()}).sort_values("MIスコア", ascending=False).round(3)
                """),
                markdown("""## CHALLENGE：RDKitでSMILESから記述子を再計算"""),
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
            ],
        ),
        [
            markdown("""## DEEP DIVE：リーク安全なtarget encodingと特徴量選択\n\nカテゴリを目的変数の平均で置き換えるtarget encodingは、分割の外で計算するとリークします。"""),
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
            markdown("""### RFECVで特徴量を交差検証つきで絞る"""),
            code("""
                from sklearn.feature_selection import RFECV
                from sklearn.ensemble import RandomForestRegressor

                rfe_data = engineered[added].fillna(engineered[added].median())
                rfecv = RFECV(RandomForestRegressor(n_estimators=100, random_state=42), cv=5, scoring="neg_mean_absolute_error", min_features_to_select=2)
                rfecv.fit(rfe_data, engineered["yield_pct"])
                print("選ばれた特徴量数:", rfecv.n_features_)
                pd.DataFrame({"特徴量": added, "残す": rfecv.support_, "順位": rfecv.ranking_}).sort_values("順位")
            """),
        ],
    )

    # ---- 第12回 ----
    write_notebook(
        "12-experiment-cycle",
        notebook(
            "第12回：改善実験を小さく回す",
            "改善した理由を後から説明できる実験とは何か。",
            [
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
                markdown("""## TRY：1要素だけ変えて記録する"""),
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
                markdown("""## 実験ログの最小項目\n\n- 実験名 / 変えたもの（1つ） / 固定した比較条件 / 結果の平均とばらつき / 気づき / 次の仮説\n\nCopilotには案を出してもらい、優先順位と予測時点の妥当性は人が判断します。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：ランダム探索・ネストCV・重要度の区間\n\n手作業の総当たりではなく、探索と評価を分けて楽観の少ない推定を得ます。"""),
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
            code("""
                from sklearn.model_selection import cross_val_score

                outer = StratifiedKFold(5, shuffle=True, random_state=7)
                nested = cross_val_score(search, X, y, cv=outer, scoring="f1")
                print("ネストCV外側F1:", nested.round(3))
                print("楽観の少ない推定:", round(nested.mean(), 3), "±", round(nested.std(), 3), " ← 探索内スコアより低いのが普通")
            """),
            markdown("""### 並べ替え重要度は区間で読む\n\n平均だけでなくばらつきを見て、0を跨ぐ列は寄与があるとは言い切れません（評価はholdoutで行います）。"""),
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
        ],
    )

    # ---- 第13回 ----
    write_notebook(
        "13-kaggle-kickoff",
        notebook(
            "第13回：Kaggleに入って最初の提出を作る",
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
                markdown("""## コンペ説明\n\n- 目的：実験計画時の情報から活性`active`（0/1）を予測する\n- 指標：F1\n- `train.csv`には答えがあり、`test.csv`にはない\n- 提出列は`sample_id`と`active`\n\nKaggle Titanicを使える場合も、最初に同じ4点を確認します。"""),
                code("""
                    from sklearn.model_selection import train_test_split
                    from sklearn.compose import ColumnTransformer
                    from sklearn.pipeline import Pipeline
                    from sklearn.impute import SimpleImputer
                    from sklearn.preprocessing import OneHotEncoder
                    from sklearn.ensemble import RandomForestClassifier
                    from sklearn.metrics import f1_score

                    target = "active"
                    drop_columns = ["sample_id", "experiment_date", "smiles", target]
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
                markdown("""## TRY：提出CSVを作り、機械的に検査する"""),
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
                markdown("""## CHANGE\n\n提出前に変えるのは1点だけです。例：`max_depth=6`を`3`へ変え、ローカル検証がどう変わるか確認します。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：OOF予測と提出バリデータ\n\n交差検証の検証側だけを集めたOOF予測は、手元でLeaderboardに近い推定を与えます。"""),
            code("""
                from sklearn.model_selection import cross_val_predict, StratifiedKFold
                from sklearn.metrics import f1_score

                oof = cross_val_predict(model, train[features], train[target], cv=StratifiedKFold(5, shuffle=True, random_state=42))
                print("OOF F1:", round(f1_score(train[target], oof), 3))
                print("この値は、公開スコアの当たりを付ける手元の推定として使える。")
            """),
            markdown("""### 提出を検査する関数をテストする\n\n異常な提出を渡して、すべてのassertが本当に働くかを確かめます。"""),
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
        ],
    )

    # ---- 第14回 ----
    write_notebook(
        "14-kaggle-improvement",
        notebook(
            "第14回：Kaggle改善会",
            "限られた時間で、次に何を試すか。",
            [
                code("""
                    import pandas as pd
                    train = pd.read_csv(DATA / "local_competition" / "train.csv")
                    test = pd.read_csv(DATA / "local_competition" / "test.csv")
                    answers = pd.read_csv(DATA / "local_competition" / "instructor_answers.csv")
                """),
                markdown("""## 5人の担当\n\n1. 欠損補完 / 2. 特徴量（最適温度からの距離） / 3. モデルの深さ / 4. 判定閾値 / 5. 誤分類の確認\n\n全員が同じ`random_state=42`とF1を使い、担当箇所以外は変えません。"""),
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
                    ignored = ["sample_id", "experiment_date", "smiles", target]
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
                code("""
                    model.fit(improved_train[features], improved_train[target])
                    improved_submission = pd.DataFrame({"sample_id": improved_test["sample_id"], "active": model.predict(improved_test[features])})
                    merged = answers.merge(improved_submission, on="sample_id", suffixes=("_true", "_pred"))
                    print("模擬Leaderboard F1:", round(f1_score(merged["active_true"], merged["active_pred"]), 3))
                """),
                markdown("""## 実験ログ\n\n改善しても悪化しても、`変更点 / ローカルF1 / 模擬Leaderboard F1 / 気づき`を1行で記録します。Leaderboardだけ改善し、ローカル検証が悪化した案は慎重に扱います。"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：OOFスタッキング・分布ずれ・シード平均\n\n単体を超えるには、間違え方の違うモデルをOOFで束ね、分布ずれと偶然を点検します。"""),
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
            markdown("""### 分布ずれを点検する"""),
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
            markdown("""### シード平均で偶然を薄める"""),
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
        ],
    )

    # ---- 第15回 ----
    write_notebook(
        "15-show-and-tell",
        notebook(
            "第15回：Show & Tellと自社データへの橋渡し",
            "自社データで始めるなら、最初の小さな一歩は何か。",
            [
                markdown("""## 最初から再実行できるか\n\n第14回Notebookを`Kernel`→`Restart Kernel and Run All Cells`で実行し、提出CSVが同じ手順で作れることを確認します。"""),
                code("""
                    import pandas as pd
                    experiment_data = pd.read_csv(DATA / "compound_experiments.csv")
                    print("共有する候補")
                    print("データ件数:", len(experiment_data))
                    print("活性率:", round(experiment_data["active"].mean(), 3))
                    print("収率の中央値:", experiment_data["yield_pct"].median())
                """),
                markdown("""## 1人5分のShow & Tell\n\n面白かった図 / 改善した実験 / 悪化したが学びがあった実験 / Copilotへの良かった聞き方 / 自社テーマへ持ち帰りたい考え方 のうち1つを選びます。完成度は競いません。"""),
                markdown("""## 自社テーマ1枚シート\n\n機密情報や実データは書かず、一般化した表現で埋めます。\n\n| 項目 | 記入内容 |\n|---|---|\n| 利用者と判断 | 誰が何を決めるか |\n| 予測時点 | いつ予測するか |\n| 目的変数 | 何を予測するか |\n| 説明変数候補 | その時点で得られる情報 |\n| 使えない情報 | 未来情報、測定後情報、機密上使えない情報 |\n| 評価方法 | 指標と分割単位 |\n| 単純な基準 | 平均、最頻値、現在の判断方法など |\n| 最初の実験 | 1〜2週間で試せる小さな範囲 |"""),
            ],
        ),
        [
            markdown("""## DEEP DIVE：モデルの永続化・モデルカード・適用領域\n\n発表で終わらせず、再現・共有・安全な運用まで一歩進めます。"""),
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
            markdown("""### モデルカードを関数で作る"""),
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
            markdown("""### 適用領域：予測してよい範囲を数値化する\n\n学習データから遠い試料は、予測を鵜呑みにせず要確認に回します。近傍距離で範囲外を仕分けます。"""),
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
        ],
    )

    # ---- 任意：Kaggle Titanic ----
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
            markdown("""## 提出後\n\nLeaderboardの点数だけで良し悪しを決めず、ローカル検証、変更点、結果を実験ログへ残します。Kaggle上の他者Notebookは、自分のベースラインを提出した後に読みます。"""),
        ],
    ))


def main() -> None:
    df = make_dataset()
    write_data(df)
    build_notebooks()
    print(f"generated: {len(df)} rows and 15 notebooks")


if __name__ == "__main__":
    main()
