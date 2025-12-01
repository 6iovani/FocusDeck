from google import genai
import os
import json
from services.flashcard_parser import FlashcardParser

class FlashcardService:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.parser = FlashcardParser()

    def generate_flashcards(self, notes):
        instruction = (
            "Return ONLY valid JSON. Format: "
            "[{'question': '...', 'answer': '...'}]\n\n"
            f"Notes:\n{notes}"
        )

        resp = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=instruction
        )

        text = resp.text
        return self.parser.parse(text)