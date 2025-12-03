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
CORS(app, resources={r"/api/*": {
    "origins": "*",
    "allow_headers": ["Content-Type", "Authorization"],
    "methods": ["GET", "POST", "DELETE", "OPTIONS"]
}})

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        headers = response.headers
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
        headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

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

# FLASHCARD STORAGE
@app.route("/api/flashcards/save", methods=["POST"])
def save_flashcards():
    try:
        token = request.headers.get("Authorization")
        user = auth_service.verify_token(token)
        data = request.get_json()
        cards = data.get("flashcards", [])
        set_title = data.get("set_title", "Untitled Set")
        flashcard_repo.save_flashcards(user["uid"], set_title, cards)
        return ApiResponse.success({"message": "Flashcards saved"})
    except Exception as e:
        return ErrorHandler.handle(e)

@app.route("/api/flashcards/load", methods=["GET"])
def load_flashcards():
    try:
        token = request.headers.get("Authorization")
        user = auth_service.verify_token(token)
        sets = flashcard_repo.get_flashcards(user["uid"])
        return ApiResponse.success({"sets": sets})
    except Exception as e:
        return ErrorHandler.handle(e)

@app.route("/api/flashcards/delete/<set_id>", methods=["DELETE"])
def delete_flashcard_set(set_id):
    try:
        token = request.headers.get("Authorization")
        user = auth_service.verify_token(token)
        flashcard_repo.delete_flashcard_set(user["uid"], set_id)
        return ApiResponse.success({"message": "Deleted"})
    except Exception as e:
        return ErrorHandler.handle(e)

# STUDY GUIDE
@app.route("/api/generate_study_guide", methods=["POST"])
def generate_study_guide():
    try:
        data = request.get_json()
        notes = data.get("notes")
        if not notes:
            return ApiResponse.error("Missing 'notes' field", status=400)
        guide = flashcard_service.generate_study_guide(notes)
        return ApiResponse.success({"guide": guide})
    except Exception as e:
        return ErrorHandler.handle(e)

@app.route("/api/study_guides/save", methods=["POST"])
def save_study_guide():
    try:
        token = request.headers.get("Authorization")
        user = auth_service.verify_token(token)
        data = request.get_json()
        title = data.get("title", "Untitled Guide")
        content = data.get("content", "")
        flashcard_repo.save_study_guide(user["uid"], title, content)
        return ApiResponse.success({"message": "Study guide saved"})
    except Exception as e:
        return ErrorHandler.handle(e)

@app.route("/api/study_guides/load", methods=["GET"])
def load_study_guides():
    try:
        token = request.headers.get("Authorization")
        user = auth_service.verify_token(token)
        guides = flashcard_repo.get_study_guides(user["uid"])
        return ApiResponse.success({"guides": guides})
    except Exception as e:
        return ErrorHandler.handle(e)

@app.route("/api/study_guides/delete/<guide_id>", methods=["DELETE"])
def delete_study_guide(guide_id):
    try:
        token = request.headers.get("Authorization")
        user = auth_service.verify_token(token)
        flashcard_repo.delete_study_guide(user["uid"], guide_id)
        return ApiResponse.success({"message": "Deleted"})
    except Exception as e:
        return ErrorHandler.handle(e)

if __name__ == "__main__":
    app.run(debug=False, port=5000)
