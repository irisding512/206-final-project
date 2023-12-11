#PART TWO: CALCULATE COUNTRY COUNTS
# base_url = "https://newsdata.io/api/1/news?apikey=pub_34479d289637b0172bf42c8842ddfc21776a8&qInTitle=health"

# #create country counts table
# cur.execute("CREATE TABLE IF NOT EXISTS top_countries_in_stories(country_id INTEGER PRIMARY KEY, count INTEGER)")

# # count how many times each country appears in the top_stories table
# cur.execute("SELECT country_id, COUNT(country_id) FROM latest_stories GROUP BY country_id ORDER BY COUNT(country_id) DESC")
# country_counts = cur.fetchall()

# # print the results
# for country_id, count in country_counts:
#     print(f"{country_id}: {count} times")
#     cur.execute("INSERT OR IGNORE INTO top_countries_in_stories (country_id, count) VALUES (?,?)", (country_id, count))

# conn.commit()

# cur.execute("SELECT country_id, COUNT(country_id) FROM latest_stories GROUP BY country_id ORDER BY COUNT(country_id) DESC")
# counts = cur.fetchall()

# # Write calculated data to a text file
# output_file_path = "calculations.txt"
# with open(output_file_path, "w") as output_file:
#     output_file.write(f"Percentage of Articles in the Top 100 Health News Articles from Each Country\n")
#     output_file.write(f"---------------------------------------------------------------------------\n\n")
#     for count in counts:
#         country_id, count = count
#         output_file.write(f"Country ID: {country_id}, Percentage: {count}%\n")