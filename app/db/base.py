from pymongo import MongoClient

# Connect to the default local MongoDB server
client = MongoClient("mongodb://localhost:27017/")

# Access or create a database
db = client["smartshifts_db"]

# Access or create a collection (like a table)
shifts = db["shifts"]

# Insert a document
