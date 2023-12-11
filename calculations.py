import unittest
import sqlite3
import json
import os
import matplotlib.pyplot as plt
import requests

db_name = "countryImpact.db"
base_url = "https://newsdata.io/api/1/news?apikey=pub_34479d289637b0172bf42c8842ddfc21776a8&qInTitle=health"

#country counts in news stories

def setUpCountryCountsTable(db_name):
    # connect to database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS top_countries_in_stories(country_id INTEGER PRIMARY KEY, count INTEGER)")
    conn.commit()
    return cur, conn


def countCountries(cur, conn):
    # count how many times each country appears in the top_stories table
    cur.execute("SELECT country_id, COUNT(country_id) FROM latest_stories GROUP BY country_id ORDER BY COUNT(country_id) DESC")
    country_counts = cur.fetchall()

    # print the results
    for country, count in country_counts:
        print(f"{country}: {count} times")
        cur.execute("INSERT OR IGNORE INTO top_countries_in_stories (country_id, count) VALUES (?,?)", (country, count))
    conn.commit()

cur, conn = setUpCountryCountsTable(db_name)
countCountries(cur, conn)
conn.close()

PUTTING THIS OVER HERE FOR NOW!


# Perform calculations for recovery percentage
# Create a table named "recoveryPercent" if it doesn't exist
db_name = "countryImpact.db"
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/'+db_name)
cur = conn.cursor()
cur.execute('''
    CREATE TABLE IF NOT EXISTS recoveryPercent (
        country_id INTEGER PRIMARY KEY,
        cases INTEGER,
        recovered INTEGER,
        recovery_percentage REAL
    )
''')

# Insert calculated data into the "recoveryPercent" table
cur.execute('''
    INSERT OR REPLACE INTO recoveryPercent (country_id, cases, recovered, recovery_percentage)
    SELECT cd.country_id, cd.cases, cd.recovered, (cd.recovered * 100.0 / cd.cases) AS recovery_percentage
    FROM covidData cd
    JOIN countryKeys ck ON cd.country_id = ck.country_id
''')

results = cur.fetchall()

# Write calculated data to a text file
output_file_path = "recovery_percentage_data.txt"
with open(output_file_path, "w") as output_file:
    for result in results:
        country_id, cases, recovered, recovery_percentage = result
        output_file.write(f"Country ID: {country_id}, Cases: {cases}, Recovered: {recovered}, Recovery Percentage: {recovery_percentage:.2f}%\n")


# Commit the changes
conn.commit()

# Close the connection
conn.close()