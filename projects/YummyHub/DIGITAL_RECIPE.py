import os
import uuid
from random import randint

import pandas as pd
import streamlit as st

import YummyHub

FILE_NAME = YummyHub.FILE_NAME
CATEGORIES = ["Breakfast", "Lunch", "Dinner", "Dessert", "Drink"]
DIFFICULTIES = ["Easy", "Medium", "Hard"]
CATEGORY_COLOR = {
    "Breakfast": "#F4A259",
    "Lunch": "#6FB98F",
    "Dinner": "#EF6461",
    "Dessert": "#A288E3",
    "Drink": "#5AA9E6",
}

st.set_page_config(page_title="Recipe Dashboard", page_icon="🍽️", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --accent: #EF6461;
        --bg: #FAFAF8;
        --card: #FFFFFF;
        --text: #2E2E2B;
        --muted: #8A8A84;
        --border: #ECECE6;
    }

    [data-testid="stAppViewContainer"] {
        background-color: var(--bg);
    }
    [data-testid="stSidebar"] {
        background-color: var(--card);
        border-right: 1px solid var(--border);
    }

    h1, h2, h3 { color: var(--text); }

    .card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .card-title { font-size: 1.05rem; font-weight: 600; color: var(--text); margin-bottom: 0.2rem; }
    .card-meta { font-size: 0.85rem; color: var(--muted); }

    .badge {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 600;
        color: #fff;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        margin-bottom: 0.4rem;
    }

    .stat {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.9rem 1rem;
        text-align: center;
    }
    .stat-label { font-size: 0.78rem; color: var(--muted); }
    .stat-value { font-size: 1.5rem; font-weight: 700; color: var(--text); }

    .stButton > button, .stFormSubmitButton > button {
        background-color: var(--accent);
        color: #fff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        background-color: #d9564e;
        color: #fff;
    }

    [data-testid="stPills"] button[aria-selected="true"] {
        background-color: var(--accent) !important;
        border-color: var(--accent) !important;
        color: #fff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
st.sidebar.title("🍽️ Recipe Dashboard")

PAGES = {
    "🏠 Overview": "Overview",
    "➕ Add Recipe": "Add Recipe",
    "🔍 Search by Ingredient": "Search by Ingredient",
    "📖 View All Recipes": "View All Recipes",
    "🎲 Random Recipe": "Random Recipe",
    "⭐ Rate Recipe": "Rate Recipe",
    "🏆 Sort by Rating": "Sort by Rating",
    "🛒 Shopping List": "Shopping List",
}
choice = st.sidebar.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")
page = PAGES[choice]

# NOTE: YummyHub.load_recipes() always returns 0 for its size value, so we
# compute the real size ourselves from the dataframe instead of trusting it.
df, _ = YummyHub.load_recipes()
size = len(df)
if size:
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0.0)


def recipe_card(r, show_rating=False):
    color = CATEGORY_COLOR.get(r["category"], "#999")
    meta = f'{r["preparing time"]} min · {r["difficulty level"]}'
    if show_rating:
        meta += f' · {float(r["rating"]):.1f}★'
    st.markdown(
        f'<div class="card">'
        f'<span class="badge" style="background:{color};">{r["category"]}</span>'
        f'<div class="card-title">{r["name"]}</div>'
        f'<div class="card-meta">{meta}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# KPI strip (every page except Add Recipe)
# ---------------------------------------------------------------------------
if page != "Add Recipe":
    rated = df[df["rating"] > 0] if size else pd.DataFrame()
    avg_rating = f"{rated['rating'].mean():.1f}" if not rated.empty else "—"
    top_category = df["category"].mode()[0] if size else "—"

    k1, k2, k3 = st.columns(3, gap="medium")
    for col, label, value in [
        (k1, "Recipes", size),
        (k2, "Avg. rating", avg_rating),
        (k3, "Top category", top_category),
    ]:
        col.markdown(
            f'<div class="stat"><div class="stat-label">{label}</div>'
            f'<div class="stat-value">{value}</div></div>',
            unsafe_allow_html=True,
        )
    st.write("")

# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------
if page == "Overview":
    st.subheader("Recently added")
    if size == 0:
        st.info("No recipes yet. Add your first one from the sidebar.")
    else:
        for _, r in df.tail(3).iloc[::-1].iterrows():
            recipe_card(r, show_rating=True)

# ---------------------------------------------------------------------------
# Add Recipe
# ---------------------------------------------------------------------------
elif page == "Add Recipe":
    st.subheader("Add a new recipe")
    with st.form("add_recipe_form", clear_on_submit=True):
        name = st.text_input("Recipe name")
        ingredients_raw = st.text_area("Ingredients (one per line, or comma-separated)")
        prep_time = st.number_input("Preparation time (minutes)", min_value=0, step=1)
        instructions_raw = st.text_area("Instructions (one step per line)")
        difficulty = st.selectbox("Difficulty level", DIFFICULTIES)
        category = st.selectbox("Category", CATEGORIES)
        submitted = st.form_submit_button("Save Recipe")

    if submitted:
        if not name.strip():
            st.error("Please enter a recipe name.")
        elif size and name.strip() in df["name"].values:
            st.error(f"'{name.strip()}' already exists. Please choose a different name.")
        elif not ingredients_raw.strip():
            st.error("Please enter at least one ingredient.")
        elif not instructions_raw.strip():
            st.error("Please enter at least one instruction step.")
        else:
            ingredients = [
                item.strip()
                for line in ingredients_raw.splitlines()
                for item in line.split(",")
                if item.strip()
            ]
            instructions = [step.strip() for step in instructions_raw.splitlines() if step.strip()]

            new_recipe = {
                "id": [str(uuid.uuid4())[:6]],
                "name": [name.strip()],
                "ingredients": ["; ".join(ingredients)],
                "preparing time": [int(prep_time)],
                "instructions": ["; ".join(instructions)],
                "difficulty level": [difficulty],
                "category": [category],
                "rating": [None],
            }
            new_df = pd.DataFrame(new_recipe)
            file_exists = os.path.exists(FILE_NAME)
            new_df.to_csv(FILE_NAME, mode="a" if file_exists else "w", header=not file_exists, index=False)
            st.success(f"'{name}' has been added!")

# ---------------------------------------------------------------------------
# Search by Ingredient
# ---------------------------------------------------------------------------
elif page == "Search by Ingredient":
    st.subheader("Search by ingredient")
    if size == 0:
        st.info("No recipes yet.")
    else:
        search_ingredient = st.text_input("Enter an ingredient")
        if search_ingredient:
            matched = df[df["ingredients"].str.lower().str.contains(search_ingredient.lower(), na=False)]
            if matched.empty:
                st.warning("No recipes found with that ingredient.")
            else:
                for _, r in matched.iterrows():
                    recipe_card(r)

# ---------------------------------------------------------------------------
# View All Recipes
# ---------------------------------------------------------------------------
elif page == "View All Recipes":
    st.subheader("All recipes")
    if size == 0:
        st.info("No recipes yet.")
    else:
        cat_filter = st.multiselect("Filter by category", CATEGORIES)
        shown = df[df["category"].isin(cat_filter)] if cat_filter else df
        st.dataframe(
            shown[["name", "category", "preparing time", "difficulty level", "rating"]],
            width="stretch",
            hide_index=True,
        )

# ---------------------------------------------------------------------------
# Random Recipe
# ---------------------------------------------------------------------------
elif page == "Random Recipe":
    st.subheader("Feeling adventurous?")
    if size == 0:
        st.info("No recipes yet.")
    else:
        if st.button("Surprise me"):
            r = df.iloc[randint(0, size - 1)]
            recipe_card(r, show_rating=True)
            st.markdown("**Ingredients**")
            for item in str(r["ingredients"]).split(";"):
                if item.strip():
                    st.markdown(f"- {item.strip()}")
            st.markdown("**Instructions**")
            for i, step in enumerate(str(r["instructions"]).split(";"), start=1):
                if step.strip():
                    st.markdown(f"{i}. {step.strip()}")

# ---------------------------------------------------------------------------
# Rate Recipe
# ---------------------------------------------------------------------------
elif page == "Rate Recipe":
    st.subheader("Rate a recipe")
    if size == 0:
        st.info("No recipes yet.")
    else:
        recipe_name = st.selectbox("Select a recipe", df["name"].tolist())
        new_rating = st.slider("Your rating", min_value=1.0, max_value=5.0, step=0.5, value=3.0)
        if st.button("Submit Rating"):
            idx = df[df["name"] == recipe_name].index[0]
            old_rating = float(df.at[idx, "rating"])
            final_rating = round((old_rating + new_rating) / 2.0, 1) if old_rating > 0.0 else round(new_rating, 1)
            df.at[idx, "rating"] = final_rating
            df.to_csv(FILE_NAME, index=False)
            st.success(f"'{recipe_name}' is now rated {final_rating}/5 stars.")

# ---------------------------------------------------------------------------
# Sort by Rating
# ---------------------------------------------------------------------------
elif page == "Sort by Rating":
    st.subheader("Top rated recipes")
    if size == 0:
        st.info("No recipes yet.")
    else:
        cat_filter = st.multiselect("Filter by category", CATEGORIES)
        rated = df[df["rating"] > 0]
        if cat_filter:
            rated = rated[rated["category"].isin(cat_filter)]
        rated = rated.sort_values(by="rating", ascending=False)
        if rated.empty:
            st.info("No rated recipes match your filter yet.")
        else:
            for _, r in rated.iterrows():
                recipe_card(r, show_rating=True)

# ---------------------------------------------------------------------------
# Shopping List
# ---------------------------------------------------------------------------
elif page == "Shopping List":
    st.subheader("Build a shopping list")
    if size == 0:
        st.info("No recipes yet.")
    else:
        selected_recipes = st.multiselect("Choose recipes", df["name"].tolist())
        if st.button("Generate List"):
            shopping_items = []
            for recipe_name in selected_recipes:
                row = df[df["name"] == recipe_name].iloc[0]
                for item in str(row["ingredients"]).split(";"):
                    item = item.strip()
                    if item and item not in shopping_items:
                        shopping_items.append(item)

            if not shopping_items:
                st.info("Shopping list is empty — select at least one recipe.")
            else:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                for item in shopping_items:
                    st.checkbox(item, key=f"shop_{item}")
                st.markdown("</div>", unsafe_allow_html=True)
