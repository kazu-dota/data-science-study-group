# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Japanese-language, 5-session hands-on data science course for pharmaceutical/chemistry
researchers who are ML beginners. The deliverables are teaching materials: per-session Jupyter
notebooks (`lessons/NN-name/lesson.ipynb`), Markdown guides (`docs/`, `lessons/*/README.md`),
and a synthetic chemistry dataset (`data/`). There is no application to run — the "product" is
the course content itself.

The course is organized **topic-first** (not workflow-first): each session is built around one
ML knowledge area, and sessions progress environment → build → evaluate → improve → advanced/operate.
The five lesson folders are `01-prepare-and-explore` (env/uv/Git basics, Python, pandas, EDA),
`02-build-models` (problem framing, regression, classification model comparison),
`03-evaluate-models` (validation/leakage, classification metrics incl. Logloss vs AUC, experiment
cycle), `04-feature-engineering` (Pipeline, feature creation, feature selection), and
`05-advanced-and-operate` (neural networks, transfer learning, MLOps: persistence/monitoring/retraining).
Session 5 also holds the optional Kaggle notebook (`lessons/05-advanced-and-operate/titanic_optional.ipynb`);
this is independent of the 5-session curriculum (which has no Kaggle-competition content).

## The single most important thing: notebooks and data are GENERATED

`scripts/build_course_materials.py` is the **single source of truth** for both the synthetic
data (`data/compound_experiments.csv` and `data/local_competition/*`) and **all 5
`lessons/*/lesson.ipynb` files** (plus `lessons/05-advanced-and-operate/titanic_optional.ipynb`).

- **Never hand-edit `lesson.ipynb` files or the CSVs in `data/`.** Edit the generator, then
  regenerate. Manual notebook edits will be overwritten on the next build and won't match the
  generator.
- The dataset is produced by `make_dataset()` with **fixed RNG seeds**. Do not change
  `make_dataset`/`write_data` unless you intend to change the data — doing so alters the
  committed CSVs. A correct content change leaves `git diff --stat data/` empty.
- `data/local_competition/*` is still generated but **no longer referenced by any lesson**
  (the mock-Kaggle-competition curriculum was removed). It's kept as raw material in case
  someone wants to build a custom exercise; don't treat stale references to it in old docs as
  a bug to silently "fix" by re-adding mock-competition content — that content was intentionally
  removed.

## Core commands

```bash
uv sync                                        # create .venv from pyproject/uv.lock (Python 3.12 only)
uv run python scripts/build_course_materials.py  # regenerate data + all 5 notebooks
uv run python scripts/validate_materials.py      # fast: structure + data invariants + relative links
uv run python scripts/validate_materials.py --execute   # also runs every notebook end-to-end
uv run python scripts/check_environment.py       # verify the learner environment
uv run jupyter lab                               # open notebooks in a browser
```

Optional dependency groups (guarded in the notebooks; base deps always work via fallback):

```bash
uv sync --extra chemistry   # rdkit (used only in session 4 part 2 / feature creation, behind try/except)
uv sync --extra advanced    # xgboost (used only in session 2 part 3 deep-dive, behind try/except)
```

The standard edit → verify loop: edit `build_course_materials.py` → run the build → run
`validate_materials.py --execute`. To iterate on one lesson quickly, execute it directly:

```bash
uv run jupyter nbconvert --to notebook --execute lessons/03-evaluate-models/lesson.ipynb \
  --output /tmp/out.ipynb --ExecutePreprocessor.timeout=420 --log-level=ERROR
```

## How the generator is structured (`scripts/build_course_materials.py`)

The build is two-phase: **first register module payloads, then assemble them into 5 notebooks.**

- `LESSON_META` — per-module objectives / terms / pitfalls / self-study / check questions,
  keyed by module name (e.g. `07-regression`, `16-neural-networks`). Key names are historical/
  descriptive labels, not strictly tied to which session a module ends up in — e.g. `01-kickoff`
  now holds the environment/uv/Git module, not a "kickoff" demo (that hands-on hook was
  intentionally removed; see below).
- `build_notebooks()` — one `write_notebook(folder, notebook(...), deep_dive_cells,
  appendix_cells)` call per module. `notebook(title, question, core_cells)` builds
  intro + setup + 基本 cells and stashes `_title`/`_question`. **`write_notebook` no longer
  writes a file** — it registers the module (title, question, core cells with intro+setup
  dropped, deep_dive, appendix, meta) into the global `MODULES` dict.
- `COURSE_GROUPS` — the 5 sessions. Each entry has `folder`, `title`, `overview`, and `members`
  (the module keys to splice in order — 4 for `01-prepare-and-explore`, 3 for the rest).
- `assemble_courses()` — for each group, builds the final cell list:
  `merged_intro` → `setup_cell` (`find_repo_root`) → `merged_guide` → for each member
  [`chapter_heading` (`# パートN：…`) → core → deep_dive → appendix] → `merged_wrapup`, then
  writes via `write_named_notebook` (which strips `_`-prefixed keys and assigns sequential cell
  IDs). Part count and numbering are derived dynamically from `len(group["members"])` — there is
  no folder-specific hardcoding, so sessions can have different numbers of parts.
- Cell helpers: `markdown(text)`, `code(text)` (both `dedent`+`strip` their input), and
  `font_cell(extra)` for plotting cells. Merge helpers: `merged_intro`, `merged_guide`,
  `chapter_heading`, `merged_wrapup`.
- Each assembled notebook's rendered structure is: merged intro → setup (`find_repo_root`) →
  `## この回で扱うこと` (merged guide) → per-part [`# パートN：…` → 基本 → 発展（任意）
  → 追加演習（任意）] → `## よくある誤り` / `## 自習` / `## 振り返りチェック` (merged wrap-up).
- `main()` runs `build_notebooks()` then `assemble_courses()`.

### Module → session map (for orientation when editing)

| Session (folder) | Members (module keys) |
|---|---|
| `01-prepare-and-explore` | `01-kickoff` (env/uv/Git), `02-python-with-copilot`, `03-pandas`, `04-eda` |
| `02-build-models` | `05-problem-framing`, `07-regression`, `10-model-comparison` |
| `03-evaluate-models` | `06-validation-leakage`, `08-classification` (incl. Logloss), `12-experiment-cycle` |
| `04-feature-engineering` | `09-preprocessing-pipeline`, `11a-feature-creation`, `11b-feature-selection` |
| `05-advanced-and-operate` | `16-neural-networks`, `17-transfer-learning`, `15-show-and-tell` (MLOps only) |

`13-kaggle-kickoff` and `14-kaggle-improvement` (mock-Kaggle-competition modules) were **deleted
entirely** — don't resurrect them from git history without confirming the course should re-add
Kaggle-competition practice. `15-show-and-tell`'s Show&Tell/self-introduction framing was also
dropped; only its MLOps-relevant content (persistence, model card, monitoring, retraining)
remains, folded directly into its own core/deep_dive/appendix cells (the old separate
`mlops_cells()` function was removed and its content merged into this module).

### Generator gotchas that will bite you

1. **`dedent` before `.format()`, never inside an f-string.** Injecting a multi-line variable
   (e.g. a joined bullet list) into an f-string leaves the template's own indentation intact,
   because `textwrap.dedent` then sees a zero-indent line and strips nothing. The result is
   stray leading whitespace that Markdown renders as gray code blocks / broken headings. The
   fix used throughout is `dedent("""...{x}...""").format(x=...)`. `font_cell` exists for the
   same reason (it dedents the font snippet and the extra code separately, then concatenates).

2. **Cells within a lesson share one kernel namespace.** 追加演習/発展（任意） cells rely on
   variables and imports defined in earlier 基本 cells (`df`, `X_train`, `model`, `features`,
   `pd`, `plt`, …). When adding cells, keep this continuity in mind, and keep every cell
   runnable on **base deps only** — anything needing `rdkit`/`xgboost` must be inside
   a `try/except ImportError` with a scikit-learn fallback, or `validate_materials.py --execute`
   (which runs on base deps) will fail.

3. **After merging, one notebook shares a kernel across several modules.** Each module was
   authored to be self-contained, and `assemble_courses` preserves member order, so variables
   generally don't collide across parts — but reused names (`df`, `model`, `X_train`, `features`)
   get rebound part-to-part. In `05-advanced-and-operate`, `15-show-and-tell`'s persistence cells
   (`reloaded`, `feat`, `X_tr`, `X_te`, `y_tr`, `y_te`) are defined in its own core cells and
   consumed later in its own deep_dive/appendix — if you reorder session-5 members away from
   `[16, 17, 15]`, re-check that ordering still holds.

## Validation contract (`scripts/validate_materials.py`)

`validate_files()` asserts: exactly 5 notebooks; each has ≥60 cells and ≥20 code cells; each
contains the required section headings (`## この回で扱うこと`, `## 発展（任意）`,
`## 追加演習（任意）`, `## よくある誤り`, `## 自習`, `## 振り返りチェック`)
plus the per-part chapter headings (`# パート1：`, `# パート2：`, `# パート3：` — note this check
is hardcoded to exactly 3, which is fine since it only asserts presence, not absence of a 4th);
and cell IDs are present and unique. `validate_data()` pins the dataset invariants (420 rows,
train 315 / test 105, `active` ∈ {0,1}, submission columns, id alignment) — this still passes
even though `local_competition` is now curriculum-unused, since the files are still generated.
`validate_relative_links()` checks every relative Markdown link resolves. `--execute` runs each
merged notebook with a 420s timeout. These thresholds encode intent — raise them when you add
content, don't silently trip them (session 5 needed several extra deep-dive/appendix cells added
to `16-neural-networks` to clear the ≥60/≥20 bar after the Kaggle modules were removed).

## Editing conventions specific to this repo

- **Language:** all learner-facing content is Japanese. Explain concepts directly; avoid
  invented analogies (a past request explicitly removed "cooking/detective"-style metaphors).
  Chemistry appears only as the data domain (yield, activity, solvent, scaffold), not as metaphor.
- **Notebook pedagogy:** each code cell is wrapped in explanation — "what we're about to do" →
  code → "how to read the output / common pitfalls" — and first-use APIs are explained inline.
  Exception: `17-transfer-learning` is intentionally concept-only (almost no code) — the course's
  synthetic 420-row tabular dataset can't meaningfully demonstrate transfer learning, and the
  notebook says so explicitly rather than faking a demo.
- **Data leakage is a course theme and a real constraint:** columns like `post_assay_signal`,
  `purity_pct`, `yield_pct` are post-experiment and must never be used as features for the
  planning-time prediction task; `scaffold_group`/`batch_id`/`experiment_date` are the grouping
  units for leakage-safe splits. This is taught in `02-build-models` (problem framing) and
  `03-evaluate-models` (validation/leakage), not confined to one module only.
- **`workspace/`** is where learners copy notebooks to edit; it is gitignored except its README.
  Notebooks write outputs there (e.g. `workspace/final_model.joblib`, `workspace/model_card.md`).
- Setup targets **Windows + VS Code + `uv`, no Git required** (learners download a ZIP). Git is
  covered as a **concept only** in `01-prepare-and-explore` part 1; hands-on `clone`/`pull` stays
  optional, documented in `docs/environment-and-git-basics.md` and `docs/setup-windows.md`. Keep
  `README.md`, `docs/setup-windows.md`, and `docs/course-plan.md` consistent with that when
  editing setup steps.

## Docs that must stay in sync with content

`README.md` (top-level tables + section markers), `lessons/README.md` (per-session folder/notebook
links), `docs/course-plan.md` (the 5-session/part mapping and per-part deep-dive table),
`docs/instructor-guide.md` (per-part teaching memos), `docs/resources.md`
(external resources keyed by session/part), `docs/kaggle-titanic-guide.md` (links to the optional
Titanic notebook under `lessons/05-advanced-and-operate/`), and `data/README.md` describe the
notebook structure and session/part numbering. If you change the section layout, markers, or
per-part emphasis in the generator, update these docs too — they refer to sessions as `第N回` and
to the sub-lessons as `パートK`.
