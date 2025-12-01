import firebase_admin
from firebase_admin import credentials, firestore, auth
import os

class FirebaseClient:
    def __init__(self):
        cred_path = os.environ.get("FIREBASE_CREDENTIALS")
        cred = credentials.Certificate(cred_path)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)

        self.db = firestore.client()
        self.auth = auth

    def get_firestore(self):
        return self.db

    def get_auth(self):
        return self.auth