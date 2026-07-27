# Windows環境の準備

## 必要なもの

1. VS Code
2. VS CodeのPython拡張とJupyter拡張
3. uv

GitHubアカウントとGitのインストールは不要です。公開リポジトリの画面からZIPをダウンロードして使います。

## 初回だけ行う操作

1. リポジトリのGitHub画面を開く
2. 緑色の`Code`を押す
3. `Download ZIP`を選ぶ
4. ダウンロードしたZIPを右クリックし、`すべて展開`を選ぶ
5. 展開した`data-science-study-group-main`フォルダをVS Codeで開く

VS Codeで`ターミナル`→`新しいターミナル`を選び、次を実行します。

```powershell
uv sync
uv run python scripts/check_environment.py
```

VS Codeが拡張機能を勧めてきたら、PythonとJupyterをインストールします。Notebook右上のカーネル選択では、`.venv\Scripts\python.exe`を選択します。

## 2回目以降

いつもの勉強会フォルダをVS Codeで開き、ターミナルで次を実行します。

```powershell
uv sync
```

教材が更新された回だけ、新しいZIPをダウンロードします。自分で変更したNotebookは先に`workspace`フォルダへ保存し、新しい教材フォルダへコピーしてください。

第11回でRDKitを使う人だけ、事前に次を実行します。計算済み記述子を使う場合は不要です。

```powershell
uv sync --extra chemistry
```

## 教材を編集するとき

`lessons`配下は配布原本です。Notebookを`workspace`へコピーしてから編集します。これにより、教材ZIPを更新しても自分の作業を分けて残せます。

## うまくいかないとき

### `uv`が見つからない

uvをインストールした後、PowerShellを開き直します。社内プロキシなどでダウンロードが止まる場合は、講師へ画面とエラーメッセージを共有してください。

### Notebookでimportに失敗する

Notebookのカーネルが`.venv\Scripts\python.exe`になっているか確認し、PowerShellで`uv sync`を再実行します。

## Gitを試したい人向け（任意）

勉強会の必須操作ではありません。興味がある人はGit for Windowsを追加し、`clone`と`pull`を試せます。アカウント作成、commit、push、Pull Requestは扱わなくても問題ありません。

```powershell
git clone https://github.com/kazu-dota/data-science-study-group.git
cd data-science-study-group
git pull
```
