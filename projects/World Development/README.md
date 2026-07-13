# World Development Statistics: Identifying Hollow Growth Countries (1960–2020)

## Project Overview

Economic growth does not always translate into improvements in people's quality of life. Some countries experience increasing income while life expectancy improves slowly, or rapid population growth reduces the impact of economic progress. This project analyzes historical world development indicators between 1960 and 2020 to identify countries experiencing **Hollow Growth**.

The analysis combines Gross National Income (GNI), life expectancy, and population data to evaluate long-term development patterns and support evidence-based funding decisions. Three raw Gapminder datasets were cleaned, reshaped, and merged into a single analysis-ready dataset, changes in each indicator were calculated between 1960 and 2020, and countries were classified into four development categories using a quartile-based rule. Out of 125 countries with complete data for both years, the analysis found that the vast majority (94) show **Balanced Development**, 20 show **Economic Growth Only**, 10 are flagged as **Potential Hollow Growth**, and exactly **1 country (Argentina)** meets all three criteria for **Hollow Growth**.

These findings suggest that, globally, economic growth has generally been accompanied by health improvements, but a meaningful minority of countries warrant closer monitoring, and targeted funding should prioritize the countries showing the clearest signs of hollow growth.

---

## Problem Statement

Economic growth can sometimes hide underlying development challenges, such as limited improvements in life expectancy or rapid population growth. The objective of this project is to analyze historical trends in GNI, life expectancy, and population between 1960 and 2020 to identify countries experiencing **Hollow Growth**, helping policymakers prioritize development funding where it is most needed.

---

## Project Objectives

- Clean and prepare multiple world development datasets.
- Merge GNI, life expectancy, and population into a single dataset.
- Explore historical development trends from 1960 to 2020.
- Measure changes in development indicators over time.
- Classify countries according to their development patterns.
- Identify countries experiencing Hollow Growth.
- Provide recommendations based on the analysis.

---

## File Directory

| File / Folder | Description |
|---|---|
| `README.md` | This file — project overview, summary, and findings. |
| `Code/World_Development.ipynb` | Main Jupyter notebook containing all data cleaning, merging, EDA, classification, and conclusions. |
| `Data/gni_per_cap_atlas_method_con2021.csv` | Raw GNI per capita data (wide format, Gapminder). |
| `Data/life_expectancy.csv` | Raw life expectancy data (wide format, Gapminder). |
| `Data/population.csv` | Raw population data (wide format, Gapminder). |
| `Data/world_development_cleaned.csv` | Cleaned, merged dataset (long format) covering 1960–2020, with no missing values. |
| `Data/hollow_growth_analysis.csv` | Final dataset with 1960 vs. 2020 values, calculated changes, and each country's Hollow Growth classification. |
| `Presentation/` | Slide deck (PDF) summarizing the project for a non-technical audience. |

> **Note:** Adjust the paths above if your local folder structure differs — the notebook currently reads/writes files using the relative path `./data/`.

---

## Data & Data Dictionary

This project uses three datasets sourced from **Gapminder** (https://www.gapminder.org/), originally provided in wide format (one column per year).

| Dataset | Description |
|---|---|
| GNI per Capita | Gross National Income (Atlas Method, constant 2021 US$), per country per year. |
| Life Expectancy | Average life expectancy at birth (years), per country per year. |
| Population | Total population, per country per year (originally stored with `K`/`M`/`B` suffixes and converted to numeric). |

The analysis focuses on the period from **1960 to 2020**.

### Data Dictionary — `world_development_cleaned.csv`

| Column | Type | Description |
|---|---|---|
| `country` | string | Country name. |
| `year` | int | Year of observation (1960–2020). |
| `GNI` | float | Gross National Income per capita (Atlas Method, constant 2021 US$). |
| `life_expectancy` | float | Life expectancy at birth, in years. |
| `population` | float | Total population (converted from `K`/`M`/`B` suffixes to full numeric values). |

### Data Dictionary — `hollow_growth_analysis.csv` (engineered features)

| Column | Type | Description |
|---|---|---|
| `country` | string | Country name. |
| `GNI_1960` / `GNI_2020` | float | GNI per capita in 1960 and 2020. |
| `life_expectancy_1960` / `life_expectancy_2020` | float | Life expectancy in 1960 and 2020. |
| `population_1960` / `population_2020` | float | Population in 1960 and 2020. |
| `GNI_change` | float | **Engineered feature.** `GNI_2020 − GNI_1960`. |
| `life_expectancy_change` | float | **Engineered feature.** `life_expectancy_2020 − life_expectancy_1960`. |
| `population_change` | float | **Engineered feature.** `population_2020 − population_1960`. |
| `Hollow_Growth` | string | **Engineered feature.** Classification label: `Hollow Growth`, `Potential Hollow Growth`, `Economic Growth Only`, or `Balanced Development` (see methodology below). |

---

## Data Preparation

The following preprocessing steps were performed:

- Loaded the three datasets using Pandas.
- Explored each dataset's shape, structure, data types, and missing values.
- Converted each dataset from wide format to long format (`pd.melt`).
- Renamed columns for consistency (`GNI`, `life_expectancy`, `population`).
- Converted population values (stored with `K`/`M`/`B` suffixes) into numeric format using a custom parsing function.
- Converted `year` to integer type across all datasets.
- Merged the three datasets on `country` and `year` into a single dataframe.
- Filtered the dataset to include only data between **1960 and 2020**.
- Investigated missing values using `missingno` matrix and heatmap visualizations to check for patterns.
- Removed rows with any missing values (GNI, life expectancy, or population) rather than imputing, since imputing yearly time-series values (e.g., with the mean) would distort each country's historical trend.
- Verified the cleaned dataset: **8,892 complete observations** across the 1960–2020 period.

---

## Exploratory Data Analysis

Several visualizations were created to better understand the data:

- Average GNI over time (1960–2020).
- Average life expectancy over time (1960–2020).
- Relationship between GNI and life expectancy (scatter plot).
- Relationship between GNI and life expectancy specifically in 2020.
- Distribution of GNI change (1960 vs. 2020).
- Distribution of life expectancy change (1960 vs. 2020).
- Distribution of population change (1960 vs. 2020).
- Missing-value matrix and correlation heatmap (`missingno`), used during data cleaning.
- Bar chart of the number of countries in each development category.

These visualizations provided insight into global development trends and highlighted differences between countries.

---

## Hollow Growth Classification — Methodology

Development changes between 1960 and 2020 were calculated for every country by merging each country's 1960 values with its 2020 values and taking the difference:

- `GNI_change = GNI_2020 − GNI_1960`
- `life_expectancy_change = life_expectancy_2020 − life_expectancy_1960`
- `population_change = population_2020 − population_1960`

Countries were then classified using quartile-based thresholds calculated from the dataset itself:

| Indicator | 25th Percentile (Q1) | 75th Percentile (Q3) |
|---|---|---|
| GNI change | 356.0 | 3,270.0 |
| Life expectancy change | 11.7 | 22.3 |
| Population change | 1,180,000 | 24,410,000 |

- **High GNI Growth**: `GNI_change` above Q3 (3,270.0)
- **Low Life Expectancy Growth**: `life_expectancy_change` below Q1 (11.7)
- **High Population Growth**: `population_change` above Q3 (24,410,000)

Based on these conditions, each country was assigned to one of the following categories, in order of priority:

1. **Hollow Growth** — High GNI growth **and** low life expectancy growth **and** high population growth.
2. **Potential Hollow Growth** — High GNI growth **and** low life expectancy growth (but not high population growth).
3. **Economic Growth Only** — High GNI growth only (life expectancy growth was not low).
4. **Balanced Development** — All other countries (did not meet the high-GNI-growth condition, or growth was broadly consistent across indicators).

---

## Key Findings

The analysis revealed several important insights:

- Of the 125 countries with complete 1960 and 2020 data, the distribution across categories was:

  | Category | Number of Countries |
  |---|---|
  | Balanced Development | 94 |
  | Economic Growth Only | 20 |
  | Potential Hollow Growth | 10 |
  | Hollow Growth | 1 |

- Most countries experienced **Balanced Development**, indicating that economic growth was generally accompanied by improvements in life expectancy.
- A smaller group of countries (20) showed **Economic Growth Only**, where income increased substantially without meeting the criteria for balanced development.
- 10 countries were classified as **Potential Hollow Growth**, suggesting possible development imbalance that should be monitored.
- **Argentina** was identified as the only country satisfying all three Hollow Growth criteria (high GNI growth, low life expectancy growth, and high population growth) based on the selected thresholds.
- The relationship between GNI and life expectancy was generally positive, although several countries deviated from this trend.
- Population growth varied considerably across countries, with a few countries experiencing exceptionally large increases.

---

## Important Visualizations

Below are the key visualizations that support the findings above (all generated in `Code/World_Development.ipynb`):

- **Average GNI over time (1960–2020)** — shows a steady global upward trend in income per capita.
- **Average life expectancy over time (1960–2020)** — shows consistent global gains in life expectancy.
- **GNI vs. life expectancy scatter plot** — illustrates the generally positive relationship between income and health outcomes, with some notable outliers.
- **Development category bar chart** — visually confirms that Balanced Development is by far the most common outcome, while Hollow Growth is rare (1 out of 125 countries).

> Note: static copies of these charts (as PNG images) can be added to a `Presentation/images/` folder and referenced here if you want them to render directly inside this README.

---

## Conclusions & Recommendations

**Conclusion:** Between 1960 and 2020, most countries achieved balanced development — economic growth was generally matched by gains in life expectancy. However, a smaller set of countries prioritized economic growth without proportional health gains, and one country (Argentina) matched the full Hollow Growth profile under the thresholds used here.

**Recommendations:**

- Prioritize development funding for countries classified as **Hollow Growth** (currently: Argentina).
- Continuously monitor the 10 countries classified as **Potential Hollow Growth**, as they may be at risk of shifting into full Hollow Growth.
- Complement economic investment with healthcare and public health initiatives, rather than income support alone.
- Continue tracking development indicators regularly (ideally on a rolling basis rather than a single 1960-vs-2020 snapshot) to support evidence-based policy decisions.

---

## Areas for Further Research/Study

- **Rolling/multi-period analysis**: This project compares only two snapshots (1960 and 2020). A rolling-window or decade-by-decade analysis could reveal whether "hollow growth" episodes are temporary or persistent for a given country.
- **Additional indicators**: Incorporating indicators such as education, income inequality (Gini coefficient), infant mortality, or healthcare spending could refine the classification and reduce reliance on only three variables.
- **Threshold sensitivity**: The classification depends on quartile thresholds calculated from this specific sample of 125 countries. Testing alternative thresholds (e.g., fixed cutoffs, or percentiles calculated on a larger/different country set) would help assess how sensitive the results are to this choice.
- **Regional analysis**: Grouping countries by region or income bracket before applying quartile thresholds could surface hollow growth patterns that are masked when compared globally.
- **Causality**: This analysis is descriptive/correlational. Further research (e.g., regression or causal inference methods) would be needed to understand *why* certain countries experienced hollow growth.

---

## Technologies Used

- Python
- Pandas
- Matplotlib
- Seaborn
- missingno
- Jupyter Notebook

---

## Final Output Files

The project produces two processed datasets:

| File | Description |
|---|---|
| **world_development_cleaned.csv** | Cleaned dataset containing GNI, life expectancy, and population for all countries between 1960 and 2020. |
| **hollow_growth_analysis.csv** | Final dataset containing 1960 vs. 2020 values, calculated development changes, and Hollow Growth classification for each country. |

---

## Sources

- Gapminder Foundation — https://www.gapminder.org/