import firebase_admin
from firebase_admin import credentials, firestore

# Caminho onde o Render salva o Secret File
cred = credentials.Certificate("/etc/secrets/.firebase_key.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
