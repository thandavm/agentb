import sqlite3
import requests
import boto3
import os

db_file = "pets.db"
if os.path.exists(db_file):
    os.remove(db_file)

conn = sqlite3.connect('pets.db')
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS pets (
           id INTEGER PRIMARY KEY, 
           name TEXT,
           status TEXT,
           category TEXT
           )""")

url = 'https://petstore.swagger.io/v2/pet/findByStatus?status=available,sold,pending'
response = requests.get(url)
pets = response.json()

for pet in pets:
    category_name = ""
    if "category" in pet:
        category_name = pet['category']['name']
    c.execute("INSERT INTO pets VALUES (?, ?, ?, ?)", 
             (pet['id'], pet['name'], pet['status'], category_name))

conn.commit()
conn.close()

## persist in to an s3 bucket
#s3 = boto3.client('s3')
#bucket = 'br-llm-agents'
#s3.upload_file('pets.db', bucket, 'pets.db')


# c.execute("SELECT * FROM pets")
#print(c.fetchall())

