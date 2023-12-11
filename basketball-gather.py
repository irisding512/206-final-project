import requests
import sqlite3

# Function to create a SQLite database and tables
def create_db():
    conn = sqlite3.connect('countryImpact.db')
    c = conn.cursor()


    # Create a table for basketball game data
    c.execute('''CREATE TABLE IF NOT EXISTS games (
                    game_id INTEGER PRIMARY KEY,
                    home_team TEXT,
                    away_team TEXT,
                    home_score INTEGER,
                    away_score INTEGER,
                    location TEXT
                )''')

    # Create another table for additional game-related data
    c.execute('''CREATE TABLE IF NOT EXISTS game_details (
                    game_id INTEGER,    
                    game_date TEXT,
                    venue TEXT,
                    FOREIGN KEY(game_id) REFERENCES games(game_id)
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

                rows_to_insert = 25
                rows_inserted = 0

                for game in games_list:
                    if rows_inserted >= rows_to_insert:
                        break  # Break the loop if the desired number of rows is reached

                    try:
                        game_id = game['id']
                        if game_id_exists(c, game_id):
                            print(f"Game ID {game_id} already exists. Skipping.")
                            continue  # Skip insertion if game ID already exists

                        home_team_name = game['teams']['home']['name']
                        away_team_name = game['teams']['away']['name']
                        home_scores = game['scores']['home']
                        away_scores = game['scores']['away']
                        game_date = game['date']
                        venue = game.get('venue', 'Unknown')
                        location = game['country']['name'] if 'country' in game else 'Unknown'

                        c.execute('''INSERT INTO games (
                                        game_id,
                                        home_team,
                                        away_team,
                                        home_score,
                                        away_score,
                                        location
                                    ) VALUES (?, ?, ?, ?, ?, ?)''',
                                    (game_id, home_team_name, away_team_name,
                                    home_scores['total'], away_scores['total'], location))

                        c.execute('''INSERT INTO game_details (
                                        game_id,
                                        game_date,
                                        venue
                                    ) VALUES (?, ?, ?)''',
                                    (game_id, game_date, venue))

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