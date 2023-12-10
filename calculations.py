import unittest
import sqlite3
import json
import os
import matplotlib.pyplot as plt
import requests

db_name = "countryImpact.db"
base_url = "https://newsdata.io/api/1/news?apikey=pub_34479d289637b0172bf42c8842ddfc21776a8&qInTitle=health"

def setUpTable(db_name):
    # connect to database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS top_countries_in_stories(country TEXT PRIMARY KEY, count INTEGER)")
    conn.commit()
    return cur, conn


def countCountries(cur, conn):
    # Count how many times each country appears in the top_stories table
    cur.execute("SELECT country, COUNT(country) FROM top_stories GROUP BY country ORDER BY COUNT(country) DESC")
    country_counts = cur.fetchall()

    # Print the results
    for country, count in country_counts:
        print(f"{country}: {count} times")
        cur.execute("INSERT OR IGNORE INTO top_countries_in_stories (country, count) VALUES (?,?)", (country, count))
    conn.commit()

cur, conn = setUpTable(db_name)
countCountries(cur, conn)
conn.close()
        