# 第13回：Kaggleに入って最初の提出を作る

**今日の問い**：コンペの説明を、ローカルの分析手順へどう翻訳するか。

## この回の深掘り

- `CORE`：問題・指標・train/test・提出形式を確認してベースラインを作る
- `DEEP DIVE`：列順、行数、ID順、一意性、値域まで提出ファイルを自動検査する
- `SELF-STUDY`：ベースラインを保存してから変更を1つだけ試す

## 90分

- 10分：問題、指標、提出形式を確認する
- 20分：trainとtestの違いを見る
- 25分：`TRY` ベースラインPipelineを実行する
- 20分：提出CSVを作り、形式を検査する
- 10分：Kaggleまたはローカル採点へ提出する
- 5分：次回に試す担当を分ける

## ASK COPILOT

```text
以下のコンペ説明から、目的変数、問題種別、評価指標、
学習データとテストデータ、提出ファイルの列と行数を抜き出してください。
書かれていない情報は推測しないでください。
```

既存教材は[教材候補一覧](../../docs/resources.md#第13回kaggleに入って最初の提出を作る)を参照します。

- 全員：模擬コンペの[lesson.ipynb](lesson.ipynb)
- Kaggleを利用できる人：[Titanic日本語ガイド](../../docs/kaggle-titanic-guide.md)と[titanic_optional.ipynb](titanic_optional.ipynb)
