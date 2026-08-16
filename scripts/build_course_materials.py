"""合成データと全5回のNotebookを再生成する。

公開可能な架空データだけを使い、乱数シードを固定して再現性を保つ。
各回は初学者向けの基本と、希望者向けの発展内容に分け、
コーディングとモデル評価を段階的に扱う。
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
            "Python環境（仮想環境）がなぜプロジェクトごとに分かれているかを説明できる",
            "uvが何をしているか、Condaとの違いを含めて説明できる",
            "Gitの基本用語（リポジトリ・コミット・クローン・プル・プッシュ・ブランチ）を説明できる",
        ],
        "terms": [
            "仮想環境：プロジェクトごとにPythonとライブラリ一式を分けて用意する場所",
            "uv：仮想環境の作成とライブラリのインストールを行うツール",
            "pyproject.toml／uv.lock：使うライブラリとバージョンを記録するファイル",
            "リポジトリ：ファイルと変更履歴をまとめて保存する場所",
            "コミット：ここまでの変更に名前を付けて記録する操作",
        ],
        "reading": [
            "sys.executableで今動いているPythonの場所を確認できる",
            "同じuv.lockを使えば、誰のPCでも同じバージョンのライブラリが入る",
            "Gitの操作は任意で、この勉強会はZIPダウンロードだけで完結する",
        ],
        "pitfalls": [
            "カーネルの選択で別のPythonを選んでしまう",
            "uvとCondaを同じもの・同じ目的だと思い込む",
            "Gitを使わないと勉強会に参加できないと思い込む",
        ],
        "self_study": [
            "pyproject.tomlとuv.lockを開き、どのライブラリがどのバージョンで固定されているか3つ挙げる",
            "docs/environment-and-git-basics.mdを読み、Gitのclone/pullを実際に試す",
        ],
        "check": [
            "仮想環境を分ける理由は何か",
            "uvとCondaの違いは何か",
            "コミットとプッシュはそれぞれ何をする操作か",
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
            "AUCとLoglossの違いを説明し、使い分けられる",
            "確率の較正（calibration）を信頼度図と指標で評価する",
            "不均衡データへclass_weightや閾値調整で対処し、効果を検証する",
        ],
        "terms": [
            "precision：陽性予測のうち正しかった割合",
            "recall：実際の陽性を見つけた割合",
            "PR-AUC：適合率-再現率曲線の下側面積",
            "Logloss：確率の自信度まで含めて誤りを罰する評価指標",
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
            "投票・スタッキングで複数モデルを組み合わせ、単体との差を評価する",
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
            "モデルの組み合わせは、元のモデルの間違え方が異なるときに効果が出やすい",
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
    "11a-feature-creation": {
        "objectives": [
            "既存の列から比・差・合計などの特徴量を作り、交差検証でアブレーションする",
            "化学分野の特徴量（SMILES由来のRDKit記述子）を、意味のある計算値として読む",
            "特徴量は予測時点で計算できる必要がある、という制約を常に確認する",
        ],
        "terms": [
            "特徴量設計：既存情報から予測に役立つ表現を作ること",
            "アブレーション：要素を足し引きして寄与を調べる比較",
            "RDKit記述子：分子構造（SMILES）から計算する分子量・LogP等の値",
            "相互情報量：非線形も捉える、特徴量と目的変数の関連の強さ",
            "適用領域：モデルが信頼できる入力範囲",
        ],
        "reading": [
            "特徴量は予測時点で計算できる必要がある",
            "追加前後で分割やモデルの条件を揃えて比較する",
            "化学記述子も「測定値の一種」として、意味を確認してから使う",
        ],
        "pitfalls": [
            "意味を説明できない特徴量を大量追加する",
            "追加前後で分割やモデルも変える",
            "RDKitが無いと動かない前提でコードを書く",
        ],
        "self_study": [
            "比・差以外の組み合わせ特徴量を1つ作り、MAEの変化を記録する",
            "RDKit記述子を使う場合と計算済み記述子表を使う場合で結果を比べる",
        ],
        "check": [
            "その特徴量はいつ計算できるか",
            "アブレーションとは何を確かめる操作か",
            "RDKit記述子はどんな情報から計算されるか",
        ],
    },
    "11b-feature-selection": {
        "objectives": [
            "リークを避けたtarget encodingを、分割の内側で自作する",
            "相互情報量・RFECVで特徴量を選び、適用領域の限界を意識する",
            "並べ替え重要度で、作った特徴量が実際に効いているかを検証する",
        ],
        "terms": [
            "target encoding：カテゴリを目的変数の集約値で置き換える手法",
            "RFECV：交差検証つきで再帰的に特徴量を削る選択法",
            "並べ替え重要度：列を崩したときの性能低下で測る寄与",
            "OOF（out-of-fold）：交差検証の検証側だけを集めた予測・値",
            "適用領域：モデルが信頼できる入力範囲",
        ],
        "reading": [
            "target encodingは分割の外で計算するとリークする",
            "選択も評価も同じ分割の内側で行う",
            "重要度が0付近（ばらつきより小さい）なら効いているとは言い切れない",
        ],
        "pitfalls": [
            "目的変数由来の値を全データで作って特徴量にする",
            "特徴量選択を分割の外側で行う",
            "重要度の高さだけで採用可否を決め、意味を確認しない",
        ],
        "self_study": [
            "自作KFold target encodingの有無でMAEを比較する",
            "RFECVで残った特徴量と、化学的な解釈を突き合わせる",
        ],
        "check": [
            "target encodingでリークを防ぐ手順は何か",
            "特徴量選択も交差検証の内側で行う理由は何か",
            "並べ替え重要度が0付近の特徴量をどう扱うか",
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
    "16-neural-networks": {
        "objectives": [
            "scikit-learnのMLP（ニューラルネットワーク）を、既存のRandomForest/勾配ブースティングと同条件で比較する",
            "小規模な表データでニューラルネットワークが必ずしも勝たない理由を説明できる",
            "ニューラルネットワークが得意な場面（大量データ・画像/テキスト等）を挙げられる",
        ],
        "terms": [
            "ニューラルネットワーク：入力を層状につないだ関数で表現を学習するモデル",
            "MLP（多層パーセプトロン）：全結合層を重ねた最も基本的なニューラルネットワーク",
            "隠れ層：入力と出力の間にある中間の層",
            "過剰パラメータ：データ量に対してモデルの自由度が大きすぎる状態",
            "早期終了：検証スコアの悪化を見て学習を止める工夫",
        ],
        "reading": [
            "表データ・少量データでは木系モデルが安定して強いことが多い",
            "ニューラルネットワークは特徴量設計を省ける代わりに大量データを要する",
            "複雑なモデルを使う前に、単純なモデルとの差を確認する",
        ],
        "pitfalls": [
            "複雑なモデル＝高性能だと思い込む",
            "スケーリングなしで数値特徴量をそのままMLPへ渡す",
            "少量データでも層を増やせば良くなると考える",
        ],
        "self_study": [
            "隠れ層のユニット数を変え、検証スコアと学習時間の変化を記録する",
            "MLPが木系モデルに負けた理由を、データ件数の観点から1文で書く",
        ],
        "check": [
            "MLPとRandomForestは何が違うか",
            "このデータでMLPが必ず勝つとは限らない理由は何か",
            "ニューラルネットワークが有利になりやすい条件は何か",
        ],
    },
    "17-transfer-learning": {
        "objectives": [
            "転移学習が何をする手法かを、事前学習とファインチューニングの言葉で説明できる",
            "この教材のデータで転移学習を使いにくい理由を説明できる",
            "化学・創薬分野で転移学習が使われている実例を1つ以上挙げられる",
        ],
        "terms": [
            "事前学習：大量データで先にモデルを学習しておく段階",
            "ファインチューニング：事前学習済みモデルを手元のデータで追加学習すること",
            "分子表現学習：分子構造を数値ベクトルとして学習する事前学習の一種",
            "事前学習済みモデル：既に大規模データで学習済みの公開モデル",
        ],
        "reading": [
            "転移学習は事前学習と手元データの領域が近いほど効果が出やすい",
            "420行の表データだけでは、転移学習のための事前学習が現実的でない",
            "画像・テキスト・分子構造など、大規模な事前学習済みモデルがある領域で使われやすい",
        ],
        "pitfalls": [
            "転移学習を使えば少ないデータでも必ず精度が上がると考える",
            "事前学習の対象領域と手元データの領域が遠いのに流用する",
            "コードを書かずに概念だけで「使ったつもり」になる",
        ],
        "self_study": [
            "自分の業務データに近い分野で、事前学習済みモデルが公開されていないか調べる",
            "分子表現学習モデルの論文・紹介記事を1つ読み、要点を3行で書く",
        ],
        "check": [
            "事前学習とファインチューニングの関係は何か",
            "このデータで転移学習が使いにくい理由は何か",
            "化学・創薬分野での転移学習の実例を1つ挙げられるか",
        ],
    },
    "15-show-and-tell": {
        "objectives": [
            "学習済みPipelineをjoblibで保存し、推論用の関数として使えるようにする",
            "運用後に監視すべき項目（入力ドリフト・予測傾向・性能・適用領域）を挙げる",
            "再学習のトリガーと、入れ替え前に必要な比較の手順を説明する",
        ],
        "terms": [
            "永続化：学習済みモデルをファイルへ保存すること",
            "サービング：保存済みモデルを使って予測を返す仕組み",
            "ドリフト：運用後に入力や関係が変わること",
            "監視：運用後の入力や性能変化を確認すること",
            "再学習：新しいデータを足してモデルを学習し直すこと",
        ],
        "reading": [
            "Pipelineごと保存すれば、前処理を含めて復元できる",
            "正解ラベルが無くても入力ドリフトは検知できる",
            "再学習後は、同じ検証・同じ評価で旧モデルと比較してから入れ替える",
        ],
        "pitfalls": [
            "モデル単体だけ保存し、前処理を保存し忘れる",
            "運用後に何も監視せず放置する",
            "再学習したモデルを、比較せずにそのまま入れ替える",
        ],
        "self_study": [
            "保存したPipelineを読み直し、同じ入力で同じ予測になるか検証する",
            "適用領域スコアを閾値化し、範囲外の試料を要確認として仕分ける",
        ],
        "check": [
            "永続化で何を一緒に保存すべきか",
            "運用後に監視すべき指標は何か",
            "再学習後、入れ替え前に何を確認すべきか",
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

            `演習`は全員、`変更して確認`は値を1つ変える練習、`自由課題（任意）`は余裕がある人向けです。
            `発展（任意）`・`追加演習`は経験者や自習向けの発展で、飛ばしても本編は完結します。
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
        "folder": "01-prepare-and-explore",
        "title": "第1回：データ分析の準備",
        "overview": "Python環境・uv・Gitの基礎を知り、Pythonとpandasの基本操作を身につけ、データの分布・欠損・外れ値を確認します。",
        "members": ["01-kickoff", "02-python-with-copilot", "03-pandas", "04-eda"],
    },
    {
        "folder": "02-build-models",
        "title": "第2回：予測モデルを作成",
        "overview": "何を・いつ予測するかを決めてデータリークを見抜き、回帰・分類のモデルを作り、様々なモデルの特徴を知ります。",
        "members": ["05-problem-framing", "07-regression", "10-model-comparison"],
    },
    {
        "folder": "03-evaluate-models",
        "title": "第3回：モデルの評価方法",
        "overview": "学習・検証・テストを正しく分けて過学習を見抜き、回帰・分類それぞれの評価指標（Logloss・AUCの違いを含む）を使い分け、評価結果を比較・改善の判断へつなげます。",
        "members": ["06-validation-leakage", "08-classification", "12-experiment-cycle"],
    },
    {
        "folder": "04-feature-engineering",
        "title": "第4回：特徴量エンジニアリングの紹介",
        "overview": "前処理をPipelineへ安全にまとめ、化学知識から特徴量を作り、作った特徴量を安全に選びます。",
        "members": ["09-preprocessing-pipeline", "11a-feature-creation", "11b-feature-selection"],
    },
    {
        "folder": "05-advanced-and-operate",
        "title": "第5回：転移学習・再学習・ニューラルネットワークモデルの紹介",
        "overview": "ニューラルネットワークを既存モデルと同条件で比較し、転移学習の考え方と限界を知り、モデルを運用・監視・再学習するところまで見据えます。",
        "members": ["16-neural-networks", "17-transfer-learning", "15-show-and-tell"],
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
    part_count = len(group["members"])
    return markdown(
        dedent(
            """
            # {title}

            この回は{part_count}つのパートで構成します：**{subs}**。

            **セルの動かし方**：各セル（灰色の枠）を選んで `Shift + Enter`（またはセル左の▷ボタン）を押すと実行できます。
            **上から順に**実行してください。前のセルを飛ばすと、後のセルでエラーになります。

            **AIと一緒に進める**：分からないコードは、セル全体ではなく気になる数行をM365 CopilotなどのAIへ貼り、
            説明や修正を相談します。ただし、提案されたコードは必ず実行結果を見て確かめます。

            まず「基本」と「演習」を進めます。「補足」は必要に応じて読み、
            「発展（任意）」「追加演習（任意）」「自由課題（任意）」は飛ばしても構いません。
            """
        ).format(title=group["title"], subs=subs, part_count=part_count)
    )


def merged_guide(group: dict) -> dict:
    part_count = len(group["members"])
    return markdown(
        dedent(
            """
            ## この回で扱うこと

            {overview}

            ### 進め方

            この回は{part_count}つのパートに分かれています。パート1から順に「基本」と「演習」を進めてください。
            1日で終える必要はありません。「発展（任意）」と「追加演習（任意）」は、余裕がある場合だけ取り組みます。

            ### 用語について

            初めて出る用語は、その用語を使うセルで説明します。ここでまとめて暗記する必要はありません。

            > **実行前の30秒予想**：各パートの問いに、今の言葉で仮の答えを書いてから始めます。
            """
        ).format(overview=group["overview"], part_count=part_count)
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

            ## 自習（任意・30〜60分）

            {self_study}

            成果は完成したコードでなくても、予想・変更点・出力・解釈を4行で残せば十分です。

            ## 振り返りチェック

            {check}

            答えに詰まった項目が、次に見返す場所です。暗記ではなくNotebookの該当セルを指せればOKです。
            """
        ).format(pitfalls=pit_md, self_study=ss_md, check=ck_md)
    )


def assemble_courses() -> None:
    for group in COURSE_GROUPS:
        cells = [merged_intro(group), setup_cell(), merged_guide(group)]
        for index, member in enumerate(group["members"], start=1):
            module = MODULES[member]
            cells.append(chapter_heading(index, member))
            cells.extend(module["core"])
            cells.extend(module["deep_dive"])
            cells.extend(module["appendix"])
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
    # ---- 第1回パート1 ----
    write_notebook(
        "01-kickoff",
        notebook(
            "第1回パート1：Python環境とuv、Gitの基礎",
            "自分のパソコンで、なぜ同じPythonの環境を再現できるのか。",
            [
                markdown("""## 「環境」とは何か

Pythonを使うプロジェクトでは、プロジェクトごとに「使うPythonのバージョン」や「入れておく
ライブラリの種類・バージョン」が違います。あるプロジェクトはpandas 2.0を使い、別のプロジェクトは
pandas 1.5でないと動かない、ということも起こります。

そこで、プロジェクトごとにPythonとライブラリ一式を**別の場所に分けて用意**し、混ざらないようにします。
この「分けて用意した場所」を**仮想環境**と呼びます。この勉強会でいう`.venv`フォルダが、
この教材専用の仮想環境です。準備セルは、その仮想環境の中にあるPythonを実際に動かしています。"""),
                markdown("""## 今、動いているPythonを確認する

`sys.executable`で、今のセルを実行しているPython本体がどこにあるかを確認できます。"""),
                code("""
                    import sys
                    print("実行中のPython:", sys.executable)
                    print("バージョン:", sys.version.split()[0])
                """),
                markdown("""### 出力の読み方

`...\\.venv\\Scripts\\python.exe`のように、勉強会フォルダの中の`.venv`を指していれば、正しい環境で
実行できています。VS Codeでカーネルを選ぶ操作は、「どの`python.exe`でこのNotebookを動かすか」を
選んでいる、というのがここでの確認でつながります。"""),
                markdown("""## なぜuvを使うのか

`uv`は、仮想環境の作成と、必要なライブラリのインストールを両方行うツールです。この勉強会での
役割は次の2つです。

- `uv sync`：`pyproject.toml`と`uv.lock`を読み、`.venv`を作って必要なライブラリを入れる
- `uv run ...`：その`.venv`の中でコマンドを実行する（`uv run jupyter lab`など）

データサイエンス分野では、`uv`の他に**Conda**（Anaconda/Miniconda）もよく使われます。どちらも
「環境を分けて再現する」ためのツールですが、得意分野が少し違います。"""),
                markdown("""| | uv | Conda |
|---|---|---|
| 主な対象 | Pythonのライブラリ | Python本体を含む、非Pythonのソフトウェアも扱える |
| 得意な場面 | 純粋なPythonプロジェクトを、速く・軽く構築する | RDKitのように、C/Fortranなどで書かれた部分を含む科学技術系ライブラリを扱う |
| この勉強会での位置づけ | 標準環境として採用 | 未使用（第4回のRDKitは`uv sync --extra chemistry`で導入） |

どちらが優れているというより、**プロジェクトの性質に合わせて選ぶもの**です。この勉強会は
構築のしやすさを優先して`uv`を選びましたが、「仮想環境を分けて再現する」という考え方自体は
どちらも同じです。"""),
                markdown("""## 演習：ライブラリのバージョンを確認する

`pyproject.toml`と`uv.lock`には、使うライブラリのバージョンが記録されています。
`importlib.metadata`で、今の環境に実際に入っているバージョンを確認しましょう。"""),
                code("""
                    from importlib.metadata import version

                    for library in ["pandas", "scikit-learn", "matplotlib"]:
                        print(f"{library}: {version(library)}")
                """),
                markdown("""### 出力の読み方

ここに出たバージョンは、`uv.lock`に固定された、**この勉強会の全員が同じ値になる**バージョンです。
別の人のパソコンで同じセルを実行しても、同じ数字が出るはずです。これが「環境を再現する」の意味です。"""),
                markdown("""## Gitとは何か（概念紹介）

Gitは、ファイルの変更履歴を記録し、後から見返したり元に戻したりできるようにする
**バージョン管理システム**です。この勉強会のリポジトリ自体もGitで管理され、GitHub上で公開されています。

ただし、この勉強会に**Gitの操作は必須ではありません**。ZIPダウンロードだけで最後まで完結します。
ここでは、用語だけ知っておきましょう。

- **リポジトリ（repository）**：ファイルとその変更履歴をまとめて保存する場所
- **コミット（commit）**：「ここまでの変更」に名前（メッセージ）を付けて記録する操作
- **クローン（clone）**：リポジトリを丸ごと自分のPCへコピーすること（ZIPダウンロードに近いが、履歴も含めてコピーされ、後から`pull`で更新できる）
- **プル（pull）**：リポジトリの最新の変更を、自分のPCへ取り込むこと
- **プッシュ（push）**：自分のPCで行った変更を、リポジトリ側へ反映すること
- **ブランチ（branch）**：同じリポジトリの中で、複数の変更を並行して進めるための分岐"""),
                markdown("""## 演習：ターミナルでuvのバージョンを確認する

このNotebookの外、VS Codeの**ターミナル**で次を実行してみましょう（このセルではなく、ターミナルで実行します）。

```powershell
uv --version
```

バージョン番号が表示されれば、`uv`が正しくインストールされています。Gitを実際に試してみたい人は、
[Python環境とGitの基礎（任意）](../../docs/environment-and-git-basics.md)の手順でclone/pullを体験できます。"""),
                markdown("""## まとめ

- プロジェクトごとに**仮想環境**を分けることで、ライブラリのバージョン衝突を避けられる。
- `uv`は仮想環境の作成とライブラリのインストールを行うツール。Condaは非Pythonの依存も扱える点が違う。
- `uv.lock`があるおかげで、**誰のパソコンでも同じバージョン**が再現される。
- Gitは変更履歴を管理する仕組みだが、この勉強会では必須ではない。"""),
            ],
        ),
        [
            markdown("""## 発展（任意）：Gitでの共同作業の考え方

ここからは、Gitをチームで使う場面をもう少し詳しく知りたい人向けの発展です。実際に手を動かす
必要はありません。"""),
            markdown("""### ブランチとPull Request

複数人が同じリポジトリを同時に変更すると、作業がぶつかります。そこで、それぞれが**ブランチ**という
分岐を作り、自分の変更をそこで進めます。

作業が終わったら、**Pull Request（PR）**という形で「このブランチの変更を、本流（`main`）へ
取り込んでほしい」と提案します。他の人がレビューし、問題なければ**マージ（merge）**して統合します。
この「分岐して、レビューして、統合する」流れが、Gitがチーム開発で広く使われる理由です。"""),
            markdown("""### リモートとローカル

自分のPC上のリポジトリを**ローカル**、GitHub上のリポジトリを**リモート**と呼びます。`clone`は
リモートをローカルへコピーする操作、`pull`はリモートの最新をローカルへ取り込む操作、`push`は
ローカルの変更をリモートへ反映する操作です。この勉強会のように「読むだけ」であれば`clone`と`pull`
だけで足り、`push`（自分の変更を反映する操作）は使いません。"""),
        ],
        [
            markdown("""## 追加演習（任意）

ここから先は90分では扱いません。手を動かして深めたい人向けの追加コードです。飛ばして次回へ進んでも
問題ありません。"""),
            markdown("""### pyproject.tomlの中身を実際に読む

`pyproject.toml`は、このプロジェクトが使うライブラリを宣言するファイルです。テキストファイルなので、
Pythonからそのまま読めます。"""),
            code("""
                pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
                print(pyproject_text[:600])
            """),
            markdown("""### 出力の読み方

`dependencies = [...]`のあたりに、`pandas`や`scikit-learn`などのライブラリ名とバージョン条件が
並んでいるはずです。`uv sync`は、このファイルと`uv.lock`を読んで`.venv`を組み立てています。"""),
            markdown("""### インストール済みライブラリの数を数える

`importlib.metadata`で、今の仮想環境に入っている全ライブラリの数も数えられます。"""),
            code("""
                from importlib.metadata import distributions

                installed = sorted(d.metadata["Name"] for d in distributions())
                print(f"インストール済み: {len(installed)}個")
                print(installed[:10])
            """),
            markdown("""### 出力の読み方

直接使っているライブラリ（pandasなど）だけでなく、それが依存する別のライブラリも一緒に
インストールされているため、見た目より多い数になります。`uv.lock`は、この**全部の組み合わせ**を
固定しているファイルです。"""),
        ],
    )

    # ---- 第1回パート2 ----
    write_notebook(
        "02-python-with-copilot",
        notebook(
            "第1回パート2：Pythonを読み、Copilotと少し変える",
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
                markdown("""## 演習：`for`（繰り返し）と`if`（条件分岐）を読む

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
                markdown("""## 演習：エラーは「読む」もの。省略せず全文を見る

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
                markdown("""## 変更して確認

`temperatures`へ温度を1つ追加し、`for`ループと変換結果の表示がどう変わるか確認します。

## Copilotへの相談

気になるセルを貼り、「各行の実行後に、変数の型と中身がどう変わるか表で説明して」と依頼します。
提案は1つずつ試し、必ず出力で答え合わせをします。"""),
            ],
        ),
        [
            markdown("""## 発展（任意）：テストで守る小さなユーティリティ

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
            markdown("""## 自由課題（任意）：関数の「性質」を調べる

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
            markdown("""## 追加演習（任意）

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

第1回パート3で本格的に使うpandasを、ひと足先に少しだけ触ります。CSVを読み、1列（Series）の平均や
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
`.dropna()`は欠損を除く指定。ここまで来れば、第1回パート3のpandasはぐっと読みやすくなります。"""),
        ],
    )

    # ---- 第1回パート3 ----
    write_notebook(
        "03-pandas",
        notebook(
            "第1回パート3：pandasで表データに触る",
            "初めて見る表データを受け取ったら、最初に何を見るか。",
            [
                markdown("""## pandasは「表を操る道具」

pandasは、Excelのような表（DataFrame）をPythonで扱うライブラリです。研究データの多くは表なので、
これが読めると分析の8割は前に進みます。この回で身につけるのは、初見の表に対して**同じ手順で
最初の点検をする**習慣です。

初見データを受け取ったら、まず次の4つを見ます：**大きさ（行数×列数）／型（数値か文字か）／
欠損（空欄はどこか）／ばらつき（平均や範囲）**。"""),
                common_load_cell(),
                markdown("""## 演習：表の「健康診断」を1度に行う

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
                markdown("""## 演習：カテゴリごとにまとめて比べる（groupby）

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
                markdown("""## 変更して確認

`groupby("solvent")`を`"catalyst"`や`"scaffold_group"`へ変えて、順位がどう変わるか見ます。
順位が変わる理由は、**データだけから断定せず仮説として**書き留めます（第4〜5回でその検証を学びます）。"""),
            ],
        ),
        [
            markdown("""## 発展（任意）：多軸集計・処理の連結・速度

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
            markdown("""## 自由課題（任意）：`apply`と「ベクトル化」の速度差

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
            markdown("""## 追加演習（任意）

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
時系列の分割（第2回パート3）にもつながる大事な操作です。"""),
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

- **merge後**：各試料に「触媒平均収率」列が付き、「平均との差」で相対評価ができます。この「群平均を特徴量にする」発想は第4回パート2のtarget encodingにつながります（ただしリークに注意）。
- **melt後**：3列だった記述子が「記述子・値」の2列に畳まれ、行数が増えます。可視化ライブラリはこの縦長形式を好むことが多いです。"""),
        ],
    )

    # ---- 第2回パート1 ----
    write_notebook(
        "04-eda",
        notebook(
            "第2回パート1：分布・欠損・外れ値を確認する",
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
                markdown("""## 演習：1変数の分布を見る（ヒストグラムと箱ひげ図）

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

- **左（温度×収率）**：右肩上がりの直線ではなく、**中くらいの温度で収率が高くなる山型**に見えるはずです。「関係＝直線」とは限らないことを、目で確認しておきます（第2回パート1の発展で扱う相互情報量につながります）。
- 点の色（触媒）で**かたまり**ができていれば、触媒が収率に効いている手がかり。
- **右（触媒別の箱ひげ）**：触媒ごとに箱の高さ（収率の中心）が違えば、触媒の効果が疑われます。ただし件数が少ない触媒は割り引いて読みます。"""),
                markdown("""## 演習：欠損と「明らかに怪しい値」を表で押さえる

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
                markdown("""## 変更して確認

散布図の色分け（`hue`）を`catalyst`から`solvent`へ変え、見え方の違いを1つ挙げます。

## 注意

外れ値＝入力ミス、ではありません。本物の珍しい現象のこともあります。EDAの結論は「削除」ではなく、
**「確認すべき仮説」**の形で残します。"""),
            ],
        ),
        [
            markdown("""## 発展（任意）：印象を統計量で裏づける

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
            markdown("""## 追加演習（任意）

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
- **右**：収率との|相関|が高い列が、回帰（yield）で効く候補。ただし第2回パート1で確認したとおり、相関が低くても相互情報量が高い列（温度など）を見落とさないよう、相関の棒だけで判断しないこと。
- ここで挙がった候補列が、第2回パート2以降の特徴量選びの出発点になります。"""),
        ],
    )

    # ---- 第2回パート2 ----
    write_notebook(
        "05-problem-framing",
        notebook(
            "第2回パート2：何を、いつ、何のために予測するか",
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
                markdown("""## 演習：まず「単純な基準（ベースライン）」を作る

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
- **多数派だけの正解率**が高く出ることに驚くかもしれません。活性が少ないデータでは「全部を多数派と答える」だけで正解率が高くなります。**だから正解率は当てにならない**。第3回パート2でF1を学ぶ動機になります。
- 本命モデルは、この2つの数字を**はっきり上回って初めて価値がある**と考えます。
- なお`Dummy`は答え(`y`)だけを見て予測するため、ここで渡している`molecular_weight`列の中身は使いません（形式的な引数です）。"""),
                markdown("""## 補足：リーク候補を自動で洗い出す

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

- `active`との|相関|が高い順に並びます。`post_assay_signal`が上位に来るはず。これは**活性測定後の値**なので、計画時には存在せず、使えばリークです。
- ただしこの監査は**あくまで補助**。相関が低くてもリークする列（例：実験日から結果を推測できる場合）もあります。最終判断は「その値がいつ確定するか」で人が行います。
- `threshold`はリーク候補とみなす相関の閾値。厳しく見たいなら下げます。"""),
                markdown("""## 演習：自分のテーマを1枚に整理する

次の8点を、機密を書かずに埋めます。**利用者／判断／予測時点／目的変数／使える列／使えない列／
回帰か分類か／単純な基準**。埋まらない項目があれば、それが今いちばん詰めるべき点です。

## Copilotへの相談

Copilotには、曖昧な項目を勝手に埋めさせず「確認すべき質問」の形で返すよう頼みます。"""),
            ],
        ),
        [
            markdown("""## 発展（任意）：最適な閾値は「コスト」で決まる

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
            markdown("""## 追加演習（任意）

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
- 分類の`most_frequent`は正解率が高く見えますが、これは第3回パート2で学ぶ「不均衡の罠」。`stratified`/`uniform`はランダムに近い基準です。
- 本命モデルは、**これらのうち最も手強い基準**を超えて初めて価値があります。"""),
            markdown("""### 予測時点チェックを関数にする

第2回パート2で確認した「使える列／使えない列」を、候補リストから自動で仕分ける関数にします。自社データでも
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
確率×利益からコストを引いて、プラスなら試す。第2回パート2・第3回パート2のコスト最適閾値の考え方の土台です。"""),
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

    # ---- 第2回パート3 ----
    write_notebook(
        "06-validation-leakage",
        notebook(
            "第2回パート3：モデルは本当に当たっているか",
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
                markdown("""## 演習：木を深くすると「過学習」が見える

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

- `max_depth=None`（無制限）では**学習スコアが1.0近く**まで上がるのに、**検証スコアはそれほど伸びない**。典型的な過学習です。
- 検証スコアが最も高い深さの手前あたりが「ちょうど良い複雑さ」。「学習スコアの高さ」を実力だと勘違いしないことが、ここでの分かれ目です。
- 教訓：**必ず「未知データ役（検証）」で評価する**。学習データでの高得点は実力ではありません。"""),
                markdown("""## 演習：リーク列を入れると「不自然に」良くなる

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

リーク列を入れた検証スコアは、リークなしのときより**明らかに高い**はずです。**「スコアが急に良くなったら喜ぶ前に疑う」**。高すぎるスコアはリークの最初のサインです。第2回パート2のリーク監査と合わせて習慣にします。"""),
                markdown("""## 補足：前処理も「分割の内側」で行う

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
原理的に楽観へ偏ります。`Pipeline`にまとめれば、分割ごとに前処理を学習し直すので安全。だから第3回パート3で
`Pipeline`を本格的に学びます。"""),
                markdown("""## 自由課題（任意）：似た試料を「両側に入れない」分割

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
                markdown("""## 補足：学習・検証・テストの3つに分ける

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
            markdown("""## 発展（任意）：分割方式で「楽観度」はこんなに変わる

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
            markdown("""## 追加演習（任意）

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

    # ---- 第3回パート1 ----
    write_notebook(
        "07-regression",
        notebook(
            "第3回パート1：数値を予測する—回帰",
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
                markdown("""## 演習：4モデルを交差検証で、3つの指標で比べる

回帰の代表的な指標を先に押さえます。

- **MAE（平均絶対誤差）**：平均で何%外すか。単位が収率と同じで**いちばん直感的**。
- **RMSE**：大きな外れを二乗で重く見る。「たまの大外し」を嫌う場面向け。
- **R²（決定係数）**：平均値予測と比べてどれだけ説明できたか（1に近いほど良い、0は平均値並み）。

`neg_...`はsklearnの都合で「大きいほど良い」に符号反転された指標名。表示時に`-`で元へ戻します。
（scikit-learnの`scoring`は「大きいほど良い」に統一されているため、誤差系の指標は符号が反転しています。）

コード中の`make_pipeline(SimpleImputer(...), モデル)`は、**欠損補完とモデルを1つにまとめて「1個のモデル」の
ように扱う**ための道具です。こうすると`fit`/`predict`や交差検証がまとめて安全に回せます。仕組みは第3回パート3で
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
足りない可能性（第4回パート2の特徴量設計の動機）。ばらばらなら、単なるノイズかもしれません。

## 変更して確認

`max_depth=6`を`3`や`10`へ変え、MAEの表・残差図・大外し試料が**どう連動して動くか**を観察します。"""),
            ],
        ),
        [
            markdown("""## 発展（任意）：伸び悩みの原因と、予測の不確かさ

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
            markdown("""## 追加演習（任意）

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

次数2で、温度の山型（第2回パート1）を線形モデルが表せるようになり、MAEが下がることが多いはず。ただし次数3で
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

温度の曲線が**山型**（中ほどで予測収率が最大）になっていれば、モデルは第2回パート1で見た構造を学べています。
部分依存プロットは、ブラックボックスに見える木モデルの「考え方」を説明する強力な道具で、
研究者への説明資料としても有効です。"""),
        ],
    )

    # ---- 第3回パート2 ----
    write_notebook(
        "08-classification",
        notebook(
            "第3回パート2：クラスを予測する—分類",
            "正解率だけで十分なのはどんなときか。",
            [
                markdown("""## 「正解率」だけ見ると、なぜ危ないのか

第2回パート2で「多数派と答えるだけで正解率が高くなる」ことを見ました。この回はその続きで、
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
                markdown("""## 演習：閾値0.5で混同行列と3指標を読む

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
                markdown("""## 演習：判定の「閾値」を動かしてみる

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
- **見逃しを避けたい場面は閾値を下げ、空振りを避けたい場面は上げる**。閾値はモデルの外側で、目的に合わせて選ぶダイヤルです（第2回パート2のコスト最適閾値につながります）。"""),
                markdown("""## 補足：不均衡データではPR-AUCを見る

「閾値をいくつにするか」を決める前に、モデルの**確率の質そのもの**を1つの数字で測りたい。不均衡データ
（活性が少ない）では、ROC-AUCよりも**PR-AUC（適合率-再現率曲線の面積）**の方が実態を映します。"""),
                code("""
                    from sklearn.metrics import average_precision_score
                    print("活性の割合:", round(df["active"].mean(), 3))
                    print("PR-AUC(平均適合率):", round(average_precision_score(y_valid, probability), 3))
                    print("常に多数派と予測したときのaccuracy:", round((y_valid == y_valid.mode()[0]).mean(), 3))
                """),
                markdown("""### 出力の読み方

- 「活性の割合」が小さいのに「多数派予測のaccuracy」が高い。**accuracyの水増し**を数字で確認できます。
- **PR-AUC**は「活性の割合」を基準線とし、それを大きく上回るほど、モデルが活性をうまく上位に並べていると読めます。閾値を決めずにモデルの良さを比べたいときの主指標です。"""),
                markdown("""## 話し合い

「見逃し（FN）と空振り（FP）の、どちらがこのテーマでは高くつくか？」を5人で言葉にします。
探索段階なら見逃しを嫌ってrecall寄り、確証段階なら空振りを嫌ってprecision寄り。**正解は場面で変わります。**"""),
            ],
        ),
        [
            markdown("""## 発展（任意）：確率を「信じてよいか」と、不均衡対策

確率をコストの計算（第2回パート2）に使うなら、その確率が**較正**されている。「0.8と言ったら本当に約80%」で
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
            markdown("""### AUCとLoglossの違い

ここまで使ってきたPR-AUC・ROC-AUCは、確率の**順位**だけを見ています（「活性の確率が高い順に
正しく並んでいるか」）。実際の確率の値そのもの（0.51なのか0.99なのか）は問いません。

一方**Logloss（対数損失）**は、確信度まで含めて誤りを罰する指標です。正解から離れた確率を
自信満々で出すほど、罰則が大きくなります。较正されていない確率は、AUCでは分からずLoglossで
初めて悪さが見える、ということが起こります。"""),
            code("""
                from sklearn.metrics import roc_auc_score, log_loss

                for name, clf in {"未較正": base_clf, "較正後": cal_clf}.items():
                    p = clf.predict_proba(X_valid)[:, 1]
                    auc = roc_auc_score(y_valid, p)
                    logloss = log_loss(y_valid, p)
                    print(f"{name}: AUC={auc:.3f}（高いほど良い）  Logloss={logloss:.3f}（低いほど良い）")
            """),
            markdown("""### 出力の読み方

- **AUC**は較正の前後でほとんど変わらないはずです。较正は確率の順位を変えないため、
  順位だけを見るAUCには効果が反映されません。
- **Logloss**は較正後に下がる（改善する）ことが多いです。確信度が実態に近づいたことが、
  Loglossには反映されます。
- まとめると、**ランキング（誰から試すか）を評価したいならAUC、確率の値そのものを意思決定に
  使うならLogloss**、という使い分けになります。"""),
            markdown("""### コスト行列で閾値を決める（較正済み確率で）

第2回パート2と同じ考え方を、較正した確率に適用します。見逃し(FN)が空振り(FP)の8倍高いとして、期待コストが
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
            markdown("""## 追加演習（任意）

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

    # ---- 第3回パート3 ----
    write_notebook(
        "09-preprocessing-pipeline",
        notebook(
            "第3回パート3：前処理をPipelineにまとめる",
            "数値列とカテゴリ列を、安全に同じモデルへ入れるにはどうするか。",
            [
                markdown("""## なぜ「Pipeline」が必要なのか

これまで欠損を`fillna`で埋めたり、数値だけを使ったりしてきました。実データでは**数値列と
カテゴリ列（文字）が混在**し、それぞれ別の下ごしらえが要ります。

- 数値列 → 欠損を埋める＋尺度を揃える（標準化）
- カテゴリ列 → 欠損を埋める＋数値へ変換（One-Hot：各カテゴリを0/1の列にする）

これらを手作業でやると、**第2回パート3で学んだ前処理リーク**（検証情報の漏れ）を起こしがちです。そこで
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
                markdown("""## 演習：列ごとの前処理を組み立てて、モデルまで繋ぐ

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

- **活性クラスの行**を重点的に見ます（少数派で難しいため）。第3回パート2で学んだとおり、accuracyより各クラスのrecall/precisionが実態を映します。
- 大事なのは点数そのものより、**文字列カテゴリを含む表をエラーなく1つのモデルへ通せた**こと。手作業のOne-Hotより安全で短いです。

補足：ここでは`scaffold_group`（化合物系列）もカテゴリ列の例として入れていますが、第2回パート3のとおり本来は
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
                markdown("""## 補足：変換後は列が増える。その姿を見る

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

## 変更して確認

数値の欠損補完を`median`から`mean`へ変え、成績を比べます。変更は`SimpleImputer(strategy=...)`の**1か所だけ**。Pipelineだと変更点が1か所に集約され、実験が管理しやすくなります。"""),
            ],
        ),
        [
            markdown("""## 発展（任意）：自作の前処理を作り、前処理も探索対象にする

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
第4回パート2の特徴量設計をリークなく行えます。"""),
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
            markdown("""## 追加演習（任意）

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
保存されるので、配布先は`predict`するだけです（第5回パート3の永続化の先取り）。"""),
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

    # ---- 第4回パート1 ----
    write_notebook(
        "10-model-comparison",
        notebook(
            "第4回パート1：複数のモデルを同じ条件で比較する",
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
                markdown("""## 演習：同じ土俵で、F1と学習時間を並べる

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
                markdown("""## 補足：交差検証で「安定して強いか」を見る

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
- 1回の分割（前セル）と順位が入れ替わることもあります。だから**単発の勝敗で決めない**。これがこの回の教訓です。"""),
                markdown("""## 5人の担当

Dummy / Logistic / Tree / Random Forest / Gradient Boosting を1人ずつ担当し、
**スコア・学習時間・説明しやすさ・安定性**を1行で共有します。「どれが最強か」ではなく
「**この用途にはどれが妥当か**」を言葉にすることが到達目標です。"""),
            ],
        ),
        [
            markdown("""## 発展（任意）：性能差とモデルを組み合わせる効果を確認する

上位2モデルのF1差が0.01だったとして、それは本物の差でしょうか、それとも分割運でしょうか。
ここでは**反復交差検証＋統計的検定**で差の確からしさを測り、次に複数モデルを組み合わせたときの効果を確認します。"""),
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
            markdown("""### 投票・スタッキングで組み合わせる

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

組み合わせたモデルが最良単体を**明確に上回るとは限りません**。効果が出やすいのは、元のモデルたちが
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
            markdown("""## 追加演習（任意）

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
違う（第3回パート2）ので、多面的に見て選びます。"""),
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

    # ---- 第4回パート2 ----
    write_notebook(
        "11a-feature-creation",
        notebook(
            "第4回パート2：特徴量を作る",
            "研究者の知識を、モデルへ渡せる形にするにはどうするか。",
            [
                markdown("""## 特徴量設計＝あなたの化学知識をモデルへ渡す

モデルは与えられた列しか見ません。**「最適温度から離れるほど収率が落ちる」**という知識を持っていても、
`temperature_c`の生の値だけでは、モデルがその山型を学ぶのは大変です。そこで、知識を**計算式**にして
新しい列（特徴量）として渡します。これが特徴量設計です。

鉄則が2つあります。
1. **予測時点で計算できること**（第2回パート2。実験後の値から作らない）。
2. **追加の効果は、同じ検証条件で前後比較して確かめる**（思い込みで良し悪しを決めない）。"""),
                common_load_cell(),
                markdown("""## 演習：仮説を計算式にする

2つの仮説を式にします。**「最適温度78℃からの距離」**（離れるほど収率減、という山型を直接表す）と、
**「単位時間あたりの濃度」**（濃度と時間の兼ね合い）。どちらも計画時に計算できる値です。"""),
                code("""
                    engineered = df.copy()
                    engineered["temperature_distance"] = (engineered["temperature_c"] - 78).abs()
                    engineered["concentration_per_hour"] = engineered["concentration_m"] / engineered["reaction_time_h"]
                    engineered[["temperature_c", "temperature_distance", "concentration_per_hour"]].head()
                """),
                markdown("""### 読みどころ

`temperature_distance`は、78℃から上下どちらに離れても大きくなる値（絶対値）。第2回パート1で見た「温度と収率の
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
- 効かない・悪化することもあります。それも立派な結果。**「この仮説はこのモデルには効かなかった」**と分かるのが検証の価値です。悪化した実験も記録します（第4回パート3）。"""),
                markdown("""## 補足：関連の強い特徴量を選ぶ（相互情報量）

特徴量が増えると、効かない列がノイズになることも。**相互情報量（第2回パート1）**で目的変数との関連が強い順に
並べ、上位k個を選びます。相関と違い、山型のような非線形の関連も拾えます。"""),
                code("""
                    from functools import partial
                    from sklearn.feature_selection import SelectKBest, mutual_info_regression

                    # random_stateを固定しないとMIの推定値は実行ごとに変わる（第2回パート1と同じ作法）
                    mi_score = partial(mutual_info_regression, random_state=42)
                    sel_data = engineered[added].fillna(engineered[added].median())
                    selector = SelectKBest(mi_score, k=4).fit(sel_data, engineered["yield_pct"])
                    pd.DataFrame({"特徴量": added, "MIスコア": selector.scores_, "選択": selector.get_support()}).sort_values("MIスコア", ascending=False).round(3)
                """),
                markdown("""### 出力の読み方（結果は素直に受け止める）

MIスコアの高い順に並び、上位4つに「選択=True」が付きます。ここで大事なのは、**自作の`temperature_distance`が
必ず上位に来るとは限らない**ことです。実際、このデータの単変量MIでは上位に来ないことがあります。相互情報量は
**1列ずつ単独で**目的変数との関連を測るため、「他の列と組み合わせて効く」種類の特徴量を低く見積もることがあります。
思い込みで良し悪しを決めず、数字を見る。そして次の発展（任意）/追加演習で、**別の見方（並べ替え重要度）だと結論が
変わる**ことを実際に確かめます。`random_state`を固定しているのは、固定しないとMIの推定値が毎回変わるためです。"""),
                markdown("""## 自由課題（任意）：RDKitでSMILESから記述子を計算する

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
        [],
        [],
    )

    # ---- 第4回パート3 ----
    write_notebook(
        "11b-feature-selection",
        notebook(
            "第4回パート3：特徴量を選ぶ",
            "作った特徴量は、本当に信頼して使ってよいか。",
            [
                markdown("""## 作った特徴量を、安全に選ぶ

前のパートで特徴量を作りました。ここでは2つの問いを扱います。**「強力だがリークしやすい作り方を、
安全に使えるか」**、そして**「たくさん作った特徴量から、どれを残すか」**です。

強力だが**リークしやすい**特徴量の代表が**target encoding**（カテゴリを目的変数の平均で置き換える）です。
やり方を誤ると、第2回パート3で学んだリークを自ら仕込むことになります。安全なやり方を身につけます。"""),
            markdown("""### target encoding：全データ平均は「リーク」、OOFなら安全

「系列ごとの平均収率」を特徴量にしたいとします。**全データの平均**で作ると、各行の答えが自分の特徴量に
混ざりリークします。正しくは、第2回パート3の交差検証と同じ発想で、**その行を含まない分割の平均**で作ります
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

「リークあり」のMAEが「OOF」より**小さく（良く）見える**ことがあります。しかしそれは幻。本番では
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
- 木モデル(RandomForest)ではなく線形モデル(Ridge)を使ったのは、**木モデルはノイズ列があっても性能が落ちにくく、RFECVが何も削らないことが多い**ため。**推定器を変えると選択結果も変わる**。特徴量選択も「どの手法で測るか」に依存する、という点も併せて押さえます。
- 選択も交差検証の内側で行うことで、選びすぎ（過学習）を避けています。"""),
            ],
        ),
        [
            markdown("""## 発展（任意）：特徴量の作り方をもう2つ

ここからは経験者・自習向けの発展です。**交互作用特徴量**（2つの列の掛け算で「組み合わせの効果」を
表す）と、連続値を区間に区切る**ビニング**を扱います。"""),
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

区間0（低温）〜3（高温）ごとの平均収率が出ます。中間の区間で収率が高い（山型）なら、第2回パート1で見た
温度の効果と一致。ビニングは効果を見せやすい一方、情報を捨てる面もあるので、元の連続値と併用も検討します。"""),
        ],
        [
            markdown("""## 追加演習（任意）

作った特徴量の効き目を、並べ替え重要度で確かめます。第1・第4回パート1で使った並べ替え重要度を、
この回で作った特徴量を含めた全体に適用します。自作特徴量が上位に来るかを、holdoutで公平に確認します。"""),
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

ここでは`temperature_distance`が**上位に来ることがあります**。ところが同じ回の基本では、相互情報量(MI)で
同じ列が**下位**、アブレーションでは追加しても**MAEがほとんど改善しない**。3つの見方で結論が食い違います。
矛盾ではなく、**それぞれ別の問いに答えているから**です。

- **アブレーション**：その列を入れるか抜くかで最終性能がどう動くか。他の列で代用が効くと、抜いても悪化せず「効果なし」に見える。
- **相互情報量**：その列を単独で見たときの関連の強さ。組み合わせて効く効果は測れない。
- **並べ替え重要度**：学習済みモデルが実際にその列に依存しているか。`temperature_distance`は`temperature_c`から作った相関の強い列なので、モデルがどちらを使うかで重要度が振れやすい。

教訓は2つ。**(1) 1つの指標だけで特徴量の良し悪しを断じない。(2) 元の列と強く相関する派生列（今回の距離特徴量）は、
重要度が不安定になりやすい。** 「作る→交差検証で効果を確かめる→複数の見方で解釈する」という一巡こそが、
思い込みを避ける特徴量設計です。"""),
        ],
    )

    # ---- 第4回パート3 ----
    write_notebook(
        "12-experiment-cycle",
        notebook(
            "第4回パート3：改善実験を1つずつ行う",
            "改善した理由を後から説明できる実験とは何か。",
            [
                markdown("""## 「なんとなく良くなった」を卒業する

改善は勢いでやると、後で「なぜ良くなったのか」を説明できません。この回のテーマは、**理由を後から
説明できる実験のやり方**です。次の原則が効きます。

1. **一度に変えるのは1つだけ**（複数変えると、どれが効いたか分からない）。
2. **比較条件は固定**（同じ分割・同じ指標）。
3. **結果は平均とばらつきで残す**（1回のスコアで一喜一憂しない）。
4. **良くなった実験も悪くなった実験も記録する**（消さない）。

まず、すべての実験で共通して使うデータと交差検証を用意します。"""),
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
                markdown("""## 演習：1要素だけ変えて、実験ログに残す

`max_depth`**だけ**を変えた3つの実験を回し、結果を表（実験ログ）にします。他の設定は固定。
学習F1と検証F1平均を両方残すのは、**過学習の度合い**（第2回パート3）も一緒に記録するためです。"""),
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

- **実験名 / 変えたもの（1つ）/ 固定した比較条件 / 結果の平均とばらつき / 分かったこと / 次の仮説**

Copilotには次の実験案を出してもらってもよいですが、**優先順位と「予測時点で妥当か」の判断は人**が行います。"""),
            ],
        ),
        [
            markdown("""## 発展（任意）：探索を自動化し、正直な推定を得る

手で`max_depth`を変えるのは学習には良いですが、設定が増えると大変です。**探索の自動化**と、
第2回パート3で学んだ**ネストCV（正直な推定）**、そして**重要度を区間で読む**ことを扱います。"""),
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

第1回パート1で見た並べ替え重要度を、今度は**ばらつき（±2SD）つき**で読みます。下限が0を跨ぐ特徴量は
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
（「この列を強める特徴量を足したら改善するのでは？」）を1つ立てて、基本の実験ログへ戻ります。これが改善実験です。"""),
        ],
        [
            markdown("""## 追加演習（任意）

実験の回し方を仕組み化します。90分の外の自習向けです。まず**実験を1行で記録する関数**を作り、
複数の設定を回してログに溜めます。手作業のコピペより、記録漏れが減ります。"""),
            code("""
                from sklearn.model_selection import cross_val_score

                experiment_log = []
                def run_experiment(name, estimator, note=""):
                    "設定を交差検証で評価し、実験ログへ1行追加して返す。"
                    scores = cross_val_score(estimator, X, y, cv=cv, scoring="f1")
                    row = {"実験名": name, "F1平均": round(scores.mean(), 3), "F1_SD": round(scores.std(), 3), "分かったこと": note}
                    experiment_log.append(row)
                    return row

                run_experiment("depth3", make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=150, max_depth=3, random_state=42)), "浅め")
                run_experiment("depth6", make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42)), "標準")
                run_experiment("leaf4", make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=150, max_depth=6, min_samples_leaf=4, random_state=42)), "葉を大きく")
                pd.DataFrame(experiment_log)
            """),
            markdown("""### 出力の読み方

3つの実験がログにたまり、F1平均・ばらつき・分かったことが1表に。**変更点と結果がセットで残る**ので、後から
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
最適な深さ。2本の乖離が広がるほど過学習が進んでいる、という第2回パート3の読み方がそのまま使えます。"""),
            markdown("""### 実験ログをファイルに残す

ログをCSVに保存し、読み直します。セッションをまたいで実験を積み上げられ、再現性（第5回パート3）にもつながります。"""),
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

    # ---- 第5回パート3 ----
    write_notebook(
        "15-show-and-tell",
        notebook(
            "第5回パート3：モデルを運用する（永続化・監視・再学習）",
            "モデルを「作って終わり」にしないために、運用で何をするか。",
            [
                markdown("""## 運用のループ：学習 → 提供 → 監視 → 再学習

ここまでで「良いモデルを作る」ことはできました。実務では、そこからが本番です。モデルは
**作って終わりではなく、動かし続ける手順**まで扱います。

> **学習 → 提供（サービング）→ 監視 → 再学習 → …**

このループを回す考え方や道具をまとめて**MLOps**と呼びます。ここでは、保存（永続化）・説明書
（モデルカード）・適用範囲（適用領域）・監視・再学習の5つを扱います。"""),
                markdown("""## 永続化：学習済みモデルをファイルに保存する

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
`Pipeline`ごと保存するので、**受け取った人は前処理を意識せず`predict`するだけ**。第3回パート3でPipelineに
まとめた恩恵がここで効きます。"""),
                markdown("""## 提供（サービング）：学習済みモデルを「関数」として使えるようにする

運用では、新しい試料が来るたびに学習し直しません。**保存済みモデルを読み込み、予測だけを返す
関数**を用意します。"""),
                code("""
                    def predict_activity(samples):
                        "新しい試料(DataFrame)へ、活性の予測(0/1)と確率を返す推論関数。"
                        proba = reloaded.predict_proba(samples[feat])[:, 1]
                        return pd.DataFrame(
                            {"活性予測": (proba >= 0.5).astype(int), "活性確率": proba.round(3)},
                            index=samples.index,
                        )

                    display(predict_activity(X_te.head()))
                """),
                markdown("""### 出力の読み方

前処理ごと保存したPipelineなので、受け取った人は`predict_activity(新しいデータ)`を呼ぶだけで
予測できます。これが「サービング」の最小形です。Webサービスやバッチ処理も、裏でこの関数を
呼んでいるだけ、とイメージしてください。"""),
                markdown("""## モデルカード：使い方の説明書を関数で作る

モデルは「精度の数字」だけ渡してもトラブルの元です。**誰向けか・何を決めるためか・限界・禁止事項**を
1枚にまとめた**モデルカード**を、関数で自動生成します。第2回パート2の問題設定が、そのまま説明書になります。"""),
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
列を入力にしない）」は、第2回パート2〜3で扱ったリークの注意点です。**精度より先に限界を書く**のが、信頼される
モデル提供者の作法です。"""),
                markdown("""## 監視と再学習：いつモデルを作り直すか

運用後は、次を定期的に見張ります。

- **入力のドリフト**：入力分布が学習時とずれていないか
- **予測の傾向**：予測の陽性率が急に変わっていないか
- **性能**：正解ラベルが遅れて届いたら、F1などを計算し直す
- **適用領域**：学習データから遠い入力が増えていないか（次のセクションで扱う）

これらが目安を超えたら**再学習のトリガー**です。新しいデータを足して学習し直し、**同じ検証
（第2回パート3）・同じ評価（第3回）で前のモデルと比較**してから入れ替えます。作って終わりにせず、
このループを回し続けることが、実データでモデルを役立て続けるコツです。"""),
                markdown("""## まとめ

- **永続化**：Pipelineごと保存すれば、前処理を含めて復元できる。
- **サービング**：保存済みモデルを関数として公開すれば、使う側は前処理を意識しなくてよい。
- **モデルカード**：性能より先に「使ってよい範囲・使ってはいけない条件」を書く。
- **監視と再学習**：正解ラベルが無くても入力ドリフトは検知できる。再学習後は必ず旧モデルと比較する。"""),
            ],
        ),
        [
            markdown("""## 発展（任意）：適用領域とドリフトの検知

発展として、**適用領域**（予測してよい範囲）と、それを使った**ドリフト検知**を扱います。"""),
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
            markdown("""### 読みどころ

範囲外と判定された試料は、予測を鵜呑みにせず人が確認する。これが**安全にAIを使う**ということです。"""),
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

                # (2) 監視：元データとドリフト後を見分けられるか（adversarial validation, 第2回パート3）
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
- 一方、**参考F1は運用中すぐには測れません**（正解が遅れて届くため）。しかもこのデータ・特徴量では変化が小さく、性能指標だけに頼ると見逃しかねません。だからこそ、正解なしで異常を検知するadversarial validation（第2回パート3）のような監視が実務で効きます。"""),
        ],
        [
            markdown("""## 追加演習（任意）

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
            markdown("""### 成績表をファイルに書き出す

`classification_report`を表として保存します。引き継ぎに添付できる、機械可読な成績表です。"""),
            code("""
                from sklearn.metrics import classification_report

                rep = classification_report(y_te, reloaded.predict(X_te), target_names=["非活性", "活性"], output_dict=True)
                rep_df = pd.DataFrame(rep).T.round(3)
                rep_df.to_csv(ROOT / "workspace" / "classification_report.csv")
                display(rep_df)
            """),
            markdown("""### 出力の読み方、そしてこの教材の終わりに

クラスごとのprecision/recall/F1と全体のaccuracyが表になり、CSVで保存されます。数字だけを渡すのではなく、
**モデルカード（用途と限界）＋メタ情報（来歴）＋成績表**をひとまとめに渡す。ここまでできれば、
「作って終わり」から「運用でき、引き継げる」モデルへの橋を渡せています。全5回、おつかれさまでした。"""),
        ],
    )

    # ---- 第5回パート1 ----
    write_notebook(
        "16-neural-networks",
        notebook(
            "第5回パート1：ニューラルネットワークを試す",
            "複雑なモデルは、このデータでも必ず勝つのか。",
            [
                markdown("""## ニューラルネットワークとは

**ニューラルネットワーク**は、入力を層状につないだ関数で表現を学習するモデルです。もっとも
基本的な形が**MLP（多層パーセプトロン）**で、入力層・**隠れ層**（中間の層）・出力層を重ねます。
画像やテキストなど、大量データがある分野で高い性能を出すことで知られています。

ここでの問いは、**このデータ（420行の表データ）でも、複雑なモデルは常に有利なのか**です。
第4回パート1で比較した木系モデルと、正面から同条件で比べます。"""),
                common_load_cell(),
                markdown("""## 演習：MLPと、これまでのモデルを同条件で比べる

`MLPClassifier`は数値の尺度に敏感なため、木系モデルと違い**標準化（StandardScaler）が必須**です。
同じ交差検証・同じ特徴量で、MLPとRandom Forestを並べます。"""),
                code("""
                    from sklearn.model_selection import cross_validate, StratifiedKFold
                    from sklearn.pipeline import make_pipeline
                    from sklearn.impute import SimpleImputer
                    from sklearn.preprocessing import StandardScaler
                    from sklearn.neural_network import MLPClassifier
                    from sklearn.ensemble import RandomForestClassifier

                    features = ["temperature_c", "reaction_time_h", "concentration_m", "molecular_weight", "logp", "tpsa"]
                    X = df[features]
                    y = df["active"]
                    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

                    candidates = {
                        "MLP（隠れ層16）": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), MLPClassifier(hidden_layer_sizes=(16,), max_iter=2000, random_state=42)),
                        "Random Forest": make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=200, max_depth=5, random_state=42)),
                    }
                    for name, est in candidates.items():
                        result = cross_validate(est, X, y, cv=cv, scoring="f1")
                        print(f"{name:16s} F1={result['test_score'].mean():.3f} ± {result['test_score'].std():.3f}")
                """),
                markdown("""### 出力の読み方

- **MLPがRandom Forestを上回るとは限りません**。420行という件数は、ニューラルネットワークが
  実力を発揮するには少なすぎることが多いのです。
- ばらつき（±）も見ます。MLPは初期値やデータの並びに敏感で、木系モデルよりばらつきが大きく
  出ることがあります。
- 「複雑なモデル＝高性能」ではなく、**データの量と質に見合ったモデルを選ぶ**という姿勢が大切です。"""),
                markdown("""## 演習：尺度をそろえないとどうなるか

`StandardScaler`を抜いた場合と比べます。木系モデルは数値の尺度（桁の大きさ）に鈍感ですが、
MLPは内部で重みを掛け合わせるため、**尺度が違う列が混ざると学習が不安定になりやすい**という
性質があります。"""),
                code("""
                    unscaled = make_pipeline(SimpleImputer(strategy="median"), MLPClassifier(hidden_layer_sizes=(16,), max_iter=2000, random_state=42))
                    scaled = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), MLPClassifier(hidden_layer_sizes=(16,), max_iter=2000, random_state=42))
                    for name, est in {"標準化なし": unscaled, "標準化あり": scaled}.items():
                        result = cross_validate(est, X, y, cv=cv, scoring="f1")
                        print(f"{name:8s} F1={result['test_score'].mean():.3f} ± {result['test_score'].std():.3f}")
                """),
                markdown("""### 出力の読み方

多くの場合、**標準化ありの方が安定して高いF1**になります。`molecular_weight`（数十〜百単位）と
`logp`（-1〜2程度）のように桁が大きく違う列が混ざると、尺度の大きい列に引きずられて学習が
うまく進まないことがある、という具体例です。"""),
                markdown("""## 演習：ベースラインと比べる

第1回・第2回と同じ習慣で、**何もしないモデル（Dummy）**と**単純な線形モデル（Logistic回帰）**も
並べます。複雑なモデルの価値は、単純なモデルとの差でしか語れません。"""),
                code("""
                    from sklearn.dummy import DummyClassifier
                    from sklearn.linear_model import LogisticRegression

                    baselines = {
                        "多数派ベースライン": DummyClassifier(strategy="most_frequent"),
                        "ロジスティック回帰": make_pipeline(SimpleImputer(strategy="median"), LogisticRegression(max_iter=1000)),
                        "MLP（隠れ層16）": scaled,
                        "Random Forest": candidates["Random Forest"],
                    }
                    for name, est in baselines.items():
                        result = cross_validate(est, X, y, cv=cv, scoring="f1")
                        print(f"{name:16s} F1={result['test_score'].mean():.3f}")
                """),
                markdown("""### 出力の読み方

MLPが多数派ベースラインより高ければ「何かは学習できている」と言えます。ただし**単純な
ロジスティック回帰にすら勝てない**なら、このデータ・この設定ではMLPを選ぶ理由がない、と
判断できます。"""),
                markdown("""## まとめ

- MLPは入力を層状に処理するモデルで、**数値の標準化が必須**という点が木系モデルと異なる。
- 420行程度の表データでは、MLPが木系モデルに勝つとは限らない。
- モデルを複雑にする前に、**単純なモデルとの差を確認する**という第1回からの姿勢が、ここでも生きる。"""),
            ],
        ),
        [
            markdown("""## 発展（任意）：隠れ層の大きさと学習時間

隠れ層のユニット数を変えると、性能と学習時間がどう動くかを見ます。"""),
            code("""
                import time

                rows = []
                for units in [4, 16, 64, 128]:
                    est = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), MLPClassifier(hidden_layer_sizes=(units,), max_iter=2000, random_state=42))
                    start = time.perf_counter()
                    result = cross_validate(est, X, y, cv=cv, scoring="f1")
                    elapsed = time.perf_counter() - start
                    rows.append({"隠れ層ユニット数": units, "F1": result["test_score"].mean(), "学習時間(秒)": round(elapsed, 2)})
                pd.DataFrame(rows).round(3)
            """),
            markdown("""### 出力の読み方

ユニット数を増やすほど学習時間は伸びますが、F1が単調に良くなるとは限りません。**データ量に対して
モデルが複雑すぎる（過剰パラメータ）と、むしろ不安定になる**ことがあります。"""),
            markdown("""### 早期終了（early stopping）を試す

`early_stopping=True`にすると、検証スコアの改善が止まった時点で学習を打ち切ります。過学習を防ぎつつ
学習時間を節約する工夫です。"""),
            code("""
                early = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), MLPClassifier(hidden_layer_sizes=(64,), max_iter=2000, early_stopping=True, random_state=42))
                result = cross_validate(early, X, y, cv=cv, scoring="f1")
                print(f"early_stopping=True: F1={result['test_score'].mean():.3f} ± {result['test_score'].std():.3f}")
            """),
            markdown("""### 出力の読み方

早期終了ありのF1を、上のセルの「隠れ層64」の結果と比べます。大きく変わらないなら、このデータでは
学習の打ち切りが結果に悪影響を与えていないということです。"""),
            markdown("""### 活性化関数を変える

隠れ層の出力を非線形に変換する**活性化関数**を変えると、学習の挙動が変わります。既定の`relu`と
`tanh`を比べます。"""),
            code("""
                for activation in ["relu", "tanh"]:
                    est = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), MLPClassifier(hidden_layer_sizes=(32,), activation=activation, max_iter=2000, random_state=42))
                    result = cross_validate(est, X, y, cv=cv, scoring="f1")
                    print(f"activation={activation:5s} F1={result['test_score'].mean():.3f} ± {result['test_score'].std():.3f}")
            """),
            markdown("""### 出力の読み方

差はデータやシードによって大小さまざまです。**どちらが常に優れているというものではなく**、
複数試して比較すること自体が、ニューラルネットワークを扱う上で必要な手間だと分かります。"""),
            markdown("""### 学習曲線（loss_curve_）を見る

`MLPClassifier`は学習中の損失（誤差）の推移を`loss_curve_`に記録しています。学習がきちんと
収束しているかを確認できます。"""),
            code("""
                fitted = scaled.fit(X, y)
                mlp_step = fitted.named_steps["mlpclassifier"]
                print("学習回数（イテレーション数）:", len(mlp_step.loss_curve_))
                print("最終損失:", round(mlp_step.loss_curve_[-1], 4))
                print("最初の損失:", round(mlp_step.loss_curve_[0], 4))
            """),
            markdown("""### 出力の読み方

最終損失が最初の損失より十分小さければ、学習は進んでいます。**イテレーション数が`max_iter`の
上限に張り付いている**場合は、学習が収束しきっていない可能性があるので、`max_iter`を増やすか
`early_stopping`を検討します。"""),
        ],
        [
            markdown("""## 追加演習（任意）

回帰タスク（収率`yield_pct`の予測）でも、MLPRegressorとRandom Forestを比較します。90分の外の
自習向けです。"""),
            code("""
                from sklearn.neural_network import MLPRegressor
                from sklearn.ensemble import RandomForestRegressor
                from sklearn.model_selection import KFold

                reg_cv = KFold(n_splits=5, shuffle=True, random_state=42)
                reg_candidates = {
                    "MLPRegressor": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), MLPRegressor(hidden_layer_sizes=(32,), max_iter=3000, random_state=42)),
                    "Random Forest": make_pipeline(SimpleImputer(strategy="median"), RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42)),
                }
                for name, est in reg_candidates.items():
                    result = cross_validate(est, df[features], df["yield_pct"], cv=reg_cv, scoring="neg_mean_absolute_error")
                    print(f"{name:14s} MAE={-result['test_score'].mean():.3f}")
            """),
            markdown("""### 出力の読み方

分類と同じ傾向が出るか確認します。**回帰でもMLPが必ず勝つわけではない**ことが多いはずです。
第3回パート1のMAEと見比べ、複雑なモデルを試す前に単純なモデルとの差を確認する習慣を続けます。"""),
            markdown("""### L2正則化（alpha）を変える

`alpha`は重みの大きさを罰する正則化の強さです。大きくすると過学習を抑えますが、強すぎると
学習不足になります。"""),
            code("""
                for alpha in [0.0001, 0.01, 1.0]:
                    est = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), MLPClassifier(hidden_layer_sizes=(32,), alpha=alpha, max_iter=2000, random_state=42))
                    result = cross_validate(est, X, y, cv=cv, scoring="f1", return_train_score=True)
                    print(f"alpha={alpha:<7} 学習F1={result['train_score'].mean():.3f}  検証F1={result['test_score'].mean():.3f}")
            """),
            markdown("""### 出力の読み方

`alpha`が小さいほど学習F1は高くなりやすい（覚え込みやすい）ですが、検証F1が伸びなければ過学習の
サインです。第1回で見た「木の深さと過学習」と同じ構図が、MLPでも`alpha`という別のダイヤルで
起こります。"""),
            markdown("""### 学習時間をRandom Forestと比べる

MLPと木系モデルでは、学習にかかる時間の性質も異なります。同じデータで学習時間を比較します。"""),
            code("""
                import time

                for name, est in {"MLP（隠れ層32）": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), MLPClassifier(hidden_layer_sizes=(32,), max_iter=2000, random_state=42)), "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=5, random_state=42)}.items():
                    start = time.perf_counter()
                    est.fit(X.fillna(X.median()), y)
                    print(f"{name:16s} 学習時間={time.perf_counter() - start:.3f}秒")
            """),
            markdown("""### 出力の読み方

このデータ規模ではどちらも数秒以内に収まりますが、木系モデルは並列化がしやすく、データが
大きくなっても比較的速く学習できる傾向があります。速度も、モデルを選ぶ際の判断材料の1つです。"""),
            markdown("""### 最適化アルゴリズム（solver）を変える

重みを更新する最適化アルゴリズムにも選択肢があります。既定の`adam`と、小規模データ向けとされる
`lbfgs`を比べます。"""),
            code("""
                for solver in ["adam", "lbfgs"]:
                    est = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), MLPClassifier(hidden_layer_sizes=(32,), solver=solver, max_iter=2000, random_state=42))
                    result = cross_validate(est, X, y, cv=cv, scoring="f1")
                    print(f"solver={solver:6s} F1={result['test_score'].mean():.3f} ± {result['test_score'].std():.3f}")
            """),
            markdown("""### 出力の読み方

`lbfgs`は小規模データで安定しやすいとされますが、必ず勝つわけではありません。**ハイパーパラメータの
選択肢は多く、どれが良いかはデータ次第**という感覚を持ち帰ってください。"""),
        ],
    )

    # ---- 第5回パート2 ----
    write_notebook(
        "17-transfer-learning",
        notebook(
            "第5回パート2：転移学習を知る",
            "少ないデータしかないとき、他所で学んだ知識を借りられないか。",
            [
                markdown("""## 転移学習とは

**転移学習**は、大量データで先に学習しておいたモデル（**事前学習済みモデル**）を、手元の少ない
データで追加学習（**ファインチューニング**）して使う手法です。画像認識やテキスト処理の分野で
広く使われています。

考え方はシンプルです。「ゼロから学ぶより、既に近い分野を学んだモデルを土台にする方が、
少ないデータでも良い結果が出やすい」というものです。"""),
                markdown("""## なぜこの教材では手を動かさないのか

この教材の`compound_experiments.csv`は420行の表データです。転移学習が効果を発揮するには、
**事前学習に使える大規模なデータと、それに近い領域の事前学習済みモデル**が必要ですが、この
規模の表データ単体では、事前学習を自分たちで行うことは現実的ではありません。

そのため、この回はコードを書かず、**考え方と実例を知ること**に絞ります。転移学習を学ぶ価値が
無いという意味ではなく、**「今回のデータでは前提条件が揃っていない」**という判断そのものが、
実務で重要な感覚です。"""),
                markdown("""## 化学・創薬分野での実例

- **分子表現学習**：大量の分子構造（SMILES）から、分子の性質を数値ベクトルとして事前学習するモデル群。手元の少ない実験データでファインチューニングし、新しい予測タスクに使う。
- **画像ベースの実験スクリーニング**：顕微鏡画像や結晶写真などを対象に、大規模画像データセットで事前学習したモデルを土台に、少数の実験画像で追加学習する。
- **言語モデルの応用**：論文や特許テキストを大量に学習した言語モデルを、社内文書の分類・要約にファインチューニングする。

共通しているのは、**事前学習の領域と、手元データの領域が近いほど効果が出やすい**という点です。"""),
                markdown("""## まとめ

- 転移学習＝事前学習済みモデルを、手元の少ないデータでファインチューニングして使う手法。
- この教材のデータ規模・形式では、事前学習を自分たちで行うことは現実的でない。
- 化学・創薬分野でも、分子表現学習や画像スクリーニングなど、条件が揃えば有効な場面がある。
- 「使えるかどうかを見極める」判断力も、手法そのものと同じくらい大切。"""),
            ],
        ),
        [
            markdown("""## 発展（任意）：事前学習済みモデルを探す観点

自分の業務データに転移学習が使えそうか検討するときの、確認ポイントを整理します。
コードは書かず、考え方の整理です。"""),
            markdown("""### 確認する3つの観点

1. **領域の近さ**：事前学習に使われたデータと、自分のデータはどれくらい近い分野か。
2. **データ形式**：画像・テキスト・分子構造など、事前学習済みモデルが対応する形式に合っているか。
3. **ライセンスと利用条件**：商用利用の可否、社内データを外部サービスへ送ってよいか（機密情報の
   取り扱い）を必ず確認する。

この3点が揃わない場合、転移学習より、この教材で扱ってきたような**表データ向けの手法（回帰・分類・
特徴量エンジニアリング）**の方が、現実的な選択肢になることが多いです。"""),
        ],
        [
            markdown("""## 追加演習（任意）

自分の業務に関連しそうな事前学習済みモデルや論文を1つ調べ、次の3点を1〜2行ずつメモします。
90分の外の自習向けです。

1. どんなデータで事前学習されているか
2. 自分の業務データとどれくらい領域が近いか
3. 試すとしたら、最初にどんな小さな検証をするか"""),
        ],
    )

    # ---- 任意：Kaggle Titanic ----
    write_named_notebook("05-advanced-and-operate", "titanic_optional.ipynb", notebook(
        "任意実践：Kaggle Titanicへ提出する",
        "この教材で学んだモデル作成・評価の手順を、実際のKaggleコンペで再現できるか。",
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
