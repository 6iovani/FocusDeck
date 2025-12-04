import re
from firebase_admin import auth
import requests
import os

class AuthService:
    def __init__(self, firebase_client):
        self.firebase = firebase_client
        self.api_key = os.environ.get("FIREBASE_WEB_API_KEY")

    def create_user(self, email, password):
        if not self.is_valid_email(email):
            raise Exception("Invalid email address")
        user = auth.create_user(email=email, password=password)
        # Send email verification using Firebase REST API
        self.send_email_verification(user.uid, email)
        return user

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

        # Check for email verification
        if not data.get("emailVerified", False):
            raise Exception("Email not verified. Please check your inbox and follow the verification link.")
        return data["idToken"]

    def send_email_verification(self, uid, email):
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={self.api_key}"
        # Firebase expects idToken, but if not available, send with requestType and email (see REST doc)
        requests.post(url, json={"requestType": "VERIFY_EMAIL", "email": email})

    def verify_token(self, token):
        return auth.verify_id_token(token)

    def is_valid_email(self, email):
        return re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email)