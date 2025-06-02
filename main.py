from fastapi import FastAPI, Query
from firebase_admin_init import db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Libera acesso externo (ex: Manus AI, FlutterFlow, Retool)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API funcionando. Use /alerts-checkin, /checklist, /driver-trips, /incidents com ?enterpriseId=..."}

# Alerts Check-In
@app.get("/alerts-checkin")
def get_alerts_checkin(enterpriseId: str = Query(None)):
    query = db.collection("AlertsCheckIn")
    if enterpriseId:
        query = query.where("enterpriseId", "==", enterpriseId)
    docs = query.limit(100).stream()
    return [doc.to_dict() for doc in docs]

# Checklist
@app.get("/checklist")
def get_checklist(enterpriseId: str = Query(None)):
    query = db.collection("Checklist")
    if enterpriseId:
        query = query.where("enterpriseId", "==", enterpriseId)
    docs = query.limit(100).stream()
    return [doc.to_dict() for doc in docs]

# Driver Trips
@app.get("/driver-trips")
def get_driver_trips(enterpriseId: str = Query(None)):
    query = db.collection("DriverTrips")
    if enterpriseId:
        query = query.where("enterpriseId", "==", enterpriseId)
    docs = query.limit(100).stream()
    return [doc.to_dict() for doc in docs]

# Incidents
@app.get("/incidents")
def get_incidents(enterpriseId: str = Query(None)):
    query = db.collection("Incidents")
    if enterpriseId:
        query = query.where("enterpriseId", "==", enterpriseId)
    docs = query.limit(100).stream()
    return [doc.to_dict() for doc in docs]
