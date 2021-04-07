import pandas as pd
import numpy as np

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
# Lag goals for, so we dont generate features from the game we are trying to predict
# teamform['goalsfor_lagged'] = teamform.groupby('team').goalsfor.shift(1)
# test = teamform.groupby("team").goalsfor_lagged.rolling(5, min_periods=5).mean().reset_index()
# test.columns = ['team', 'id', 'goals_for_l5']
# teamform = pd.merge(teamform, test, how='left', on=['team', 'id'])

def add_rolling_average(df, column='goalsfor', window=5, min_periods=5):
    df[f'{column}_lagged'] = df.groupby('team')[column].shift(1)
    test = df.groupby("team")[f"{column}_lagged"].rolling(window, min_periods).mean().reset_index()
    test.columns = ['team', 'id', f"{column}_l{window}"]
    df = pd.merge(df, test, how='left', on=['team', 'id'])
    df.drop(f'{column}_lagged', axis=1, inplace=True)
    return df

teamform = add_rolling_average(teamform, column='goalsfor', window=5, min_periods=5)
teamform = add_rolling_average(teamform, column='goalsagainst', window=5, min_periods=5)

# Insights and questions:
# The relationship between goals scored and if the team wins next game

# Does a half-time lead make it more likely the team will win?
# Get percent of Full Time wins for Home Teams
percent_of_home_wins = len(result[result["ftr"] == "H"]) / len(result)  # Show bool of if ftr is H
# Get percent of Half Time Leads for Home Teams
percent_of_halftime_lead_h = len(result[result["htr"] == "H"]) / len(result)
percent_of_halftime_lead_d = len(result[result["htr"] == "D"]) / len(result)
percent_of_halftime_lead_a = len(result[result["htr"] == "A"]) / len(result)
# I know that the percent of full time wins for the home team is 46%.
# I found:
# The percent of half time leads for the Home team is 35%.
# The percent of half time draws for the Home team is 37%.
# The percent of half time deficits for the Home team is 27%.
# This suggests that the Home Team is most likely to see the first half out with a draw.
# However, if the Home Team is winning at half time, this does not indicate they will win the game at Full Time.
# It does suggest that the Home Team is more likely to remain level by half-time
# It also suggests the Home Team is more likely to score in the second-half.

# Calculate the Attacking and Defending strength of each team
# Get average goals from last 5 games to determine attacking strength
# Use Pandas Rank to decide the rank and remove human bias
# Compute numerical data ranks (1 through n) along axis
# teamform['default_rank'] = teamform['goals_for_l5'].rank()
# teamform['max_rank'] = teamform['goals_for_l5'].rank(method='max')
# teamform['NA_bottom'] = teamform['goals_for_l5'].rank(na_option='bottom')
teamform['pct_rank'] = teamform['goals_for_l5'].rank(pct=True)

if teamform['pct_rank'] < 0.33:
    attacking_strength_l5 = "low"
elif teamform['pct_rank'] > 0.66:
    attacking_strength_l5 = "high"
else:
    attacking_strength_l5 = "medium"

# Now I need to create the column "attacking_strength_l5" in team form
# Create a list of conditions
conditions = [
    (teamform['pct_rank'] <= 0.33),
    (teamform['pct_rank'] >= 0.66),
    (teamform['pct_rank'] > 0.33) & (teamform['pct_rank'] < 0.66)
     ]

# Create a list of values we want to assign for each condition
attack_form_values = ["low", "high", "medium"]

# Create a new column and use np.select to assign values
teamform["attacking_strength_l5"] = np.select(conditions, attack_form_values)

# Display updated DataFrame
teamform.head()

# Add a Column to check whether the team won or not



# Get average goals conceded in the last 5 games