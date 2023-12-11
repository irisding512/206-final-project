import sqlite3
import os
import requests

db_name = "countryImpact.db"
base_url = "https://api-basketball.p.rapidapi.com/countries"

def setUpTable(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/' + db_name)
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS countries(country_id INTEGER PRIMARY KEY, country_name TEXT)")
    conn.commit()
    return cur, conn

def insertCountryData(cur, conn, country_id, country_name):
    cur.execute("INSERT OR IGNORE INTO countries (country_id, country_name) VALUES (?,?)", (country_id, country_name))
    conn.commit()

cur, conn = setUpTable(db_name)

response = requests.get(base_url, headers={
    "X-RapidAPI-Key": "ab11cf4f3emshbf271858852cbb7p1840f3jsn068c226e4bb7",
    "X-RapidAPI-Host": "api-basketball.p.rapidapi.com"
})

if response.status_code == 200:
    data = response.json()
    countries = data.get('response', [])

    for country in countries:
        country_id = country['id']
        country_name = country['name']

        insertCountryData(cur, conn, country_id, country_name)
        print(f"Data for {country_name} inserted into the database.")

else:
    print(f"Failed to retrieve data. Status code:", response.status_code)
    print("Response content:", response.text)

conn.close()