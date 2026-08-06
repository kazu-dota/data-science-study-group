"""教材の構成、リンク、Notebook実行を検証する。"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LESSONS = [
    "lessons/01-python-pandas-numpy/lesson.ipynb",
    "lessons/02-machine-learning-basics/lesson.ipynb",
    "lessons/03-advanced-models/lesson.ipynb",
    "lessons/04-model-evaluation/lesson.ipynb",
    "lessons/05-performance-improvement/lesson.ipynb",
]
LESSON_REQUIRED_TEXT = {
    LESSONS[0]: ["列の型と分布", "欠損と外れ値候補"],
    LESSONS[1]: ["予測問題と列の役割", "OneHotEncoder"],
    LESSONS[2]: ["木の深さと過学習", "学習F1"],
    LESSONS[3]: ["グループをまたいで評価", "誤った行を見る"],
    LESSONS[4]: ["学習曲線で改善の方向", "最終確認後に誤りを調べる"],
}
APPENDICES = [
    "appendix/image-recognition.ipynb",
    "appendix/audio-recognition.ipynb",
    "appendix/nlp.ipynb",
]
NOTEBOOKS = ["quickstart.ipynb", *LESSONS, *APPENDICES]


def validate_notebooks() -> list[Path]:
    paths = [ROOT / relative for relative in NOTEBOOKS]
    for path in paths:
        content = json.loads(path.read_text(encoding="utf-8"))
        cells = content["cells"]
        code_cells = [cell for cell in cells if cell["cell_type"] == "code"]
        assert content["nbformat"] == 4, f"Notebook形式が不正です: {path}"
        assert len(cells) >= 10, f"説明や例が少なすぎます: {path}"
        assert len(code_cells) >= 5, f"実行例が少なすぎます: {path}"
        ids = [cell.get("id") for cell in cells]
        assert all(ids) and len(ids) == len(set(ids)), f"セルIDが不正です: {path}"
        text = "\n".join(str(cell["source"]) for cell in cells)
        assert "上から順に実行してください" in text, f"開始案内がありません: {path}"
        assert not re.search(r"\b(CORE|DEEP DIVE)\b", text), f"不要なラベルがあります: {path}"
        if path.relative_to(ROOT).as_posix() in LESSONS:
            assert "外部資料の指定範囲" in text, f"外部資料への案内がありません: {path}"
            for required in LESSON_REQUIRED_TEXT[path.relative_to(ROOT).as_posix()]:
                assert required in text, f"深掘り項目「{required}」がありません: {path}"
    return paths


def validate_data() -> None:
    data = pd.read_csv(ROOT / "data" / "compound_experiments.csv")
    required = {"sample_id", "yield_pct", "active"}
    assert required <= set(data.columns), "教材データの列が不足しています"
    assert len(data) == 420, "教材データの行数が変わっています"
    assert data["sample_id"].is_unique, "sample_idが重複しています"


def validate_links() -> None:
    pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    errors = []
    for path in ROOT.rglob("*.md"):
        if any(part in {".git", ".venv", ".uv-cache", "archive", "work"} for part in path.parts):
            continue
        for target in pattern.findall(path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            relative = target.split("#", 1)[0]
            if relative and not (path.parent / relative).resolve().exists():
                errors.append(f"{path.relative_to(ROOT)} -> {target}")
    assert not errors, "リンク切れ:\n" + "\n".join(errors)


def execute_notebooks(paths: list[Path]) -> None:
    with tempfile.TemporaryDirectory(prefix="ds-course-") as temp_dir:
        for index, path in enumerate(paths, start=1):
            print(f"実行 {index}/{len(paths)}: {path.relative_to(ROOT)}", flush=True)
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "jupyter",
                    "nbconvert",
                    "--to=notebook",
                    "--execute",
                    str(path),
                    f"--output={index:02d}.ipynb",
                    f"--output-dir={temp_dir}",
                    "--ExecutePreprocessor.timeout=420",
                    "--log-level=ERROR",
                ],
                check=True,
                cwd=ROOT,
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="全Notebookも実行する")
    args = parser.parse_args()
    paths = validate_notebooks()
    validate_data()
    validate_links()
    if args.execute:
        execute_notebooks(paths)
    print("教材検証: OK")


if __name__ == "__main__":
    main()
