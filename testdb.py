import sqlite3

# Establish connection with the database. Creates a new file if it doesn't exist
connection = sqlite3.connect('asia-cards.db')

# Create a cursor object to execute SQL queries
cursor = connection.cursor()

# Execute a query
cursor.execute("SELECT * FROM cards WHERE name='Charlotte Katakuri'")

# Fetch all the results
results = cursor.fetchall()

# Print the results
for row in results:
    print(row)

# Commit changes (if any)
connection.commit()

# Close the connection
connection.close()