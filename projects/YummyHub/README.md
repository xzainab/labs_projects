# 🍽️ YummyHub — Digital Recipe Book & Dashboard

> A Python-powered digital recipe manager that lets you store, organize, rate, and rediscover your favorite recipes — available both as a terminal application and as an interactive Streamlit web dashboard.

YummyHub replaces the scattered, paper-based (or screenshot-folder-based) way people keep recipes with a single structured, searchable, and ratable recipe collection backed by a simple CSV data store. It was built as a Python group project and ships in two parallel forms: a menu-driven Command-Line Interface (`YummyHub.py`) and a polished Streamlit dashboard (`DIGITAL_RECIPE.py`) that sits on top of the same data layer.

---

## 1. Problem Statement

Home cooks and hobbyist chefs typically manage recipes across disorganized sources — screenshots, sticky notes, bookmarked webpages, or memory. This creates several recurring problems:

- **No central catalog** — recipes aren't stored in one searchable place.
- **No easy filtering** — finding "what can I cook with what I already have" is manual and slow.
- **No feedback loop** — there's no lightweight way to track which recipes are actually good (rating/re-rating over time).
- **No shopping support** — turning a set of chosen recipes into a single consolidated grocery list is tedious and error-prone.

YummyHub addresses this by giving users a lightweight, file-based recipe management system with ingredient search, categorization, rating, and shopping-list generation — accessible from either a terminal or a browser-based dashboard.

---

## 2. Project Objectives

- **Data ingestion** — allow users to add new recipes (name, ingredients, prep time, instructions, difficulty, category) through guided, validated prompts (CLI) or a web form (Streamlit).
- **Data storage** — persist all recipes in a single flat-file `recipes.csv`, acting as the project's lightweight database.
- **Data validation** — enforce controlled vocabularies for `category` (Breakfast / Lunch / Dinner / Dessert / Drink) and `difficulty level` (Easy / Medium / Hard), reject blank/duplicate entries, and validate numeric/rating input.
- **Search & retrieval** — enable ingredient-based search, full recipe listing, and random recipe discovery.
- **Rating system** — let users rate recipes on a 1–5 scale, with existing ratings averaged against new ones rather than overwritten.
- **Ranking** — sort and surface recipes by rating (optionally filtered by category).
- **Shopping list generation** — deduplicate and consolidate ingredients across multiple selected recipes into a single list.
- **Dual interface** — expose all of the above through both a terminal menu (`YummyHub.py`) and a styled, multi-page Streamlit dashboard (`DIGITAL_RECIPE.py`) that reuses the same backend functions/data file.

---

## 3. File Directory & Folder Structure

YummyHub is a flat, single-directory Python project (no subpackages):

| File / Folder | Type | Description |
|---|---|---|
| `YummyHub.py` | Python module (backend + CLI) | Core data-access and business-logic functions (`load_recipes`, `add_new_recipe`, `search_by_ingredients`, `rate_recipe`, `sort_by_rating`, `shopping_list`, `random_recipe`, `view_all_recipes`, `recipes_categorize`) **and** the terminal `main()` menu loop (`display_menu` → options 1–8). Defines `FILE_NAME = "recipes.csv"`, the single source of truth for storage. |
| `DIGITAL_RECIPE.py` | Python module (Streamlit UI) | The web dashboard. Imports `YummyHub` as its data layer, reads `YummyHub.FILE_NAME`, and re-implements each CLI feature as an interactive Streamlit page (Overview, Add Recipe, Search by Ingredient, View All Recipes, Random Recipe, Rate Recipe, Sort by Rating, Shopping List) with custom CSS theming and KPI cards. |
| `recipes.csv` | Data file | The flat-file recipe database. 1 header row + recipe rows, `;`-delimited sub-fields for ingredients/instructions within cells. Read/written by both `YummyHub.py` and `DIGITAL_RECIPE.py` via `pandas`. |
| `testing.ipynb` | Jupyter Notebook | Development/scratch notebook used to prototype and sanity-check `pandas` operations (loading, filtering, rating logic, etc.) against `recipes.csv` before wiring the logic into `YummyHub.py`/`DIGITAL_RECIPE.py`. |
| `Python Project Guidelines.pdf` | Document | The academic/course assignment brief the project was built against (mandatory feature list, grading rubric, etc.). |
| `.gitattributes` | Config | Git attributes configuration (line endings / diff handling). |
| `.gitignore` | Config | Standard ignore rules for the Python/Git workflow. |
| `.DS_Store` | System file | macOS Finder metadata (accidentally committed; safe to remove and add to `.gitignore`). |
| `README.md` | Documentation | Project readme (this file). |

> **Note:** There is no `requirements.txt`, `src/` layout, `tests/` folder, or packaging metadata (`setup.py`/`pyproject.toml`) in the repository at present — see [Areas for Further Research](#12-areas-for-further-research--future-improvements).

---

## 4. Data & Data Dictionary

### Dataset overview

| Attribute | Detail |
|---|---|
| File | `recipes.csv` |
| Format | CSV (UTF-8, comma-delimited columns; `;`-delimited items *within* the `ingredients` and `instructions` cells) |
| Size | ~4.35 KB, 22 lines total (1 header + 21 recipe records as of the current commit) |
| Role | Acts as the sole persistent data store — read and written directly by both `YummyHub.py` and `DIGITAL_RECIPE.py` via `pandas.read_csv` / `DataFrame.to_csv` |
| Raw vs. processed | There is no separate "raw" ingestion source — `recipes.csv` is simultaneously the raw *and* the working/processed dataset. Every add/rate operation mutates it directly and immediately (no staging or backup copy is created). |

### Schema — `recipes.csv`

| Column | Type (as stored) | Description |
|---|---|---|
| `id` | `string` (6-char hex, e.g. `a1b2c3`) | Unique identifier generated via `str(uuid.uuid4())[:6]` when a recipe is created. Used to disambiguate recipes with matching/similar names during rating. |
| `name` | `string` | Recipe title. Must be unique (checked case-sensitively against existing `name` values before insertion). |
| `ingredients` | `string` (semicolon-delimited list, e.g. `"flour; sugar; eggs"`) | Free-text ingredient list. Stored as one delimited string per row and split on `"; "` for display/search. |
| `preparing time` | `int` | Preparation time in minutes. Collected via a validated numeric prompt (CLI) / `st.number_input` (dashboard). |
| `instructions` | `string` (semicolon-delimited list) | Step-by-step cooking instructions, stored as one delimited string per row and split on `"; "` for display. |
| `difficulty level` | `categorical string` — `Easy` \| `Medium` \| `Hard` | Enforced against a fixed whitelist (`DIFFICULTIES` in the dashboard, an inline list in the CLI). |
| `category` | `categorical string` — `Breakfast` \| `Lunch` \| `Dinner` \| `Dessert` \| `Drink` | Enforced against a fixed whitelist (`CATEGORIES` in the dashboard, validated via `recipes_categorize()` in the CLI). Drives the color-coded badges in the dashboard (`CATEGORY_COLOR` mapping). |
| `rating` | `float` (1.0–5.0) or `NaN`/`None` | User rating. `None`/blank until first rated. On re-rating, the new score is **averaged** with the existing score and rounded to 1 decimal place (see [Methodology](#8-methodology--core-logic--modeling)) rather than overwritten. |

---

## 5. Data Preparation & Pipeline

YummyHub does not run a traditional offline ETL pipeline — data preparation happens **inline, at the point of user interaction**, in both the CLI and dashboard layers. The effective pipeline is:

1. **Load** — `load_recipes()` checks whether `recipes.csv` exists (`os.path.exists`). If it does, it's loaded into a `pandas.DataFrame`; if not, an empty `DataFrame` is returned so the app can still run on a fresh checkout.
2. **Type coercion (dashboard only)** — `DIGITAL_RECIPE.py` explicitly coerces `rating` to numeric with `pd.to_numeric(df["rating"], errors="coerce").fillna(0.0)`, so any malformed/missing rating values become `0.0` rather than crashing downstream comparisons/aggregations.
3. **Input validation on write** — before any row is appended:
   - `name` is checked for **duplicates** against `df["name"].values`.
   - `ingredients` / `instructions` are split on commas or newlines, stripped of whitespace, filtered for blanks, and re-joined with `"; "` as the storage delimiter.
   - `preparing time` must parse as an `int` (CLI retries on `ValueError`; the dashboard constrains input via `st.number_input(min_value=0, step=1)`).
   - `difficulty level` and `category` are validated against fixed whitelists — invalid input is rejected with a re-prompt (CLI) or blocked at the widget level (dashboard, via `st.selectbox`).
4. **Missing-value handling**
   - New recipes are inserted with `rating` explicitly set to `None` until first rated.
   - `sort_by_rating()` drops unrated rows with `dropna(subset=["rating"])` before sorting, so unrated recipes never appear in "Top Rated" views.
   - The dashboard instead **fills** missing ratings with `0.0` for KPI/average calculations, then filters on `rating > 0` to distinguish "rated" from "unrated" — a subtly different (and more numerically robust) strategy than the CLI's `dropna` approach.
5. **Persist** — writes go back to `recipes.csv` via `DataFrame.to_csv`, using `mode="a", header=False` for appends (new recipes) or a full overwrite for updates (ratings), so the CSV is always the single up-to-date snapshot of state.

There is no separate cleaning script, no outlier handling, and no imputation beyond the rating defaults above — the "cleaning" is entirely defensive, front-loaded input validation rather than post-hoc data cleaning.

---

## 6. Exploratory Data Analysis (EDA) & Key Features

`testing.ipynb` served as the project's scratch/EDA notebook during development — used to prototype and validate the `pandas` operations (loading `recipes.csv`, filtering by ingredient substring, computing average ratings, sorting) before they were hardened into the reusable functions now living in `YummyHub.py` and `DIGITAL_RECIPE.py`. It is a development artifact rather than a polished analytical report, and is not wired into the application at runtime.

The application itself surfaces "EDA-style" insight at runtime rather than in a static notebook, via the dashboard's **KPI strip**, shown on every page except *Add Recipe*:

| KPI | Computation |
|---|---|
| **Recipes** | `len(df)` — total row count |
| **Avg. rating** | Mean of `rating` across rows where `rating > 0` (i.e., only recipes that have been rated at least once) |
| **Top category** | `df["category"].mode()[0]` — the most frequently occurring category in the dataset |

### Key features surfaced across the CLI / dashboard

- **Category-based organization** — every recipe is tagged with exactly one of 5 categories, driving both filtering (`st.multiselect`) and visual color-coding.
- **Ingredient search** — case-insensitive substring match against the `ingredients` column (`str.contains`).
- **Randomized discovery** — `random_recipe()` picks a uniformly random row index via `random.randint`.
- **Difficulty tagging** — a 3-tier `Easy`/`Medium`/`Hard` scale attached to every recipe.

---

## 7. Methodology / Core Logic / Modeling

YummyHub does not use machine learning — its "logic layer" is deterministic, rule-based data manipulation over the `recipes.csv` table. The core algorithms are:

### 7.1 Recipe rating — running average, not overwrite

```python
if pd.notna(old_rating):
    recipes.loc[index, "rating"] = round((float(old_rating) + new_rating) / 2, 1)
else:
    recipes.loc[index, "rating"] = round(new_rating, 1)
```
Every new rating is blended 50/50 with the previous rating rather than replacing it, producing a simple recency-weighted running average that smooths out single outlier scores. (Note: this is a 2-point average, not a true cumulative mean across *all* historical ratings — later ratings always carry more weight than earlier ones.)

### 7.2 Ingredient-based search

```python
matched_recipes = df[df['ingredients'].str.lower().str.contains(search_ingredient, na=False)]
```
A case-insensitive substring match against the semicolon-joined `ingredients` string — simple and effective for a small dataset, though it will also match partial-word substrings (e.g., searching `"egg"` also matches `"eggplant"`).

### 7.3 Shopping list generation

Iterates over every ingredient in every **selected** recipe, splitting on `;`, stripping whitespace, and appending to a running list **only if not already present** — a manual deduplication pass (`if item not in shopping_list`) rather than using a `set`, preserving insertion order for readability.

### 7.4 Category & difficulty validation (controlled vocabularies)

Both `category` and `difficulty level` are validated against hardcoded whitelists at the point of entry:
```python
categorize = ["breakfast", "lunch", "dinner", "dessert", "drink"]
valid_levels = ["easy", "medium", "hard"]
```
Input is lower-cased for comparison, then `.capitalize()`d before storage — guaranteeing consistent casing in the CSV regardless of how the user typed it.

### 7.5 Unique ID generation

```python
recipe_id = str(uuid.uuid4())[:6]
```
A truncated UUID4 is used as a lightweight, collision-resistant (for this dataset's scale) row identifier — primarily used to disambiguate multiple search matches during rating.

### 7.6 Dual-interface architecture

`DIGITAL_RECIPE.py` does not duplicate the CSV read/write logic — it imports `YummyHub` and calls `YummyHub.load_recipes()` / reuses `YummyHub.FILE_NAME`, meaning the CLI module doubles as the shared backend for the Streamlit frontend. The dashboard then layers Streamlit widgets (`st.form`, `st.selectbox`, `st.multiselect`, `st.slider`) and custom CSS (accent colors, card components, category badges) on top of that shared logic.

---

## 8. Key Findings / Results

Because YummyHub is an interactive application rather than a static analysis, its "results" are functional rather than statistical:

- **21 recipes** currently seeded in `recipes.csv` (as of the latest commit), spanning the 5 supported categories.
- **8 core user workflows** are fully implemented and available in *both* interfaces: add, search by ingredient, view all, random discovery, rate, sort by rating, generate shopping list, and (CLI-only labeling) categorize.
- **Two independently maintained rating aggregation strategies** exist across the CLI and dashboard (`dropna` filtering vs. `fillna(0.0)` + `> 0` filtering) — functionally similar in output but implemented differently, worth reconciling (see below).
- **Zero external dependencies beyond `pandas` and `streamlit`** — the entire application is achievable with two libraries plus the Python standard library (`os`, `uuid`, `random`).

---

## 9. Important Visualizations

YummyHub does not currently generate charts, plots, or exported visual reports (no `matplotlib`/`seaborn`/`plotly` usage was found in the codebase). Its "visual layer" is the Streamlit dashboard's UI itself:

- **KPI stat cards** — Recipes / Avg. Rating / Top Category, rendered as styled `<div class="stat">` blocks.
- **Category badges** — pill-shaped, color-coded labels per category (`CATEGORY_COLOR` mapping: Breakfast `#F4A259`, Lunch `#6FB98F`, Dinner `#EF6461`, Dessert `#A288E3`, Drink `#5AA9E6`).
- **Recipe cards** — a reusable `recipe_card()` component showing name, category badge, prep time, difficulty, and (contextually) star rating.
- **Sidebar navigation** — an 8-page radio menu (`🏠 Overview`, `➕ Add Recipe`, `🔍 Search by Ingredient`, `📖 View All Recipes`, `🎲 Random Recipe`, `⭐ Rate Recipe`, `🏆 Sort by Rating`, `🛒 Shopping List`) mirroring the CLI's 8-option menu.

> A future iteration could add a ratings-by-category bar chart or a prep-time distribution histogram using `st.bar_chart`/`plotly`, directly off the existing `df` — see Section 12.

---

## 10. Conclusions & Actionable Recommendations

- The project successfully demonstrates a complete **CRUD + light analytics** loop (Create/Read/Update recipes, aggregate ratings, generate derived outputs like shopping lists) using only `pandas` for persistence — a solid pattern for small, single-user, file-backed tools.
- The **shared backend module** (`YummyHub.py` imported by `DIGITAL_RECIPE.py`) is a good architectural instinct — it avoids duplicating the core CSV logic — but the two interfaces have since drifted (e.g., differing rating-null-handling strategies), so the shared functions should be the single source of truth for *all* aggregation logic, not just I/O.
- The averaging-based rating update is intentional and reasonable for a lightweight app, but should be documented for end users, since it does not behave like a conventional "average of all ratings ever submitted."
- For any real multi-user deployment, the flat-CSV storage model (no locking, no transactions, no concurrent-write protection) is a hard ceiling — see recommendations below.

---

## 11. Areas for Further Research / Future Improvements

- **Concurrency & data integrity** — `recipes.csv` has no file-locking or transactional writes; two simultaneous users (or the CLI and dashboard running against the same file at once) could corrupt data. A move to SQLite would resolve this with minimal code change (both interfaces already funnel through `pandas`, which reads/writes SQL natively).
- **Unify rating-aggregation logic** — reconcile the CLI's `dropna(subset=["rating"])` approach with the dashboard's `fillna(0.0)` + `rating > 0` approach into one shared, tested function in `YummyHub.py`.
- **True cumulative average rating** — track a `rating_count` alongside `rating` to compute a proper running mean instead of a 2-point blend.
- **Dependency management** — add a `requirements.txt` (or `pyproject.toml`) pinning `pandas` and `streamlit` versions; none currently exists in the repo.
- **Automated tests** — promote the ad-hoc checks in `testing.ipynb` into a real `tests/` suite (e.g., `pytest`) covering the add/search/rate/shopping-list functions.
- **Input robustness** — ingredient search is a raw substring match (`"egg"` matches `"eggplant"`); consider tokenized/whole-word matching for higher search precision.
- **Repository hygiene** — remove the tracked `.DS_Store` file and add it to `.gitignore`; the top-level `README.md` is currently a single title line and should be replaced with documentation such as this file.
- **Analytics/visualization** — add category-distribution and rating-distribution charts to the Streamlit Overview page using the KPI data already being computed.
- **Recipe editing/deletion** — the current feature set supports add, view, search, rate, and sort, but not editing or deleting an existing recipe.

---

## 12. Technologies Used

| Category | Technology |
|---|---|
| Language | Python 3 |
| Data handling | `pandas` (CSV I/O, filtering, sorting, aggregation) |
| Web dashboard | `streamlit` (multi-page UI, forms, widgets, custom CSS injection) |
| CLI | Python standard library `input()`/`print()` loop (`YummyHub.py::main`) |
| Unique IDs | `uuid` (UUID4, truncated to 6 characters) |
| Randomization | `random.randint` (random recipe selection) |
| File system | `os` (existence checks for `recipes.csv`) |
| Data storage | Flat-file CSV (`recipes.csv`) — no external database |
| Prototyping | Jupyter Notebook (`testing.ipynb`) |
| Documentation | Markdown (`README.md`), PDF assignment brief (`Python Project Guidelines.pdf`) |

---

## 13. Final Output Files / Deliverables

| File | Role |
|---|---|
| `recipes.csv` | The living, continuously updated recipe database — the primary "output" of ongoing app usage (every add/rate operation mutates this file). |
| `YummyHub.py` | Deliverable: standalone runnable CLI application (`python YummyHub.py`) plus the shared backend module. |
| `DIGITAL_RECIPE.py` | Deliverable: standalone runnable Streamlit web app (`streamlit run DIGITAL_RECIPE.py`). |
| `testing.ipynb` | Supporting development artifact — not a shipped deliverable, but documents the logic-prototyping process. |

### Running the project

```bash
# Install dependencies
pip install pandas streamlit

# Option 1 — Command-line interface
python YummyHub.py

# Option 2 — Streamlit web dashboard
streamlit run DIGITAL_RECIPE.py
```

> Both entry points read/write the same `recipes.csv` in the working directory — run them from the repository root.

---

## 14. Sources & Acknowledgments

- **Dataset** — `recipes.csv` is an original dataset authored by the project team specifically for this application (not sourced from an external/public recipe corpus).
- **Assignment brief** — built to satisfy the requirements laid out in `Python Project Guidelines.pdf`, the course/project specification driving the mandatory feature set (categorize, view, rate, shopping list, etc.).
- **Contributors** (per in-code function docstrings — *"Done by ..."* attributions found in `YummyHub.py`):
  - **Zainab Abdulwahab** — recipe categorization, add-new-recipe flow, main menu/CLI loop.
  - **Kawthar Hussain** — view-all-recipes, shopping list, random recipe generation.
  - **Malak Mahdi** — rating system, sort-by-rating, ingredient search.
- **Libraries** — [pandas](https://pandas.pydata.org/), [Streamlit](https://streamlit.io/), and the Python standard library (`uuid`, `os`, `random`).

---

*This README was generated from a direct review of the repository's source code, data schema, and structure as of the latest commit on the `main` branch.*
