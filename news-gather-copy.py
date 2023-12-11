import unittest
import sqlite3
import json
import os
import matplotlib.pyplot as plt
import requests
from newsdataapi import NewsDataApiClient

api = NewsDataApiClient(apikey='pub_34479d289637b0172bf42c8842ddfc21776a8')

db_name = "countryImpact.db"
base_url = "https://newsdata.io/api/1/news?apikey=pub_34479d289637b0172bf42c8842ddfc21776a8&qInTitle=health"

def setUpTable(db_name):
    # connect to database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()

    # create top stories table
    cur.execute("CREATE TABLE IF NOT EXISTS top_latest_stories(ranking INTEGER, title TEXT PRIMARY KEY, country TEXT, link TEXT)")
    conn.commit()
    return cur, conn

def insertNewsData(cur, conn, ranking, title, country, link):
    # newsdata.io API
    # search by keyword "health"
    # 10 articles at a time

    # add top stories into database
    cur.execute("INSERT OR IGNORE INTO top_latest_stories (ranking, title, country, link) VALUES (?,?,?,?)", (ranking, title, country, link))
    conn.commit()

cur, conn = setUpTable(db_name)

response = api.news_api()

stories = response.get('results', [])

#checks how many rows have been added to table so far
cur.execute(f"SELECT COUNT(*) FROM top_latest_stories")
initial_row_count = cur.fetchone()[0]

#returns 10 stories (sometimes can be duplicates)
for index in range(10):
    #check how many rows are in table, in case last value was not inserted b/c it was a duplicate, to get rankings
    cur.execute(f"SELECT COUNT(*) FROM top_latest_stories")
    before_row_count = cur.fetchone()[0]

    #if table has less than 100 items
    if before_row_count < 100:

        #assign table variables
        ranking = before_row_count + 1
        title = stories[index]['title']
        country = stories[index]['country'][0].title()
        link = stories[index]['link']

        #insert into table
        insertNewsData(cur, conn, ranking, title, country, link)

        #check row count again
        cur.execute(f"SELECT COUNT(*) FROM top_latest_stories")
        after_row_count = cur.fetchone()[0]
            
        if after_row_count == before_row_count + 1:
            print(f"Data for {country} inserted into the database.")
        
    else:
        print("Database contains 100 items.")

conn.close()
