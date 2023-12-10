import requests
import pycountry
import sqlite3

url = "https://covid-193.p.rapidapi.com/statistics"
database_path = "countryImpact.db"  # Change the path as needed

# Function to check if a row with the same country_id has been inserted in covidData table
def row_exists(cursor, country_id):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS covidData (country_id INTEGER, cases INTEGER, recovered INTEGER, deaths INTEGER, inserted INTEGER)
    ''')
    cursor.execute("SELECT COUNT(*) FROM covidData WHERE country_id = ? AND inserted = 1", (country_id,))
    return cursor.fetchone()[0] > 0

# Function to check if a row with the same country_id exists in countryKeys table
def country_key_exists(cursor, country_id):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS countryKeys (country_name TEXT PRIMARY KEY, country_id INTEGER)
    ''')
    cursor.execute("SELECT COUNT(*) FROM countryKeys WHERE country_id = ?", (country_id,))
    return cursor.fetchone()[0] > 0

# Function to insert data into the SQLite database
def insert_data(conn, country_id, cases, recovered, deaths):
    cursor = conn.cursor()

    # Check if a row with the same country_id has already been inserted
    if not row_exists(cursor, country_id):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS covidData (country_id INTEGER, cases INTEGER, recovered INTEGER, deaths INTEGER, inserted INTEGER)
        ''')
        cursor.execute("INSERT INTO covidData (country_id, cases, recovered, deaths, inserted) VALUES (?, ?, ?, ?, 1)",
                       (country_id, cases, recovered, deaths))
        conn.commit()
        return True  # Return True if a new row is inserted successfully

    return False  # Return False if a row with the same country_id has already been inserted
# Function to insert data into the countryKeys table
def insert_country_key(conn, country_id, country_name):
    cursor = conn.cursor()

    # Check if a row with the same country_id already exists
    if not country_key_exists(cursor, country_id):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS countryKeys (country_name TEXT PRIMARY KEY, country_id INTEGER)
        ''')
        cursor.execute("INSERT INTO countryKeys (country_name, country_id) VALUES (?, ?)",
                       (country_id, country_name))
        conn.commit()
        return True  # Return True if a new row is inserted successfully

    return False  # Return False if a row with the same country_id already exists or contains NULL values

# Function to get the next available country_id
def get_next_country_id(cursor):
    cursor.execute("SELECT MAX(country_id) FROM countryKeys")
    last_inserted_country_id = cursor.fetchone()[0]
    return last_inserted_country_id + 1 if last_inserted_country_id is not None else 1

# Function to get the set of countries that have already been inserted
def get_inserted_countries(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT country_name FROM countryKeys")
    return set(row[0] for row in cursor.fetchall())

# Assuming you have a SQLite database connection
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

# Ensure the existence of the covidData and countryKeys tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS covidData (country_id INTEGER, cases INTEGER, recovered INTEGER, deaths INTEGER, inserted INTEGER)
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS countryKeys (country_name TEXT PRIMARY KEY, country_id INTEGER)
''')

# Get the set of countries that have already been inserted
inserted_countries = get_inserted_countries(conn)

# Limit the number of rows to be inserted
rows_to_insert = 25
rows_inserted = 0

# Get the next available country_id
current_country_id = get_next_country_id(cursor)

# Make the API request and retrieve the data for entries that haven't been inserted yet
# countryISO = 'fr'
# countryName = pycountry.countries.get(alpha_2=countryISO).name
# querystring = {"country": countryName}

headers = {
    "X-RapidAPI-Key": "a6d9a1e9c2msh6c79d540ed20982p1b8b9cjsn6c6fab5bac81",
    "X-RapidAPI-Host": "covid-193.p.rapidapi.com"
}

response = requests.get(url, headers=headers)
data = response.json()


for entry in data['response']:
    original_country_name = entry['country']
    
    # Replace dashes with spaces in the country name
    country_name = original_country_name.replace('-', ' ')
    
    if country_name not in inserted_countries:
        total_cases = entry['cases']['total']
        total_deaths = entry['deaths']['total']
        total_recoveries = entry['cases']['recovered']

        # Insert data into the covidData table if all values are not NULL and haven't been inserted yet
        if insert_data(conn, current_country_id, total_cases, total_recoveries, total_deaths):
            # Insert data into the countryKeys table if all values are not NULL and there are no duplicates
            insert_country_key(conn, country_name, current_country_id)
            rows_inserted += 1

            # Update the set of inserted countries
            inserted_countries.add(country_name)  # Use lowercase

            # Increment the country_id
            current_country_id += 1

        # Break the loop if the desired number of rows is reached
        if rows_inserted >= rows_to_insert:
            break


# Close the connection
conn.close()
