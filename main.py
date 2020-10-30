# Some techniques used:
# List Comprehension
# Format Strings
# join()
# Looping using range()
# df.iloc[] and df.loc[]

import pandas as pd

# We put all functions inside their own script to make this script cleaner
from utils import connect_to_db, run_query, convert_data_type_names, clean_query

# Load data
df = pd.read_csv('data.csv')
# Define the name of the table to hold the data
table_name = 'results'
# Define location of the db
db_dir = 'db.sqlite'
# Create connection to DB
conn = connect_to_db('db.sqlite')
# Create the cursor (which you use to run queries)
cursor = conn.cursor()

# Convert column names to lower case so the names are easier to write.
# The code below is called a 'list comprehension', google it
df.columns = [col.lower() for col in df.columns]
# Convert 'as' to 'away_shots' and 'hs' to 'home_shots'
# We do this because 'as' is a command in SQL so it cant be a column name
df = df.rename(columns={'as': 'away_shots', 'hs': 'home_shots'})
# Get the data types for each of the columns
data_types = dict(df.dtypes)

# Create a description of the columns, used to create the table. Print this to see how it looks.
# This is pretty complicated so dont worry about understanding it, you can also write this by hand as a string
column_description = ''.join([f"{key} {convert_data_type_names(value)}, " for key, value in data_types.items()])
# Remove the ", " from the end of the description
column_description = column_description[:-2]

# Clear the table if it already exists
run_query(query=f'DROP TABLE IF EXISTS {table_name}', return_data=False, path_to_db=db_dir)
# Create the table
query = f"CREATE TABLE {table_name} ({column_description})"
# Remove any non-alphabet symbols
query = clean_query(query)
run_query(query=query, return_data=False, path_to_db=db_dir)

# Upload the results to a table, row by row. We do this by taking the keys of the dictionary,
# and joining them together
column_names = ', '.join([key for key, value in data_types.items()])

for i in range(len(df)):
    # Get the i'th row, convert it to a list
    row = list(df.iloc[i, :])
    for j in range(len(df.columns)):
        data_type = data_types[df.columns[j]]
        if str(data_type) == 'object':
            row[j] = "'" + str(row[j]) + "'"

    # Convert all elements of the list to strings
    string_row = ", ".join([str(x) for x in row])
    # Add the values to the database
    query = f"INSERT INTO {table_name} ({column_names}) VALUES ({string_row})"
    query = clean_query(query)
    run_query(query=query, return_data=False, path_to_db=db_dir)

# Check that the values have been added
result = run_query(query=f'select * from {table_name}', return_data=True, path_to_db=db_dir)
