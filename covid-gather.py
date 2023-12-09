import requests
import pycountry
import sqlite3

url = "https://covid-193.p.rapidapi.com/statistics"
database_path = "covid19_data.db"  # Change the path as needed

# Function to insert data into the SQLite database
def insert_data(country, cases, recovered, deaths):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO covid19_data (country, cases, recovered, deaths)
        VALUES (?, ?, ?, ?)
    ''', (country, cases, recovered, deaths))
    conn.commit()
    conn.close()

countryISO = 'fr'
countryName = pycountry.countries.get(alpha_2=countryISO).name
#print(countryName, '\n')
querystring = {"country": countryName}

headers = {
    "X-RapidAPI-Key": "a6d9a1e9c2msh6c79d540ed20982p1b8b9cjsn6c6fab5bac81",
    "X-RapidAPI-Host": "covid-193.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

if response.status_code == 200:
    data = response.json()
    statistics = data.get('response', [])[0]

    # Extract relevant information
    cases = statistics['cases']['total']
    recovered = statistics['cases']['recovered']
    deaths = statistics['deaths']['total']

    # Insert data into the database
    insert_data(countryName, cases, recovered, deaths)
    print(f"Data for {countryName} inserted into the database.")
else:
    print(f"Failed to retrieve data for {countryName}. Status code:", response.status_code)
    print("Response content:", response.text)
