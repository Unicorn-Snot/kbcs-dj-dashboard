import pandas as pd
from data_loader import load_year_df, SHEETS

# Load all years and tag with a "year" column
dfs = []
for year in SHEETS.keys():
    df_year = load_year_df(year)
    df_year["year"] = year
    dfs.append(df_year)

# Merge into one long dataframe
df_all = pd.concat(dfs, ignore_index=True)
