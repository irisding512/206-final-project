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

    # create top stories table
    cur.execute("CREATE TABLE IF NOT EXISTS latest_stories(ranking INTEGER, title TEXT PRIMARY KEY, country TEXT, countryID INTEGER, link TEXT)")
    conn.commit()
    return cur, conn

def insertNewsData(cur, conn, ranking, title, country, countryID, link):
    # newsdata.io API
    # search by keyword "health"
    # 10 articles at a time

    # add top stories into database
    cur.execute("INSERT OR IGNORE INTO latest_stories (ranking, title, country, countryID, link) VALUES (?,?,?,?,?)", (ranking, title, country, countryID, link))
    conn.commit()

cur, conn = setUpTable(db_name)

response = requests.get(base_url, params=None)

if response.status_code == 200:
    data = response.json()
    stories = data.get('results', [])

    #checks how many rows have been added to table so far
    cur.execute(f"SELECT COUNT(*) FROM top_stories")
    initial_row_count = cur.fetchone()[0]

    #returns 10 stories (sometimes can be duplicates)
    for index in range(10):
        #check how many rows are in table, in case last value was not inserted b/c it was a duplicate, to get rankings
        cur.execute(f"SELECT COUNT(*) FROM top_stories")
        before_row_count = cur.fetchone()[0]

        #if table has less than 100 items
        if before_row_count < 100:

            #assign table variables
            ranking = before_row_count + 1
            title = stories[index]['title']
            country = stories[index]['country'][0].title()

            #exceptions for country ID assignment
            if country.lower() == "united states of america":
                country = "USA"
            elif country.lower() == "united kingdom":
                country = "UK"
                
            #country ID assignment
            countryID = 0
            link = stories[index]['link']

            #insert into table
            insertNewsData(cur, conn, ranking, title, country, link)

            #check row count again
            cur.execute(f"SELECT COUNT(*) FROM top_stories")
            after_row_count = cur.fetchone()[0]
            
            if after_row_count == before_row_count + 1:
                print(f"Data for {country} inserted into the database.")
        
        else:
            print("Database contains 100 items.")
else:
    print(f"Failed to retrieve data. Status code:", response.status_code)
    print("Response content:", response.text)

conn.close()

