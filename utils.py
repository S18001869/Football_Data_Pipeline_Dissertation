import os
import re
import sqlite3
import pandas as pd


def connect_to_db(path_to_db):
    """Connect to local sqlite3 database
    """
    # Establish a connection to the database
    if not os.path.exists(path_to_db):  # Check if the path to the DB exists
        print('DB not found, creating DB at this location')
    conn = sqlite3.connect(path_to_db)
    # Return the connection object to use in queries
    return conn


def run_query(*, query, params=None, return_data=True, path_to_db=None) -> pd.DataFrame:
    """Function to run a query on the DB while still keeping the column names. Returns a DataFrame
    """
    # Create connection object
    conn = connect_to_db(path_to_db)
    # Create cursor (which you use to run queries)
    cursor = conn.cursor()
    # Run query
    cursor.execute(query, params if params is not None else [])
    # Commit any changes
    conn.commit()
    # Get column names and apply to the data frame
    if return_data:
        names = cursor.description  # Get the column names
        name_list = []
        for name in names:
            name_list.append(name[0])  # Add the column names to a list
        # Convert the result into a DataFrame and add column names
        df = pd.DataFrame(cursor.fetchall(), columns=name_list)
        conn.close()
        return df
    # Close the connection
    conn.close()


def convert_data_type_names(x):
    """Convert the python data type names into the sqlite data type names
    """
    # Make sure x is a string
    x = str(x)
    if 'object' in x:
        return 'TEXT'
    elif 'float' in x:
        return 'REAL'
    elif 'int' in x:
        return 'INTEGER'


def clean_query(query):
    """Remove any non-alphabetic symbols from query text
    """
    query = query.replace('<', 'u')
    query = query.replace('>', 'o')
    query = query.replace('nan', 'NULL')
    # Define all the symbols we want to be allowed in the text
    regex = re.compile("[^a-zA-Z0123456789 ,()_']")
    # Replace any characters that arent defined above, with nothing
    # First parameter is the replacement, second parameter is your input string
    return regex.sub('', query)
