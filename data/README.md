# 教材データ

このフォルダのデータは、勉強会用に生成した架空の化学実験データです。実在する企業、研究テーマ、化合物、実験結果とは関係ありません。

## `compound_experiments.csv`

420件の架空実験を収録しています。第3～12回で同じデータを繰り返し使い、データの見方からモデル改善まで段階的に学びます。

| 列 | 意味 | 予測計画時に利用 |
|---|---|---|
| `sample_id` | 架空の試料ID | 識別用のみ |
| `experiment_date` | 架空の実験日 | 状況による |
| `batch_id` | 架空の実験バッチ | 分割単位の検討用 |
| `scaffold_group` | 架空の化合物系列 | 可 |
| `smiles` | 教材用の小さな分子表現 | 可 |
| `solvent` / `catalyst` | 架空の実験条件 | 可 |
| `temperature_c` | 温度 | 可 |
| `reaction_time_h` | 反応時間 | 可 |
| `concentration_m` | 濃度 | 可 |
| `molecular_weight` / `logp` / `tpsa` | 計算済み記述子 | 可 |
| `h_bond_donors` / `rotatable_bonds` | 計算済み記述子 | 可 |
| `yield_pct` | 架空の収率 | 回帰の目的変数 |
| `active` | 架空の活性ラベル | 分類の目的変数 |
| `post_assay_signal` | 活性測定後の信号 | 不可・リーク教材 |
| `purity_pct` | 実験後の純度 | 不可・リーク候補 |

欠損値と明らかに大きい温度・反応時間を意図的に含めています。見つけることが演習なので、事前に削除しません。

## `local_competition`

第13～14回の模擬Kaggleで使います。

- `train.csv`：説明変数と`active`
- `test.csv`：説明変数のみ
- `sample_submission.csv`：提出形式の見本
- `instructor_answers.csv`：ローカル採点用の答え。第14回の採点まで開かない運用を推奨

公開リポジトリなので答えを技術的に隠すものではありません。順位を競うためではなく、train/test/提出CSVという流れを安全に体験するための教材です。

## 再生成

```powershell
uv run python scripts/build_course_materials.py
```

乱数シードを固定しているため、同じ内容を再生成できます。
