import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate("service_account")
firebase_admin.initialize_app(cred)

def verify_firebase_token(id_token: str):
    return auth.verify_id_token(id_token)
