"""教材のファイル構成・データ・Notebook実行を検証する。"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def validate_files() -> list[Path]:
    notebooks = sorted((ROOT / "lessons").glob("*/lesson.ipynb"))
    assert len(notebooks) == 5, f"Notebookは5本必要です（旧15回を3回ずつ統合）: {len(notebooks)}本"
    required_sections = [
        "## この回でできるようになること",
        "# パート1：",
        "# パート2：",
        "# パート3：",
        "## DEEP DIVE",
        "## APPENDIX（任意・追加演習）",
        "## よくある誤り",
        "## SELF-STUDY",
        "## 振り返りチェック",
    ]
    for path in notebooks:
        content = json.loads(path.read_text(encoding="utf-8"))
        assert content["nbformat"] == 4
        assert len(content["cells"]) >= 60, f"セルが少なすぎます: {path}"
        code_cells = [cell for cell in content["cells"] if cell["cell_type"] == "code"]
        assert len(code_cells) >= 20, f"実行例が少なすぎます: {path}"
        markdown_text = "\n".join(
            "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
            for cell in content["cells"]
            if cell["cell_type"] == "markdown"
        )
        missing_sections = [section for section in required_sections if section not in markdown_text]
        assert not missing_sections, f"必須セクション不足: {path}: {missing_sections}"
        ids = [cell.get("id") for cell in content["cells"]]
        assert all(ids) and len(ids) == len(set(ids)), f"セルIDを確認してください: {path}"
    return notebooks


def validate_data() -> None:
    data = pd.read_csv(ROOT / "data" / "compound_experiments.csv")
    required = {"sample_id", "scaffold_group", "yield_pct", "active", "post_assay_signal"}
    assert required <= set(data.columns)
    assert len(data) == 420
    assert data["sample_id"].is_unique
    assert set(data["active"].unique()) <= {0, 1}

    directory = ROOT / "data" / "local_competition"
    train = pd.read_csv(directory / "train.csv")
    test = pd.read_csv(directory / "test.csv")
    answers = pd.read_csv(directory / "instructor_answers.csv")
    sample = pd.read_csv(directory / "sample_submission.csv")
    assert "active" in train and "active" not in test
    assert list(sample.columns) == ["sample_id", "active"]
    assert len(test) == len(answers) == len(sample)
    assert set(test["sample_id"]) == set(answers["sample_id"]) == set(sample["sample_id"])


def validate_relative_links() -> None:
    pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    errors = []
    for markdown_path in ROOT.rglob("*.md"):
        if any(part in {".git", ".venv", "work"} for part in markdown_path.parts):
            continue
        for target in pattern.findall(markdown_path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            relative = target.split("#", 1)[0]
            if relative and not (markdown_path.parent / relative).resolve().exists():
                errors.append(f"{markdown_path.relative_to(ROOT)} -> {target}")
    assert not errors, "リンク切れ:\n" + "\n".join(errors)


def execute_notebooks(notebooks: list[Path]) -> None:
    with tempfile.TemporaryDirectory(prefix="ds-study-notebooks-") as temp_dir:
        for path in notebooks:
            output_dir = Path(temp_dir) / path.parent.name
            output_dir.mkdir()
            print(f"execute: {path.parent.name}")
            subprocess.run(
                [
                    str(ROOT / ".venv" / "Scripts" / "jupyter.exe") if (ROOT / ".venv" / "Scripts" / "jupyter.exe").exists() else str(ROOT / ".venv" / "bin" / "jupyter"),
                    "nbconvert", "--to", "notebook", "--execute", str(path),
                    "--output", "lesson.ipynb", "--output-dir", str(output_dir),
                    "--ExecutePreprocessor.timeout=420", "--log-level=ERROR",
                ],
                check=True,
                cwd=ROOT,
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="全Notebookを実行する")
    args = parser.parse_args()
    notebooks = validate_files()
    validate_data()
    validate_relative_links()
    if args.execute:
        execute_notebooks(notebooks)
    print("教材検証: OK")


if __name__ == "__main__":
    main()
