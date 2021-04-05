import pandas as pd

# We put all functions inside their own script to make this script cleaner
from utils import connect_to_db, run_query, convert_data_type_names, clean_query

from download_data import generate_download_links

# Define location of the db
db_dir = 'db.sqlite'
# Define the name of the table to hold the data
table_name = 'results'

result = run_query(query=f'select * from {table_name}', return_data=True, path_to_db=db_dir)

# Does Home Advantage play a part in winning the game?
# Percent of times the home team wins compared to draw and away win
percent_of_home_wins = len(result[result["ftr"] == "H"]) / len(result)  # Show bool of if ftr is H
percent_of_home_draws = len(result[result["ftr"] == "D"]) / len(result)  # Show bool of if ftr is D
percent_of_home_loss = len(result[result["ftr"] == "A"]) / len(result)  # Show bool of if ftr is A
assert percent_of_home_wins + percent_of_home_draws + percent_of_home_loss == 1, ""
# Check percentage includes 100% games
# Insights:
# When the team plays at home, the team wins 46% of the time.
# When the teams at home, it's x % more likely to win.

# Is Team Form a good predictor of whether the team will win their next game?
# Team Form based on the Home Goals in previous 5 games
result.groupby("hometeam").fthg.rolling(
    5, min_periods=5, center=False, win_type=None, on=None, axis=0, closed=None).mean()
# This is okay, but I want overall form
# I need one row per team per game to find the Home Form value
result["id"] = result.index
homecols = ["id", "date", "hometeam", "fthg", "ftag"]
homecolsnew = ["id", "date", "team", "goalsfor", "goalsagainst"]
df_home = result[homecols]
df_home.columns=homecolsnew
df_home.loc[:, "ishome"] = True

# Team Form based on the Away Goals in previous 5 games
awaycols = ["id", "date", "awayteam", "ftag", "fthg"]
awaycolsnew = ["id", "date", "team", "goalsfor", "goalsagainst"]
df_away = result[awaycols]
df_away.columns=awaycolsnew
df_away.loc[:, "ishome"] = False

# Split home and away teams into individual rows
teamform = df_home
teamform = teamform.append(df_away)
assert len(teamform) == len(result) * 2  # Testing new dataframe is the correct size

# Team Form for past 5 games (excluding most recent game)
test = teamform.groupby("team").goalsfor.rolling(
    5, min_periods=5, center=False, win_type=None, on=None, axis=0, closed=None).mean().shift(1).reset_index()
test.columns = ['team', 'id', 'goals_for_l5']
teamform = pd.merge(teamform, test, how='left', on=['team', 'id'])
# TODO: FIX SHIFT BUG
# Insights and questions:
# The relationship between goals scored and if the team wins next game

