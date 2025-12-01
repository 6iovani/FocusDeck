from firebase_admin import auth
import requests
import os

class AuthService:
    def __init__(self, firebase_client):
        self.firebase = firebase_client
        self.api_key = os.environ.get("FIREBASE_WEB_API_KEY")

    def create_user(self, email, password):
        return auth.create_user(email=email, password=password)

    def login(self, email, password):
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
        resp = requests.post(url, json={
            "email": email,
            "password": password,
            "returnSecureToken": True
        })
        data = resp.json()

        if "idToken" not in data:
            raise Exception(data.get("error", {}).get("message", "Login failed"))

        return data["idToken"]

    def verify_token(self, token):
        return auth.verify_id_token(token)