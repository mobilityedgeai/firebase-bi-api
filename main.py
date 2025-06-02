from fastapi import FastAPI
from firebase_admin_init import db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (necessário para acesso do Manus AI ou web clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API funcionando. Use /all-data para ver tudo."}

@app.get("/all-data")
def get_all_collections():
    from google.cloud.firestore_v1.base_client import BaseClient
    client: BaseClient = db
    collections = client.collections()
    
    output = {}
    for collection in collections:
        name = collection.id
        docs = collection.limit(100).stream()
        output[name] = [doc.to_dict() for doc in docs]
    
    return output
