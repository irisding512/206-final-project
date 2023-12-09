import unittest
import sqlite3
import json
import os
import matplotlib.pyplot as plt
import requests

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def createTopStoriesTable(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS top_stories (ranking INTEGER PRIMARY KEY, title TEXT, locale TEXT")
    conn.commit()

# thenewsapi
# https://api.thenewsapi.com/v1/news/top?api_token=vbPjlVlYfITCitC4cKYFlt3oeN9Y5uUXbyTNrx10&limit=2&page=1
# https://api.thenewsapi.com/v1/news/top?api_token=vbPjlVlYfITCitC4cKYFlt3oeN9Y5uUXbyTNrx10&limit=2&page=2
# grab data from first 50 pages

# newsapi
# d6658b18e4944b728bbf727db2f4dd62

# newsdata.io
# search by keyword "Covid"
# 10 articles at a time

def addTopStories(base_url, params=None, cur, conn):
    response = requests.get(base_url, params)
    data = response.text
    stories = json.loads(data)

    for story in stories:
        ranking = story['']
        title = story['']
        locale = story['']

        cur.execute(
            "INSERT OR IGNORE INTO top_stories (ranking, title, locale) VALUES (?,?,?)", (ranking, title, locale)
        )
    conn.commit()
    

def main():
    cur, conn = setUpDatabase('news.db')
    createTopStoriesTable(cur, conn)
    params = {"keyword": "covid"}
    addTopStories('https://newsdata.io/api/1/news?apikey=pub_34479d289637b0172bf42c8842ddfc21776a8&q=covid ', params, cur, conn)
