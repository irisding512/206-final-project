import requests
import sqlite3

# Function to create a SQLite database and tables
def create_db():
    conn = sqlite3.connect('countryImpact.db')
    c = conn.cursor()

    # Create a table for basketball game data
    c.execute('''CREATE TABLE IF NOT EXISTS games (
                    game_id INTEGER PRIMARY KEY,
                    home_team_id INTEGER,
                    away_team_id INTEGER,
                    home_team_name TEXT,
                    away_team_name TEXT,
                    home_score INTEGER,
                    away_score INTEGER,
                    game_date TEXT,
                    location TEXT
                )''')

    # Create a table for team IDs and names
    c.execute('''CREATE TABLE IF NOT EXISTS teams_key (
                    team_id INTEGER PRIMARY KEY,
                    team_name TEXT
                )''')

    conn.commit()
    conn.close()

# Function to check if a row with the same game_id exists in the games table
def game_id_exists(cursor, game_id):
    cursor.execute("SELECT COUNT(*) FROM games WHERE game_id = ?", (game_id,))
    return cursor.fetchone()[0] > 0

# Fetching and storing data in the database
def fetch_and_store_data():
    url = "https://api-basketball.p.rapidapi.com/games"
    querystring = {"date": "2019-11-26"}
    headers = {
        "X-RapidAPI-Key": "ab11cf4f3emshbf271858852cbb7p1840f3jsn068c226e4bb7",
        "X-RapidAPI-Host": "api-basketball.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        try:
            data = response.json()
            if 'response' in data and isinstance(data['response'], list) and len(data['response']) > 0:
                games_list = data['response']

                conn = sqlite3.connect('countryImpact.db')
                c = conn.cursor()

                rows_to_insert = 12
                rows_inserted = 0

                for game in games_list:
                    if rows_inserted >= rows_to_insert:
                        break  # Break the loop if the desired number of rows is reached

                    try:
                        game_id = game['id']
                        if game_id_exists(c, game_id):
                            print(f"Game ID {game_id} already exists. Skipping.")
                            continue  # Skip insertion if game ID already exists

                        home_team_id = game['teams']['home']['id']
                        away_team_id = game['teams']['away']['id']
                        home_team_name = game['teams']['home']['name']
                        away_team_name = game['teams']['away']['name']
                        home_scores = game['scores']['home']
                        away_scores = game['scores']['away']
                        game_date = game['date']
                        location = game['country']['name'] if 'country' in game else 'Unknown'

                        c.execute('''INSERT INTO games (
                                        game_id,
                                        home_team_id,
                                        away_team_id,
                                        home_team_name,
                                        away_team_name,
                                        home_score,
                                        away_score,
                                        game_date,
                                        location
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                    (game_id, home_team_id, away_team_id, home_team_name, away_team_name,
                                    home_scores['total'], away_scores['total'], game_date, location))

                        # Inserting team IDs and names into the teams_key table
                        c.execute('''INSERT OR IGNORE INTO teams_key (team_id, team_name) VALUES (?, ?)''',
                                    (home_team_id, home_team_name))
                        c.execute('''INSERT OR IGNORE INTO teams_key (team_id, team_name) VALUES (?, ?)''',
                                    (away_team_id, away_team_name))

                        rows_inserted += 1

                    except KeyError as e:
                        print(f"Error extracting game data: {e}. Skipping this game.")
                        continue

                conn.commit()
                conn.close()

                print(f"{rows_inserted} rows successfully stored in the database.")
            else:
                print("No valid games found in the response.")
        except ValueError as e:
            print(f"ValueError while processing response: {e}. Response content: {response.content}")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

# Create database and tables (if they don't exist)
create_db()

# Fetch and store data
fetch_and_store_data()