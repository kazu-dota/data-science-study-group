# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Japanese-language, 15-session hands-on data science course for pharmaceutical/chemistry
researchers who are ML beginners. The deliverables are teaching materials: per-session Jupyter
notebooks (`lessons/NN-name/lesson.ipynb`), Markdown guides (`docs/`, `lessons/*/README.md`),
and a synthetic chemistry dataset (`data/`). There is no application to run — the "product" is
the course content itself.

## The single most important thing: notebooks and data are GENERATED

`scripts/build_course_materials.py` is the **single source of truth** for both the synthetic
data (`data/compound_experiments.csv` and `data/local_competition/*`) and **all 15
`lessons/*/lesson.ipynb` files** (plus `lessons/13-kaggle-kickoff/titanic_optional.ipynb`).

- **Never hand-edit `lesson.ipynb` files or the CSVs in `data/`.** Edit the generator, then
  regenerate. Manual notebook edits will be overwritten on the next build and won't match the
  generator.
- The dataset is produced by `make_dataset()` with **fixed RNG seeds**. Do not change
  `make_dataset`/`write_data` unless you intend to change the data — doing so alters the
  committed CSVs and breaks `data/local_competition/instructor_answers.csv` (the mock-Kaggle
  answer key). A correct content change leaves `git diff --stat data/` empty.

## Core commands

```bash
uv sync                                        # create .venv from pyproject/uv.lock (Python 3.12 only)
uv run python scripts/build_course_materials.py  # regenerate data + all 15 notebooks
uv run python scripts/validate_materials.py      # fast: structure + data invariants + relative links
uv run python scripts/validate_materials.py --execute   # also runs every notebook end-to-end
uv run python scripts/check_environment.py       # verify the learner environment
uv run jupyter lab                               # open notebooks in a browser
```

Optional dependency groups (guarded in the notebooks; base deps always work via fallback):

```bash
uv sync --extra chemistry   # rdkit (used only in lesson 11, behind try/except)
uv sync --extra advanced    # xgboost, optuna (used only in DEEP DIVE/APPENDIX, behind try/except)
```

The standard edit → verify loop: edit `build_course_materials.py` → run the build → run
`validate_materials.py --execute`. To iterate on one lesson quickly, execute it directly:

```bash
uv run jupyter nbconvert --to notebook --execute lessons/07-regression/lesson.ipynb \
  --output /tmp/out.ipynb --ExecutePreprocessor.timeout=180 --log-level=ERROR
```

## How the generator is structured (`scripts/build_course_materials.py`)

- `LESSON_META` — per-lesson objectives / terms / pitfalls / self-study / check questions,
  injected into the `guide` and `wrap_up` cells by `write_notebook`.
- `build_notebooks()` — one `write_notebook(folder, notebook(...), deep_dive_cells,
  appendix_cells)` call per lesson. `notebook(title, question, core_cells)` builds the
  intro + setup + CORE cells; `write_notebook` then splices in the guide, DEEP DIVE cells,
  optional APPENDIX cells, and wrap-up, and assigns sequential cell IDs.
- Cell helpers: `markdown(text)`, `code(text)` (both `dedent`+`strip` their input), and
  `font_cell(extra)` for plotting cells.
- Each notebook's rendered structure is: title → setup (`find_repo_root`) → `## この回で
  できるようになること` (guide) → CORE cells → `## DEEP DIVE` → `## APPENDIX（任意・追加演習）`
  → `## よくある誤り` / `## SELF-STUDY` / `## 振り返りチェック` (wrap-up). CORE = 90-min
  sync content; DEEP DIVE = advanced; APPENDIX = optional heavier self-study code.

### Two generator gotchas that will bite you

1. **`dedent` before `.format()`, never inside an f-string.** Injecting a multi-line variable
   (e.g. a joined bullet list) into an f-string leaves the template's own indentation intact,
   because `textwrap.dedent` then sees a zero-indent line and strips nothing. The result is
   stray leading whitespace that Markdown renders as gray code blocks / broken headings. The
   fix used throughout is `dedent("""...{x}...""").format(x=...)`. `font_cell` exists for the
   same reason (it dedents the font snippet and the extra code separately, then concatenates).

2. **Cells within a lesson share one kernel namespace.** APPENDIX/DEEP DIVE cells rely on
   variables and imports defined in earlier CORE cells (`df`, `X_train`, `model`, `features`,
   `pd`, `plt`, …). When adding cells, keep this continuity in mind, and keep every cell
   runnable on **base deps only** — anything needing `rdkit`/`xgboost`/`optuna` must be inside
   a `try/except ImportError` with a scikit-learn fallback, or `validate_materials.py --execute`
   (which runs on base deps) will fail.

## Validation contract (`scripts/validate_materials.py`)

`validate_files()` asserts: exactly 15 notebooks; each has ≥20 cells and ≥8 code cells; each
contains the required section headings (`## この回でできるようになること`, `## DEEP DIVE`,
`## APPENDIX（任意・追加演習）`, `## よくある誤り`, `## SELF-STUDY`, `## 振り返りチェック`);
and cell IDs are present and unique. `validate_data()` pins the dataset invariants (420 rows,
train 315 / test 105, `active` ∈ {0,1}, submission columns, id alignment). `validate_relative_links()`
checks every relative Markdown link resolves. These thresholds encode intent — raise them when
you add content, don't silently trip them.

## Editing conventions specific to this repo

- **Language:** all learner-facing content is Japanese. Explain concepts directly; avoid
  invented analogies (a past request explicitly removed "cooking/detective"-style metaphors).
  Chemistry appears only as the data domain (yield, activity, solvent, scaffold), not as metaphor.
- **Notebook pedagogy:** each code cell is wrapped in explanation — "what we're about to do" →
  code → "how to read the output / common pitfalls" — and first-use APIs are explained inline.
- **Data leakage is a course theme and a real constraint:** columns like `post_assay_signal`,
  `purity_pct`, `yield_pct` are post-experiment and must never be used as features for the
  planning-time prediction task; `scaffold_group`/`batch_id`/`experiment_date` are the grouping
  units for leakage-safe splits.
- **`workspace/`** is where learners copy notebooks to edit; it is gitignored except its README.
  Notebooks write outputs there (e.g. `workspace/submission_baseline.csv`).
- Setup targets **Windows + VS Code + `uv`, no Git required** (learners download a ZIP). Keep
  `README.md`, `docs/setup-windows.md`, and `docs/course-plan.md` consistent with that when
  editing setup steps.

## Docs that must stay in sync with content

`README.md` (top-level tables + section markers), `lessons/README.md` (per-lesson folder/notebook
links), `docs/course-plan.md` (the 4-layer depth table and per-session deep-dive table), and
`docs/instructor-guide.md` describe the notebook structure. If you change the section layout,
markers, or per-session emphasis in the generator, update these docs too.
