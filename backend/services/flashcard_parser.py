import json

class FlashcardParser:
    def parse(self, text):
        start = text.find("[")
        end = text.rfind("]")

        if start == -1 or end == -1:
            raise ValueError("No JSON array found")

        json_data = text[start:end+1]

        return json.loads(json_data)