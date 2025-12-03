# FocusDeck
A web app that helps students study through flashcards.
FocusDeck allows users to:
- Generate flashcards from notes/topics using AI (Gemini API)  
- Save, load, and delete flashcards per user  
- Authenticate via Firebase login/signup 

# commands

from the terminal cd into backend and activate virtual environment "$source venv/bin/activate"
install dependencies "pip install -r requirements.txt"

run backend server "python app.py"
run frontend server "flutter run -d chrome"

# Prerequisites
- Python 3.10+  
- Flutter SDK  
- fire_base_service.json file - this is the service key, you can use the one I provided or create your own, place it in the backend folder.
- Google Gemini API key  - this is the service key, you can use the one I provided or create your own 
- .env file - this is where you will put the necessary keys for the code to run. 
    the file should look like this:
    GEMINI_API_KEY= whatever the AI pi key is
    FIREBASE_CREDENTIALS = the name of the service key file (fire_base_service.json)
    FIREBASE_WEB_API_KEY = whatever the web api key is. I'll provide it or you can just go to the firebase project -> project settings -> in general tab scroll all the way down to "your apps" -> click on focusdeck-web -> press config -> copy api key



# Security Note

**Never commit these files to GitHub:**
- `backend/firebase_service_account.json`  
- `.env`  

These contain private keys and secrets. `.gitignore` ensures they are ignored. so if your getting erros when pushing to github thats why. you have to remove them from the project then put them back when you want to work on or test the project.


# structure
FocusDeck/
├── backend/                  # Flask + Firebase backend
│   ├── app.py
│   ├── firebase_client.py
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── utils/
│   ├── venv/
│   └── firebase_service_account.json (local, ignored)
├── frontend/                 # Flutter app
│   └── main.dart
├── .gitignore
├── README.md
└── .env                      # local environment variables (ignored)