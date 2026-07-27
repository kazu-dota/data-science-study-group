# M365 Copilotと一緒にコードを書く

この勉強会では、Copilotに完成品を一度で作らせるより、短い相談を繰り返してコードを理解・改善します。

## プロンプトの基本形

Microsoftが紹介している「目的・背景・情報源・期待する出力」の4要素を使います。

```text
目的:
このPythonコードのエラーを直したいです。

背景:
私はPython初心者です。pandasでCSVを読んでいます。

情報源:
コード:
...

エラーメッセージ:
...

期待する出力:
原因を短く説明し、元のコードをなるべく残した最小の修正を示してください。
```

## よく使う4つの聞き方

### 読む

```text
以下のPythonコードを初心者向けに説明してください。
各行でデータの形と中身がどう変化するかも示してください。
```

### 小さく変更する

```text
以下のコードについて、変更する行を最小限にして、
RandomForestRegressorのmax_depthを3、5、10で比較できるようにしてください。
```

### エラーを調べる

```text
コードとエラーメッセージから原因候補を挙げ、
まず確認すべきことを1つずつ示してください。
```

### 分析をレビューする

```text
以下のモデル構築手順をレビューしてください。
データリーク、評価指標、データ分割の観点で問題がないか確認してください。
断定できない点は質問として返してください。
```

## 約束

- 自社データや機密情報は入力しない
- 必要な数行だけを貼る
- エラーメッセージを省略しない
- Copilotの提案は一つずつ試す
- 実行できても、分析方法が妥当とは限らない
- 何を予測時点で利用できるかは人が判断する

## 公式教材

- [Microsoft 365 Copilotで優れたプロンプトを書く](https://support.microsoft.com/en-us/microsoft-365-copilot/write-a-great-prompt-in-microsoft-365-copilot)
- [Microsoft Learn: Copilot Chat (Basic)の効果的なプロンプト](https://learn.microsoft.com/en-us/training/modules/write-effective-prompts-do-more-prompting/)
