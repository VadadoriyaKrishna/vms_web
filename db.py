import sqlite3

# Connect to an SQLite database (create it if it doesn't exist)
conn = sqlite3.connect('example.db')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Create a table
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL
                )''')

# Insert data into the table
cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ('John Doe', 'john@example.com'))

# Commit changes
conn.commit()

# Query the table
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close the connection
conn.close()
