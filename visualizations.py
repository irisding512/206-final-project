import sqlite3
import os
import matplotlib.pyplot as plt

# Connect to the database
db_name = "countryImpact.db"
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/'+db_name)
cur = conn.cursor()

# Step 1: Retrieve the 17 country_ids from top_countries_in_stories
cur.execute("SELECT country_id FROM top_countries_in_stories")
top_country_ids = [row[0] for row in cur.fetchall()]

# Step 2: Replace country_id with country_name using countryKeys
country_names = []
for country_id in top_country_ids:
    cur.execute("SELECT country_name FROM countryKeys WHERE country_id = ?", (country_id,))
    result = cur.fetchone()
    if result:
        country_names.append(result[0])

# Step 3: Query the recoveryPercent table for recovery percentages of the selected countries
cur.execute('''
    SELECT country_id, recovery_percentage
    FROM recoveryPercent
    WHERE country_id IN ({})
'''.format(','.join('?' for _ in top_country_ids)), top_country_ids)

recovery_data = cur.fetchall()

# Extract relevant columns
recovery_country_ids, recovery_percentages = zip(*recovery_data)

# Filter out None values from recovery_percentages
filtered_recovery_percentages = [percent for percent in recovery_percentages if percent is not None]

# Check lengths of country_names and filtered_recovery_percentages
print("Number of countries:", len(country_names))
print("Number of recovery percentages:", len(filtered_recovery_percentages))

# Plotting the bar graph if lengths match
if len(country_names) == len(filtered_recovery_percentages):
    plt.bar(country_names, filtered_recovery_percentages, color='blue')
    plt.xlabel('Country Names')
    plt.ylabel('Recovery Percentage')
    plt.title('Recovery Percentage for Top Countries in Stories')
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability

    # Show the plot
    plt.tight_layout()
    plt.show()
else:
    print("Mismatch in the number of countries and recovery percentages.")


# Query data from the country counts table with a join to get country names
cur.execute('''
    SELECT tcis.country_id, tcis.count, ck.country_name
    FROM top_countries_in_stories tcis
    JOIN countryKeys ck ON tcis.country_id = ck.country_id
''')
counts = cur.fetchall()

country_ids, counts, country_names = zip(*counts)

# Plotting the bar graph
plt.bar(country_names, counts, color='blue')
plt.xlabel('Country Names')
plt.ylabel('% of Articles in Top 100')
plt.title('% of Articles in Top 100 Health News Articles from Each Country')

# Show the plot
plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
plt.tight_layout()
plt.show()

# Close the connection
conn.close()
