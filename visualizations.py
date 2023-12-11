import matplotlib.pyplot as plt
import sqlite3
import os

# Connect to the database
db_name = "countryImpact.db"
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/'+db_name)
cur = conn.cursor()

# Query data from the recoveryPercent table with a join to get country names
cur.execute('''
    SELECT rp.country_id, rp.recovery_percentage, ck.country_name
    FROM recoveryPercent rp
    JOIN countryKeys ck ON rp.country_id = ck.country_id
''')
data = cur.fetchall()

# Extract relevant columns
country_ids, recovery_percentages, country_names = zip(*data)

# Plotting the line graph
plt.plot(country_names, recovery_percentages, marker='o', linestyle='-')
plt.xlabel('Country Names')
plt.ylabel('Recovery Percentage')
plt.title('Recovery Percentage for Each Country')
plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability

# Show the plot
plt.tight_layout()
plt.show()


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