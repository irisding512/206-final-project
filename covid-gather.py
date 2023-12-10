import requests
import pycountry
import sqlite3

url = "https://covid-193.p.rapidapi.com/statistics"
database_path = "countryImpact.db"  # Change the path as needed

# Function to check if a row with the same country exists in covidData table
def row_exists(cursor, country_id):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS covidData (country_id INTEGER, cases INTEGER, recovered INTEGER, deaths INTEGER)
    ''')
    cursor.execute("SELECT COUNT(*) FROM covidData WHERE country_id = ?", (country_id,))
    return cursor.fetchone()[0] > 0

# Function to check if a row with the same country_id exists in countryKeys table
def country_key_exists(cursor, country_id):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS countryKeys (country_id INTEGER, country_name TEXT)
    ''')
    cursor.execute("SELECT COUNT(*) FROM countryKeys WHERE country_id = ?", (country_id,))
    return cursor.fetchone()[0] > 0

# Function to insert data into the SQLite database
def insert_data(conn, country_id, cases, recovered, deaths):
    cursor = conn.cursor()
    
    # Check if a row with the same country_id already exists
    if not row_exists(cursor, country_id):
        # Check for NULL values before inserting
        if None not in (country_id, cases, recovered, deaths):
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS covidData (country_id INTEGER, cases INTEGER, recovered INTEGER, deaths INTEGER)
            ''')
            cursor.execute("INSERT INTO covidData (country_id, cases, recovered, deaths) VALUES (?, ?, ?, ?)",
                           (country_id, cases, recovered, deaths))
            conn.commit()
            return True  # Return True if a new row is inserted successfully

    return False  # Return False if a row with the same country_id already exists or contains NULL values

# Function to insert data into the countryKeys table
def insert_country_key(conn, country_id, country_name):
    cursor = conn.cursor()
    
    # Check if a row with the same country_id already exists
    if not country_key_exists(cursor, country_id):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS countryKeys (country_id INTEGER, country_name TEXT)
        ''')
        cursor.execute("INSERT INTO countryKeys (country_id, country_name) VALUES (?, ?)",
                       (country_id, country_name))
        conn.commit()
        return True  # Return True if a new row is inserted successfully

    return False  # Return False if a row with the same country_id already exists or contains NULL values

# Assuming you have a SQLite database connection
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS countryKeys (country_id INTEGER, country_name TEXT)
''')

# Find the last inserted country_id
cursor.execute("SELECT MAX(country_id) FROM countryKeys")
last_inserted_country_id = cursor.fetchone()[0]

# Set the starting country_id for the current run
current_country_id = last_inserted_country_id + 1 if last_inserted_country_id is not None else 1

# Limit the number of rows to be inserted
rows_to_insert = 25
rows_inserted = 0

# Make the API request and retrieve the data
countryISO = 'fr'
countryName = pycountry.countries.get(alpha_2=countryISO).name
querystring = {"country": countryName}

headers = {
    "X-RapidAPI-Key": "a6d9a1e9c2msh6c79d540ed20982p1b8b9cjsn6c6fab5bac81",
    "X-RapidAPI-Host": "covid-193.p.rapidapi.com"
}

response = requests.get(url, headers=headers)
data = response.json()

# Iterate over the data and insert into the database
for entry in data['response']:
    country_name = entry['country']
    total_cases = entry['cases']['total']
    total_deaths = entry['deaths']['total']
    total_recoveries = entry['cases']['recovered']

    # Insert data into the covidData table if all values are not NULL and there are no duplicates
    if insert_data(conn, current_country_id, total_cases, total_recoveries, total_deaths):
        # Insert data into the countryKeys table if all values are not NULL and there are no duplicates
        insert_country_key(conn, current_country_id, country_name)
        rows_inserted += 1

        current_country_id += 1  # Increment country_id only if the row is inserted

    # Break the loop if the desired number of rows is reached
    if rows_inserted >= rows_to_insert:
        break

# Close the connection
conn.close()
