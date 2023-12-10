import requests
import pycountry
import sqlite3

url = "https://covid-193.p.rapidapi.com/statistics"
database_path = "countryImpact.db"  # Change the path as needed

# Function to check if a row with the same country exists
def row_exists(cursor, country):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS covidData (country, cases, recovered, deaths)
    ''')
    cursor.execute("SELECT COUNT(*) FROM covidData WHERE country = ?", (country,))
    return cursor.fetchone()[0] > 0

# Function to insert data into the SQLite database
def insert_data(conn, country, cases, recovered, deaths):
    cursor = conn.cursor()
    
    # Check if a row with the same country already exists
    if not row_exists(cursor, country):
        # Check for NULL values before inserting
        if None not in (country, cases, recovered, deaths):
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS covidData (country, cases, recovered, deaths)
            ''')
            cursor.execute("INSERT INTO covidData (country, cases, recovered, deaths) VALUES (?, ?, ?, ?)",
                           (country, cases, recovered, deaths))
            conn.commit()
            return True  # Return True if a new row is inserted successfully

    return False  # Return False if a row with the same country already exists or contains NULL values


# Assuming you have a SQLite database connection
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

# Limit the number of rows to be inserted
rows_to_insert = 25
rows_inserted = 0

countryISO = 'fr'
countryName = pycountry.countries.get(alpha_2=countryISO).name
querystring = {"country": countryName}

headers = {
    "X-RapidAPI-Key": "a6d9a1e9c2msh6c79d540ed20982p1b8b9cjsn6c6fab5bac81",
    "X-RapidAPI-Host": "covid-193.p.rapidapi.com"
}

response = requests.get(url, headers=headers)
data = response.json()

for entry in data['response']:
    country_name = entry['country']
    total_cases = entry['cases']['total']
    total_deaths = entry['deaths']['total']
    total_recoveries = entry['cases']['recovered']

    # Insert data into the database if all values are not NULL and there are no duplicates
    if insert_data(conn, country_name, total_cases, total_recoveries, total_deaths):
        rows_inserted += 1

    # Break the loop if the desired number of rows is reached
    if rows_inserted >= rows_to_insert:
        break

# Close the connection
conn.close()
