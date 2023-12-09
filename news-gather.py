import unittest
import sqlite3
import json
import os
import matplotlib.pyplot as plt
import requests

def insertNewsData(db_name):
    # connectToDatabase
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()

    # createTopStoriesTable
    cur.execute("CREATE TABLE IF NOT EXISTS top_stories(ranking INTEGER PRIMARY KEY, title TEXT, locale TEXT)")
    conn.commit()

    # newsdata.io
    # search by keyword "Covid"
    # 10 articles at a time

    # addTopStories
    base_url = 'https://newsdata.io/api/1/news?apikey=pub_34479d289637b0172bf42c8842ddfc21776a8&q=covid'
    params = {"keyword": "covid"}

    response = requests.get(base_url, params)

    if response.status_code == 200:
        data = response.json()
    
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

    data = response.text
    stories = json.loads(data)

    for story in stories:
        ranking = story['results']['ranking']
        title = story['results']['title']
        locale = story['results']['locale']

        cur.execute(
            "INSERT OR IGNORE INTO top_stories (ranking, title, locale) VALUES (?,?,?)", (ranking, title, locale)
        )
    conn.commit()
