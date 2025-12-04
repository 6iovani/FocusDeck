from google import genai
import os
import json
from services.flashcard_parser import FlashcardParser

# logic for making flashcards/study guides
class FlashcardService:
    """
    Handles AI generation logic for both flashcards and study guides.
    Uses the Gemini API to extract or create content, using careful prompts.
    """
    def __init__(self):
        # Gemini API client and parser for post-processing model response
        api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.parser = FlashcardParser()

    # make flashcards
    def generate_flashcards(self, notes, amount=10, detail='brief'):
        
        style = 'short, succinct answers' if detail == 'brief' else 'detailed, in-depth answers'
        n = int(amount) if amount else 10
        instruction = (
            f"Return ONLY valid JSON. Format: [{{'question': '...', 'answer': '...'}}]"
            f"\nGenerate exactly {n} flashcards. Answers should be {style}.\nNotes:\n{notes}"
        )
        resp = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=instruction
        )
        text = resp.text
        return self.parser.parse(text)

    # make study guide
    def generate_study_guide(self, notes: str):
       
        prompt = f'''
Convert the following notes into a detailed, structured study guide.

Formatting rules (strict!):
- Only use numbers for topics and subtopics (e.g. 1., 2.1, 2.2, 3.)
- Use plain bullet points (• or -) for all info under each heading
- Do NOT use *, #, =, _, >, ~, or any extra symbols or markdown
- NO bolding, ALL CAPS, or font/size tricks
- Include more detail and core ideas—not one-liners!

Make the guide as comprehensive and organized as possible.

NOTES:
{notes}
'''
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text