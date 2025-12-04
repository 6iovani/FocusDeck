import firebase_admin
from firebase_admin import credentials, firestore, auth
import os

class FirebaseClient:
    """
    initializes and provides access to firebase services for this app.
    loads credentials from local service account json file for API authentication.
    """
    def __init__(self):
        # get file name & path of the firebase service account credentials
        cred_file = os.environ.get("FIREBASE_CREDENTIALS", "firebase_service_account.json")
        cred_path = os.path.join(os.path.dirname(__file__), cred_file)
        # start firebase admin SDK if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        # show the database and auth
        self.db = firestore.client()
        self.auth = auth

    # get firestore database
    def get_firestore(self):
        return self.db
    # get firebase auth
    def get_auth(self):
        return self.auth