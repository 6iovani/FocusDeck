import os, json
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

from firebase_client import FirebaseClient
from services.auth_service import AuthService
from services.flashcard_service import FlashcardService
from repositories.flashcard_repository import FlashcardRepository
from utils.api_response import ApiResponse
from utils.error_handler import ErrorHandler

load_dotenv()

# Initialize services
firebase = FirebaseClient()
auth_service = AuthService(firebase_client=firebase)
flashcard_service = FlashcardService()
flashcard_repo = FlashcardRepository(firebase_client=firebase)

app = Flask(__name__)
CORS(app)

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})



# AUTH ROUTES
@app.route("/api/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        user = auth_service.create_user(email, password)
        return ApiResponse.success({"uid": user.uid, "email": user.email})
    except Exception as e:
        return ErrorHandler.handle(e)

@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        token = auth_service.login(email, password)
        return ApiResponse.success({"idToken": token})
    except Exception as e:
        return ErrorHandler.handle(e)

@app.route("/api/logout", methods=["POST"])
def logout():
    # For Firebase, logout is handled on frontend by removing token
    return ApiResponse.success({"message": "Logged out"})




# FLASHCARD GENERATION
@app.route("/api/generate_flashcards", methods=["POST"])
def generate_flashcards():
    try:
        data = request.get_json()
        notes = data.get("notes")

        cards = flashcard_service.generate_flashcards(notes)
        return ApiResponse.success({"flashcards": cards})
    except Exception as e:
        return ErrorHandler.handle(e)



# FLASHCARD STORAGE (Firestore)
@app.route("/api/flashcards/save", methods=["POST"])
def save_flashcards():
    try:
        token = request.headers.get("Authorization")
        user = auth_service.verify_token(token)

        data = request.get_json()
        cards = data.get("flashcards", [])

        flashcard_repo.save_flashcards(user["uid"], cards)
        return ApiResponse.success({"message": "Flashcards saved"})
    except Exception as e:
        return ErrorHandler.handle(e)


@app.route("/api/flashcards/load", methods=["GET"])
def load_flashcards():
    try:
        token = request.headers.get("Authorization")
        user = auth_service.verify_token(token)

        cards = flashcard_repo.get_flashcards(user["uid"])
        return ApiResponse.success({"flashcards": cards})
    except Exception as e:
        return ErrorHandler.handle(e)


@app.route("/api/flashcards/delete/<card_id>", methods=["DELETE"])
def delete_flashcard(card_id):
    try:
        token = request.headers.get("Authorization")
        user = auth_service.verify_token(token)

        flashcard_repo.delete_flashcard(user["uid"], card_id)
        return ApiResponse.success({"message": "Deleted"})
    except Exception as e:
        return ErrorHandler.handle(e)


if __name__ == "__main__":
    app.run(debug=False, port=5000)