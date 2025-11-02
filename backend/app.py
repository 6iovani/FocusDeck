from flask import Flask, request, jsonify
from flask_cors import CORS 
import os
import openai

#set API key from environment 


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
    
    #prompt to create flashcards
    system_prompt = (
        "generate 10 flashcards Q&A pairs for study from these notes: "
        f"""{prompt}""" + "\n"
        "return a JSON list of objects, each with 'question' and 'answer' keys."
    )

    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "you are a helpful flashcard generator."},
                      {"role": "user", "content": system_prompt}],
            temperature=0.35,
            max_tokens=650,
            response_format={"type": "json_object"}
        )
        #parse the content as JSON
        import json
        raw_content = completion.choices[0].message.content
        parsed = json.loads(raw_content)
        flashcards = parsed["flashcards"] if "flashcards" in parsed else parsed  
        result_cards = []
        for fc in flashcards:
            if isinstance(fc, dict) and 'question' in fc and 'answer' in fc:
                result_cards.append({
                    'question': str(fc['question']),
                    'answer': str(fc['answer'])
                })
        return jsonify({'flashcards': result_cards})
    except Exception as e:
        return jsonify({'error': str(e)}), 500 #something's wrong with ai

@app.route('/api/generate_flashcards', methods=['POST'])
def generate_flashcards():
    data = request.get_json()
    notes = data.get('notes', '').strip()
    if not notes:
        return jsonify({'error': 'notes are required goofy'}), 400 #if nothing is typed
    
    system_prompt = (
        "generate 10 flashcards Q&A pairs for study from these notes: "
        f"""{notes}""" + "\n"
        "return a JSON list of objects, each with 'question' and 'answer' keys."
    )
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "you are a helpful flashcard generator."},
                      {"role": "user", "content": system_prompt}],
            temperature=0.35,
            max_tokens=650,
            response_format={"type": "json_object"}
        )
        import json
        raw_content = completion.choices[0].message.content
        parsed = json.loads(raw_content)
        flashcards = parsed["flashcards"] if "flashcards" in parsed else parsed
        result_cards = []
        for fc in flashcards:
            if isinstance(fc, dict) and 'question' in fc and 'answer' in fc:
                result_cards.append({
                    'front': str(fc['question']),
                    'back': str(fc['answer'])
                })
        return jsonify({'flashcards': result_cards})
    except Exception as e:
        return jsonify({'error': str(e)}), 500 #somthing's prob wrong with ai

if __name__ == '__main__':
    app.run(debug=False, port=5000)