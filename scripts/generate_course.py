"""Quickstart、全5回、AppendixのNotebookを生成する。"""

from __future__ import annotations

from pathlib import Path

from course_content import (
    appendix_audio,
    appendix_image,
    appendix_nlp,
    lesson01,
    lesson02,
    lesson03,
    lesson04,
    lesson05,
    quickstart,
)
from course_content.builder import write_notebook

ROOT = Path(__file__).resolve().parents[1]

NOTEBOOKS = [
    ("quickstart.ipynb", quickstart),
    ("lessons/01-python-pandas-numpy/lesson.ipynb", lesson01),
    ("lessons/02-machine-learning-basics/lesson.ipynb", lesson02),
    ("lessons/03-advanced-models/lesson.ipynb", lesson03),
    ("lessons/04-model-evaluation/lesson.ipynb", lesson04),
    ("lessons/05-performance-improvement/lesson.ipynb", lesson05),
    ("appendix/image-recognition.ipynb", appendix_image),
    ("appendix/audio-recognition.ipynb", appendix_audio),
    ("appendix/nlp.ipynb", appendix_nlp),
]


def main() -> None:
    for relative_path, content in NOTEBOOKS:
        path = ROOT / relative_path
        write_notebook(path, content.TITLE, content.SUMMARY, content.CELLS)
        print(f"生成: {relative_path}")


if __name__ == "__main__":
    main()
