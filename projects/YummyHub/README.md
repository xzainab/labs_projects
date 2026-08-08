# 🍽️ YummyHub — Digital Recipe Book & Dashboard

> A Python recipe manager for storing, organizing, rating, and rediscovering recipes — available as a terminal app and a Streamlit dashboard.


## 1. Overview
YummyHub replaces scattered, unorganized recipe storage (screenshots, notes, memory) with one structured, searchable, ratable recipe collection backed by a CSV file. It ships as two parallel interfaces sharing the same data layer: a CLI (`YummyHub.py`) and a Streamlit dashboard (`DIGITAL_RECIPE.py`).

## 2. Problem Statement
Home cooks lack a central, searchable place to store recipes, filter by ingredient, track which recipes are actually good, or turn chosen recipes into a single shopping list.

## 3. Project Objectives
- Add recipes via validated prompts (CLI) or a web form (Streamlit)
- Persist all data in a single flat-file `recipes.csv`
- Enforce controlled vocabularies for `category` and `difficulty level`
- Enable ingredient search, full listing, and random discovery
- Support rating (1–5) with averaging on re-rate
- Sort/filter recipes by rating and category
- Generate deduplicated shopping lists from selected recipes
- Expose all features through both a CLI menu and a Streamlit dashboard

## 4. File Directory & Structure

| File | Description |
|---|---|
| `YummyHub.py` | Core backend logic (`load_recipes`, `add_new_recipe`, `search_by_ingredients`, `rate_recipe`, `sort_by_rating`, `shopping_list`, `random_recipe`, etc.) **and** the CLI `main()` menu loop. Defines `FILE_NAME = "recipes.csv"`. |
| `DIGITAL_RECIPE.py` | Streamlit dashboard. Imports `YummyHub` as its data layer and reimplements each feature as a page (Overview, Add Recipe, Search, View All, Random, Rate, Sort, Shopping List) with custom CSS/KPI cards. |
| `recipes.csv` | Flat-file recipe database (1 header + 21 rows currently). |
| `testing.ipynb` | Scratch notebook used to prototype `pandas` operations during development. |
| `Python Project Guidelines.pdf` | Course assignment brief the project was built against. |
| `.gitattributes`, `.gitignore`, `.DS_Store` | Repo/config files (`.DS_Store` is an accidental commit). |
| `README.md` | This file. |

> No `requirements.txt`, `tests/`, or packaging files currently exist.

## 5. Data & Data Dictionary
`recipes.csv` (~4.35 KB) is both the raw and working dataset — read/written directly by both modules via `pandas`.

| Column | Type | Description |
|---|---|---|
| `id` | string (6-char) | UUID4-derived unique ID |
| `name` | string | Recipe title (must be unique) |
| `ingredients` | string, `;`-delimited | Ingredient list |
| `preparing time` | int | Minutes |
| `instructions` | string, `;`-delimited | Step-by-step instructions |
| `difficulty level` | categorical | Easy / Medium / Hard |
| `category` | categorical | Breakfast / Lunch / Dinner / Dessert / Drink |
| `rating` | float or null | 1.0–5.0, blended average on re-rate |

## 6. Data Preparation & Pipeline
1. **Load** — `load_recipes()` returns an empty `DataFrame` if `recipes.csv` doesn't exist yet.
2. **Type coercion** — dashboard coerces `rating` with `pd.to_numeric(..., errors="coerce").fillna(0.0)`.
3. **Validation on write** — duplicate name checks, blank-input rejection, whitelist checks for category/difficulty, numeric checks for prep time.
4. **Missing values** — new recipes get `rating = None`; CLI's `sort_by_rating()` uses `dropna`, while the dashboard fills with `0.0` and filters `rating > 0` (two slightly different strategies).
5. **Persist** — writes go back via `to_csv` (`mode="a"` for appends, full overwrite for rating updates).

No separate cleaning script exists — validation is front-loaded at input time.

## 7. EDA & Key Features
`testing.ipynb` was used to prototype the `pandas` logic before it was hardened into the app; it's a dev artifact, not a shipped report. At runtime, the dashboard's KPI strip computes:

| KPI | Computation |
|---|---|
| Recipes | `len(df)` |
| Avg. rating | mean of `rating` where `rating > 0` |
| Top category | `df["category"].mode()[0]` |

Key features: category tagging, case-insensitive ingredient search, random recipe discovery, 3-tier difficulty labeling.

## 8. Methodology / Core Logic
No ML — deterministic rule-based logic:
- **Rating update** — blends old and new rating 50/50 (`round((old + new) / 2, 1)`), not a true cumulative average.
- **Ingredient search** — case-insensitive substring match (`str.contains`) on the `ingredients` field.
- **Shopping list** — iterates selected recipes' ingredients, deduplicating manually (`if item not in shopping_list`).
- **Validation** — category/difficulty checked against hardcoded whitelists, normalized via `.capitalize()`.
- **IDs** — `str(uuid.uuid4())[:6]`.
- **Shared backend** — `DIGITAL_RECIPE.py` imports `YummyHub` rather than duplicating I/O logic.

## 9. Key Findings / Results
- 21 recipes seeded across 5 categories.
- 8 core workflows fully implemented in both interfaces.
- Two divergent rating-null-handling strategies between CLI and dashboard.
- Only two third-party dependencies: `pandas` and `streamlit`.

## 10. Important Visualizations
No charts/plots are generated (no `matplotlib`/`plotly` usage found). The "visual layer" is the dashboard UI itself: KPI stat cards, color-coded category badges, reusable recipe cards, and an 8-page sidebar menu.

## 11. Conclusions & Recommendations
- Demonstrates a clean CRUD + light-analytics loop using only `pandas` for persistence.
- The shared backend module is good architecture but has drifted (rating logic differs between CLI and dashboard) — should be unified.
- The averaging-based rating update should be documented for end users, since it isn't a conventional running average.
- Flat-CSV storage is a hard ceiling for any multi-user use case.

## 12. Future Improvements
- Move to SQLite for concurrency/data-integrity safety
- Unify rating-aggregation logic across CLI and dashboard
- Track `rating_count` for a true cumulative average
- Add `requirements.txt`/`pyproject.toml`
- Add automated tests (promote `testing.ipynb` checks to `pytest`)
- Tokenized ingredient search (avoid `"egg"` matching `"eggplant"`)
- Clean up `.DS_Store`, expand root `README.md`
- Add rating/category charts to the dashboard
- Support recipe editing/deletion

## 13. Technologies Used
Python 3 · `pandas` · `streamlit` · `uuid` · `random` · `os` · Jupyter Notebook · Markdown/PDF docs.

## 14. Deliverables

| File | Role |
|---|---|
| `recipes.csv` | Living recipe database |
| `YummyHub.py` | CLI app + shared backend |
| `DIGITAL_RECIPE.py` | Streamlit web app |
| `testing.ipynb` | Dev/prototyping artifact |

```bash
pip install pandas streamlit

python YummyHub.py              # CLI
streamlit run DIGITAL_RECIPE.py # Dashboard
```

## 15. Sources & Acknowledgments
- **Dataset** — `recipes.csv` is original, authored by the project team.
- **Assignment brief** — `Python Project Guidelines.pdf`.
- **Contributors** (from in-code docstrings):
  - **Zainab Abdulwahab** — categorization, add-recipe flow, CLI menu
  - **Kawthar Hussain** — view-all, shopping list, random recipe
  - **Malak Mahdi** — rating system, sort-by-rating, ingredient search
- **Libraries** — [pandas](https://pandas.pydata.org/), [Streamlit](https://streamlit.io/)