# Kaggle Titanic 日本語ガイド

## 目的

第5回のパート1・2（模擬コンペ）で覚えた「問題確認→ローカル検証→提出CSV作成→提出」の流れを、実際のKaggle過去コンペで1回経験します。順位を競うことは目的にしません。

## 使うコンペ

[Titanic - Machine Learning from Disaster](https://www.kaggle.com/competitions/titanic)

二値分類、欠損値、数値列とカテゴリ列、提出CSVを一通り扱えるため、この勉強会の最初の実コンペとして使います。

## 画面で見る場所

| Kaggle画面 | 確認すること |
|---|---|
| `Overview` | 何を予測するか、評価指標は何か |
| `Data` | `train.csv`と`test.csv`の違い、列の説明 |
| `Code` | 自分でベースラインを作った後の参考例 |
| `Submit Predictions` | 提出ファイルのアップロードと結果 |

## データの置き場所

Kaggleでルールへ同意し、`Data`からダウンロードしたファイルを展開します。

```text
data/
└── kaggle/
    └── titanic/
        ├── train.csv
        ├── test.csv
        └── gender_submission.csv
```

`data/kaggle`はGit管理対象外です。コンペデータをこの公開リポジトリへcommitしません。

## Notebook

[任意実践Notebook](../lessons/05-ship-and-operate/titanic_optional.ipynb)を上から順に実行します。データがまだない場合は、置き場所を表示して安全に停止します。

Notebookは次を行います。

1. train/testの形を確認
2. `Survived`を目的変数としてローカル検証
3. 欠損補完とOne-Hot EncodingをPipelineで実行
4. `PassengerId`と`Survived`の提出CSVを作成
5. 列名、行数、ID重複を検査

## アカウントやアクセスが難しい場合

Kaggleアカウントを作れない、社内ネットワークからアクセスできない、ルールへ同意できない場合は、[ローカル模擬コンペ](../data/README.md#local_competition)だけで同じ学習目標を満たせます。講師が代理提出する必要はありません。
