import re
from firebase_admin import auth
import requests
import os

class AuthService:
    """
    Provides user authentication methods using Firebase Auth and Identity Toolkit API.
    Handles local user creation, login/verification, and secure authentication token work.
    """
    def __init__(self, firebase_client):
        # Save reference to the app-wide Firebase object and web api key
        self.firebase = firebase_client
        self.api_key = os.environ.get("FIREBASE_WEB_API_KEY")

    def create_user(self, email, password):
        """
        Creates a new Firebase user with email/password.
        Requires a valid email (simple regex check). Also sends out a verification email so users must confirm before login is allowed.
        """
        if not self.is_valid_email(email):
            raise Exception("Invalid email address")
        user = auth.create_user(email=email, password=password)
        self.send_email_verification(user.uid, email)
        return user

    def login(self, email, password):
        """
        Log user in using Firebase's public REST API (Identity Toolkit).
        Only succeeds if email + password are correct AND the email is verified (user clicked the link).
        Returns the user's ID token on success.
        """
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
        resp = requests.post(url, json={
            "email": email,
            "password": password,
            "returnSecureToken": True
        })
        data = resp.json()
        # Credentials wrong or account does not exist
        if "idToken" not in data:
            raise Exception(data.get("error", {}).get("message", "Login failed"))
        # Block login until email is verified
        if not data.get("emailVerified", False):
            raise Exception("Email not verified. Please check your inbox and follow the verification link.")
        return data["idToken"]

    def send_email_verification(self, uid, email):
        """
        Sends a verification email to the user via Firebase's REST API
        so the user must prove they control the email address.
        """
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={self.api_key}"
        requests.post(url, json={"requestType": "VERIFY_EMAIL", "email": email})

    def verify_token(self, token):
        """
        Checks that an ID token provided with requests is genuine and fresh (not expired or spoofed).
        Returns the user's details if valid, else throws.
        """
        return auth.verify_id_token(token)

    def is_valid_email(self, email):
        """
        Basic regex for recognizing valid emails. Used during signup.
        """
        return re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email)