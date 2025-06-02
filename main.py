from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin_init import db

app = FastAPI()

# Liberar acesso externo (Manus AI, FlutterFlow)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/alerts-checkin")
async def get_alerts_checkin():
    docs = db.collection("AlertsCheckIn").limit(100).stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results
