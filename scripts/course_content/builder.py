"""教材Notebookを組み立てる共通処理。"""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

CellSpec = tuple[str, str]


def markdown(text: str) -> CellSpec:
    return ("markdown", dedent(text).strip() + "\n")


def code(text: str) -> CellSpec:
    return ("code", dedent(text).strip() + "\n")


def external_study(lesson_number: int) -> CellSpec:
    return markdown(
        f"""
        ## 外部資料と組み合わせる

        このNotebookは第{lesson_number}回の最低限の実習です。
        実習の前後に[外部資料の指定範囲](../../docs/resources.md)を読み、確認問題と追加演習にも取り組みます。
        """
    )


SETUP = code(
    """
    from pathlib import Path

    def find_repo_root(start=None):
        current = Path.cwd() if start is None else Path(start)
        for candidate in [current, *current.parents]:
            if (candidate / "pyproject.toml").exists():
                return candidate
        raise FileNotFoundError("pyproject.tomlがある教材フォルダ内で実行してください")

    ROOT = find_repo_root()
    DATA = ROOT / "data"
    print("教材フォルダ:", ROOT)
    """
)


def _cell(kind: str, source: str, index: int) -> dict:
    cell = {
        "cell_type": kind,
        "id": f"cell-{index:02d}",
        "metadata": {},
        "source": source,
    }
    if kind == "code":
        cell.update({"execution_count": None, "outputs": []})
    return cell


def write_notebook(path: Path, title: str, summary: str, cells: list[CellSpec]) -> None:
    intro = markdown(f"# {title}\n\n{summary}\n\n上から順に実行してください。")
    specs = [intro, SETUP, *cells]
    content = {
        "cells": [_cell(kind, source, index) for index, (kind, source) in enumerate(specs)],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (uv)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
