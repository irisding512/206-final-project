<<<<<<< HEAD
            ranking = before_row_count + 1
=======
import requests
import pycountry
import sqlite3

url = "https://covid-193.p.rapidapi.com/statistics"
database_path = "countryImpact.db"  # Change the path as needed

# Function to check if a row with the same country exists in covidData table
def row_exists(cursor, country_id):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS covidData (country_id INTEGER, cases INTEGER, recovered INTEGER, deaths INTEGER, inserted INTEGER)
    ''')
    cursor.execute("SELECT COUNT(*) FROM covidData WHERE country_id = ? AND inserted = 1", (country_id,))
    return cursor.fetchone()[0] > 0

# Function to insert data into the SQLite database
def insert_data(conn, country_id, cases, recovered, deaths):
    cursor = conn.cursor()

    # Check if a row with the same country_id has already been inserted
    if not row_exists(cursor, country_id):
        # Check for NULL values before inserting
        if None not in (country_id, cases, recovered, deaths):
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS covidData (country_id INTEGER, cases INTEGER, recovered INTEGER, deaths INTEGER, inserted INTEGER)
            ''')
            cursor.execute("INSERT INTO covidData (country_id, cases, recovered, deaths, inserted) VALUES (?, ?, ?, ?, 1)",
                           (country_id, cases, recovered, deaths))
            conn.commit()
            return True  # Return True if a new row is inserted successfully

    return False  # Return False if a row with the same country_id has already been inserted or contains NULL values

# Assuming you have a SQLite database connection
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

# Limit the number of rows to be inserted
rows_to_insert = 25
rows_inserted = 0

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

# Iterate over the data and insert into the database
for entry in data['response']:
    country_id = entry['country']
    total_cases = entry['cases']['total']
    total_deaths = entry['deaths']['total']
    total_recoveries = entry['cases']['recovered']

    # Insert data into the covidData table if all values are not NULL and haven't been inserted yet
    if insert_data(conn, country_id, total_cases, total_recoveries, total_deaths):
        rows_inserted += 1

    # Break the loop if the desired number of rows is reached
    if rows_inserted >= rows_to_insert:
        break

# Close the connection
conn.close()
>>>>>>> 10d80b4ad4a091dc3fe727079cd86f9328d578f2
