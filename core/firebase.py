import os
import json
import firebase_admin
from firebase_admin import credentials, auth

def init_firebase():
    if firebase_admin._apps:
        return

    raw = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if not raw:
        raise RuntimeError("FIREBASE_SERVICE_ACCOUNT env var missing")

    service_account = json.loads(raw)

    cred = credentials.Certificate(service_account)
    firebase_admin.initialize_app(cred)

init_firebase()

def verify_firebase_token(id_token: str):
    return auth.verify_id_token(id_token)
