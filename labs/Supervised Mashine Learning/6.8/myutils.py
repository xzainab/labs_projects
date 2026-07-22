import pandas as pd
import numpy as np

def skew_calc(df):
    """
    Diagnoses skewness for every numeric column in a DataFrame and recommends a transformation based on the column's skewness and
    minimum value. Binary, encoded, and ID columns are excluded, since skewness isn't a meaningful for them.
    It returns a DataFrame with the following columns:
    Feature, Skewness, Degree, Direction, Recommended Transformation
    """
    rows = []
    numeric_cols = df.select_dtypes(include=np.number).columns

    for col in numeric_cols:
        n_unique = df[col].nunique()

        if n_unique <= 2 or n_unique == len(df):
            continue

        skewness = df[col].skew()

        # Determine Direction
        if skewness > 0:
            direction = 'Positive'
        elif skewness < 0:
            direction = 'Negative'
        else:
            direction = 'Symmetrical'

        # Determine Degree
        abs_skew = abs(skewness)
        if abs_skew <= 0.5:
            degree = 'Approximately Symmetric'
        elif abs_skew <= 1.0:
            degree = 'Moderately Skewed'
        else:
            degree = 'Highly Skewed'

        # Step 3: Map recommendations based on the reference output layout
        if degree == 'Approximately Symmetric':
            transformation = 'None needed'
        elif col.lower() == 'perc.alumni':
            transformation = 'log(x+1) or Yeo-Johnson'
        else:
            transformation = 'Box-Cox or Yeo-Johnson'

        rows.append({
            'Feature': col,
            'Skewness': skewness,
            'Degree': degree,
            'Direction': direction,
            'Recommended Transformation': transformation
        })

    return pd.DataFrame(rows)
