from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["bibliotheque"]

def get_db():
    return db
def close_db():
    """Ferme la connexion MongoDB proprement."""
    client.close()
    print("🔒 Connexion MongoDB fermée.")