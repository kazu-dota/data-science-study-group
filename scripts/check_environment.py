"""勉強会のローカル環境を確認するスクリプト。"""

import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

REQUIRED_PACKAGES = (
    "ipykernel",
    "jupyterlab",
    "matplotlib",
    "numpy",
    "pandas",
    "scikit-learn",
    "seaborn",
)


def main() -> int:
    print("データサイエンス勉強会：環境チェック")
    print(f"Python: {sys.version.split()[0]}")
    print(f"実行環境: {Path(sys.executable)}")

    if sys.version_info[:2] != (3, 12):
        print("[NG] Python 3.12ではありません。`uv sync`を再実行してください。")
        return 1

    missing: list[str] = []
    for package in REQUIRED_PACKAGES:
        try:
            installed_version = version(package)
        except PackageNotFoundError:
            missing.append(package)
            print(f"[NG] {package}: 見つかりません")
        else:
            print(f"[OK] {package}: {installed_version}")

    if missing:
        print("\n不足パッケージがあります。`uv sync`を実行してください。")
        return 1

    from sklearn.datasets import load_iris
    from sklearn.ensemble import RandomForestClassifier

    features, target = load_iris(return_X_y=True)
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(features, target)
    prediction = model.predict(features[:1])[0]
    print(f"[OK] scikit-learn動作確認: 予測クラス={prediction}")
    print("\n準備OKです。VS CodeでNotebookを開きましょう。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
