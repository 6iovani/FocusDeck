from flask import Flask, request, jsonify
from flask_cors import CORS 
import os
import openai

# Remove the incorrect export line, set API key from environment or hard-coded (not recommended for prod)
openai.api_key = os.environ.get('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')

app = Flask(__name__)
CORS(app)

@app.route('/api/health')
def health():
    return jsonify({"status": "ok!"})

@app.route('/api/flashcards', methods=['POST'])
def flashcards():
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    # Compose an OpenAI prompt to create 5 flashcard (Q&A) pairs from notes
    system_prompt = (
        "Generate 5 flashcards (Q&A pairs) for study from these notes: "
        f"""{prompt}""" + "\n"
        "Return a JSON list of objects, each with 'question' and 'answer' keys."
    )

    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful flashcard generator."},
                      {"role": "user", "content": system_prompt}],
            temperature=0.35,
            max_tokens=650,
            response_format={"type": "json_object"}
        )
        # Parse the assistant's content as JSON
        import json
        raw_content = completion.choices[0].message.content
        parsed = json.loads(raw_content)
        flashcards = parsed["flashcards"] if "flashcards" in parsed else parsed  # Flexible parsing
        result_cards = []
        for fc in flashcards:
            if isinstance(fc, dict) and 'question' in fc and 'answer' in fc:
                result_cards.append({
                    'question': str(fc['question']),
                    'answer': str(fc['answer'])
                })
        return jsonify({'flashcards': result_cards})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5001)