import pandas as pd
import numpy as np
import plotly.express as pe
import plotly.io as pio
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import sklearn


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
teamform = teamform.sort_values('id')
assert len(teamform) == len(result) * 2  # Testing new dataframe is the correct size

# Make a rolling average window for features
def add_rolling_average(df, column='goalsfor', window=5, min_periods=5):
    # Shift so we dont use the current game score as part of the average
    df[f'{column}_lagged'] = df.groupby('team')[column].shift(1)
    test = df.groupby("team")[f"{column}_lagged"].rolling(window, min_periods).mean().reset_index()
    test.columns = ['team', 'index', f"{column}_l{window}"]
    df['index'] = df.index.copy()
    df = pd.merge(df, test, how='left', on=['team', 'index'])
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

# Create a Ranking function that I can reuse on different columns


def ranking_function(teamform, col_name, new_col_name, ascending=True):

    teamform['pct_rank'] = teamform[col_name].rank(ascending=ascending, pct=True)

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
    teamform[new_col_name] = np.select(conditions, attack_form_values)
    return teamform


teamform = ranking_function(teamform, "goalsfor", "attacking_strength_l5" )
teamform = ranking_function(teamform, "goalsagainst", "defensive_strength_l5", ascending=False)

# Use this to filter results in the teamform dataframe
# liverpool = teamform[teamform['team'] == 'Liverpool']
# HomeTeamsOnly = teamform[teamform['isHome'==True]


# Add a Column to check whether the team won or not
# First define the get_result function


def get_result(x):
    if x['goalsfor'] > x['goalsagainst']:
        return "W"
    elif x['goalsfor'] < x['goalsagainst']:
        return "L"
    else:
        return "D"

# Applies the 'get_result' function to every row in teamform, adds results to a new col called "result"

teamform['result'] = teamform.apply(get_result, axis=1)

# teamform['result'] = teamform.apply(lambda x: get_result(x), axis=1)

# Get average goals conceded in the last 5 games



# VISUALISATION

pio.renderers.default = 'browser'

# Plot goals for each match for home team
import plotly
home_teams = teamform[teamform['ishome']==True]
away_teams = teamform[teamform['ishome']==False]
home_goals = pe.histogram(home_teams, x='goalsfor', title='Goals scored by home team (histogram)')
plotly.offline.plot(home_goals)
away_goals = pe.histogram(away_teams, x='goalsfor', title='Goals scored by away team (histogram)')
plotly.offline.plot(away_goals)


# Plot goals for each match
#plot = pe.histogram(teamform, 'goalsfor')
#plot.show()

# Plot goals against each match
#plot = pe.histogram(teamform, 'goalsagainst')
#plot.show()

#plot = pe.histogram(teamform, 'attacking_strength_l5')
#plot.show()

# this histogram has a poisson distribution, some models assume that features follow a normal distribution
# this might mean we can't use certain models without transforming the feature


# JOIN HOME TEAM AND AWAY TEAM FEATURES ONTO ONE ROW, RATHER THAN HAVING THEM AS SEPERATE RECORDS
# WE DO THIS AS OTHERWISE WE ARE MAKING A PREDICTION WITH HALF OF THE DATA
full_teams = pd.merge(home_teams, away_teams, on=['id', 'date']).reset_index(drop=True)

def assign_result(x):
    if x == 'W':
        return 'H'
    elif x == 'L':
        return 'A'
    else:
        return 'D'

# Add a column for result that is home, draw or away
for i in range(len(full_teams)):
    full_teams.loc[i, 'final_result'] = assign_result(full_teams.loc[i, 'result_x'])


# MODEL BUILDING

# Add feature names here
features = [
        # Home team features
       'goalsfor_l5_x', 'goalsagainst_l5_x', 'pct_rank_x',
       'attacking_strength_l5_x', 'defensive_strength_l5_x',
        # Away team features
       'goalsfor_l5_y', 'goalsagainst_l5_y', 'pct_rank_y',
       'attacking_strength_l5_y', 'defensive_strength_l5_y'
]

# Make sure categorical columns are one-hot encoded (this means trhey only contain 1 or 0). This is because
# models cant deal with string categories
categorical_cols = ['attacking_strength_l5_x', 'defensive_strength_l5_x',
                    'attacking_strength_l5_y', 'defensive_strength_l5_y']
categorical_dummies = pd.get_dummies(full_teams[categorical_cols])
# Add these one-hot encoded columns to the data
full_teams = pd.concat([full_teams.reset_index(drop=True), categorical_dummies.reset_index(drop=True)], axis=1)
# Drop the original columns
full_teams = full_teams.drop(categorical_cols, axis=1)
# Redefine features wit hthe new columns
features = [
        # Home team features
       'goalsfor_l5_x', 'goalsagainst_l5_x',
        # Away team features
       'goalsfor_l5_y', 'goalsagainst_l5_y',
] + list(categorical_dummies.columns)

# Remove null values as  the modcel cant handle them
full_teams = full_teams.dropna()

# Drop null values as the model cant deal with NULLs
y = full_teams['final_result']
X = full_teams[features]

# Scale the data (also known as Standardization). This makes the data have a mean of 0 and a
# standard deviation of 1. This is required by some models, like linear models and neural networks
scaler = sklearn.preprocessing.StandardScaler()
full_teams[features] = scaler.fit_transform(full_teams[features])

# Split data into test and train
X_train, X_test, y_train, y_test = train_test_split(full_teams[features], full_teams['final_result'])

# Create a random forest classifier
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier()

model.fit(X_train, y_train)

# Generate new predictions
preds = model.predict(X_test)

# Evaluate model in terms of roc_auc
from sklearn.metrics import accuracy_score
score = accuracy_score(y_test, preds)

