# Some techniques used:
# List Comprehension
# Format Strings
# join()
# Looping using range()
# df.iloc[] and df.loc[]

import pandas as pd

# We put all functions inside their own script to make this script cleaner
from utils import connect_to_db, run_query, convert_data_type_names, clean_query

from download_data import generate_download_links

# Define location of the db
db_dir = 'db.sqlite'
# Define the name of the table to hold the data
table_name = 'results'


def GetResults(link, dropresults):

    # Load data
    df = pd.read_csv(link)
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

    # if statement to decide whether to clear results table or not
    if dropresults == True:
        # Clear the table if it already exists
        run_query(query=f'DROP TABLE IF EXISTS {table_name}', return_data=False, path_to_db=db_dir)
        # Create the table
        query = f"CREATE TABLE {table_name} ({column_description})"
        # Remove any non-alphabet symbols
        query = clean_query(query)
        run_query(query=query, return_data=False, path_to_db=db_dir)
        table_cols = list(data_types.keys())
    else:
        # TODO: Get a list of columns that exist in the table, if we arent recreating it
        res = run_query(query=f'select * from {table_name} limit 1', return_data=True, path_to_db=db_dir)
        data_types2 = dict(res.dtypes)
        table_cols = list(res.columns)

    # Upload the results to a table, row by row. We do this by taking the keys of the dictionary,
    # and joining them together
    column_names = ', '.join(table_cols)
    # Select all columns stored in table_cols, drop everything else

    # Add any columns that exist in the sql table, but dont exist in the new csv
    missing_columns = [col for col in table_cols if col not in df.columns]
    for col in missing_columns:
        df[col] = 'NULL'

    # Drop any columns that exist in the new csv, but not in the sql table.
    df = df[table_cols]

    # Combine the schema of the csv file and the sql file (if we are adding data)
    if dropresults == False:
        data_types = {**data_types, **data_types2}

    for i in range(len(df)):
        # Get the i'th row, convert it to a list
        row = list(df.iloc[i, :])
        for j in range(len(df.columns)):
            # IF the data type is a string, we need to add ' ' around it
            data_type = data_types[df.columns[j]]
            if str(data_type) == 'object':
                row[j] = "'" + str(row[j]) + "'"
        # Convert all elements of the list to strings
        string_row = ", ".join([str(x) for x in row])
        # Add the values to the database
        query = f"INSERT INTO {table_name} ({column_names}) VALUES ({string_row})"
        query = clean_query(query)
        run_query(query=query, return_data=False, path_to_db=db_dir)


if __name__ == '__main__':

    dlinks = generate_download_links(2018, 2020)
    dropcondition = 0 # Set dropcondition to 0

    for footballlinks in dlinks:  # For every element in dlinks, call GetResults and pass the link
        if dropcondition == 0:
            dropresults = True
        else:
            dropresults = False
        dropcondition = dropcondition + 1  # Add 1 to drop condition each time

        GetResults(footballlinks, dropresults)

    # Check that the values have been added
    result = run_query(query=f'select * from {table_name}', return_data=True, path_to_db=db_dir)
