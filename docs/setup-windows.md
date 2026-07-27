# Windows環境の準備

## 必要なもの

1. VS Code
2. VS CodeのPython拡張とJupyter拡張
3. Git for Windows
4. uv

GitHubアカウントは不要です。公開リポジトリの閲覧、clone、pullはサインインせずに行えます。

## 初回だけ行う操作

PowerShellを開き、作業用フォルダへ移動します。

```powershell
git clone https://github.com/kazu-dota/data-science-study-group.git
cd data-science-study-group
uv sync
uv run python scripts/check_environment.py
code .
```

VS Codeが拡張機能を勧めてきたら、PythonとJupyterをインストールします。Notebook右上のカーネル選択では、`.venv\Scripts\python.exe`を選択します。

## 2回目以降

```powershell
cd <勉強会フォルダ>
git pull
uv sync
code .
```

第11回でRDKitを使う人だけ、事前に次を実行します。計算済み記述子を使う場合は不要です。

```powershell
uv sync --extra chemistry
```

## 教材を編集するとき

`lessons`配下は配布原本です。Notebookを`workspace`へコピーしてから編集します。これにより、次回の`git pull`で衝突しにくくなります。

## うまくいかないとき

### `git`が見つからない

Git for Windowsをインストールした後、VS CodeとPowerShellを一度閉じて開き直します。

### `uv`が見つからない

uvをインストールした後、PowerShellを開き直します。社内プロキシなどでダウンロードが止まる場合は、講師へ画面とエラーメッセージを共有してください。

### Notebookでimportに失敗する

Notebookのカーネルが`.venv\Scripts\python.exe`になっているか確認し、PowerShellで`uv sync`を再実行します。

## ZIPダウンロードの予備手段

Gitをインストールできない場合は、GitHubの`Code`から`Download ZIP`を選べます。ただし教材更新のたびに再ダウンロードが必要なため、通常はGitを使います。
