import unittest
import sqlite3
import json
import os
import matplotlib.pyplot as plt
import requests

db_name = "countryImpact.db"
base_url = 'https://newsdata.io/api/1/news?apikey=pub_34479d289637b0172bf42c8842ddfc21776a8&q=covid'

def setUpTable(db_name):
    # connect to database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()

    # create top stories table
    cur.execute("CREATE TABLE IF NOT EXISTS top_stories(ranking INTEGER, title TEXT PRIMARY KEY, country TEXT, link TEXT)")
    conn.commit()
    return cur, conn

def insertNewsData(cur, conn, ranking, title, country, link):
    # newsdata.io API
    # search by keyword "Covid"
    # 10 articles at a time

    # add top stories into database
    cur.execute("INSERT OR IGNORE INTO top_stories (ranking, title, country, link) VALUES (?,?,?,?)", (ranking, title, country, link))
    conn.commit()

cur, conn = setUpTable(db_name)

response = requests.get(base_url, params=None)

if response.status_code == 200:
    data = response.json()
    stories = data.get('results', [])
    print(stories)

    for index in range(10):
        #check how many rows are in table, in case last value was not inserted b/c it was a duplicate, to get rankings
        cur.execute(f"SELECT COUNT(*) FROM top_stories")
        row_count = cur.fetchone()[0]

        #assign table variables
        ranking = row_count + 1
        title = stories[index]['title']
        country = stories[index]['country'][0].title()
        link = stories[index]['link']

        #insert into table
        insertNewsData(cur, conn, ranking, title, country, link)
        print(f"Data for {country} inserted into the database.")
else:
    print(f"Failed to retrieve data. Status code:", response.status_code)
    print("Response content:", response.text)

conn.close()

