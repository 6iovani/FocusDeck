import os, json
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

load_dotenv()

try:
    from google import genai
    from google.genai import types
except Exception as e:
    raise RuntimeError("google-genai SDK not installed. pip install google-genai") from e

# create client to read api key from env
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else genai.Client()

app = Flask(__name__)
CORS(app)

@app.route("/api/health")
def health():
    return jsonify({"status": "ok!"})


def ask_gemini_for_json(prompt_text: str, model: str = "gemini-2.5-flash", max_output_tokens: int = 1200, temperature: float = 0.35):
    """
    Ask Gemini to return a JSON array of objects {question,answer}.
    Tries strict parse, then attempts simple repairs for truncated output.
    """
    instruction = (
        "You are a helpful flashcard generator. Produce exactly a JSON array of objects "
        "with 'question' and 'answer' keys only. Keep answers concise (one-sentence). "
        "Do not include any extra text, comments, or markdown.\n\n"
        f"Notes:\n{prompt_text}"
    )

    cfg = types.GenerateContentConfig(
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        candidate_count=1,
    )

    resp = client.models.generate_content(
        model=model,
        contents=instruction,
        config=cfg,
    )

    #extract text
    text = getattr(resp, "text", None) or getattr(resp, "generated_text", None) or str(resp)

    #maunal debuggin output (server console)
    print("\n=== GEMINI RAW OUTPUT START ===")
    print(text[:10000])
    print("=== GEMINI RAW OUTPUT END ===\n")

    #strict JSON
    try:
        parsed = json.loads(text)
    except Exception:
    
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end+1]
        else:
            #if no closing bracket, take from first '[' to end and attempt repair
            if start != -1:
                candidate = text[start:]
            else:
                raise ValueError(f"No JSON array found in model output. Raw start: {text[:500]!r}")

        #repair attempts
        repaired = candidate

        #balance braces/brackets counts by appending closing tokens if missing
        open_braces = repaired.count("{")
        close_braces = repaired.count("}")
        if close_braces < open_braces:
            repaired += "}" * (open_braces - close_braces)

        open_brackets = repaired.count("[")
        close_brackets = repaired.count("]")
        if close_brackets < open_brackets:
            repaired += "]" * (open_brackets - close_brackets)

        #remove trailing commas before closing bracket/brace 
        repaired = repaired.replace(",]", "]").replace(",}", "}")

        #try to remove any non-JSON prefix/suffix lines if still invalid
        try:
            parsed = json.loads(repaired)
        except Exception as e2:
            #final fallback detailed error with a short raw sample for debugging
            raise ValueError(f"Failed to parse or repair model JSON output. Raw (first 800 chars): {text[:800]!r}") from e2

    if not isinstance(parsed, list):
        raise ValueError("Parsed content is not a list as expected")

    return parsed



@app.route("/api/flashcards", methods=["POST"])
def flashcards():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    try:
        parsed_cards = ask_gemini_for_json(prompt, model="gemini-2.5-flash", max_output_tokens=1500)
        result_cards = []
        for fc in parsed_cards:
            if isinstance(fc, dict) and "question" in fc and "answer" in fc:
                result_cards.append({"question": str(fc["question"]), "answer": str(fc["answer"])})
        return jsonify({"flashcards": result_cards})
    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "debug": repr(e)[:1000],
                }
            ),
            500,
        )


@app.route("/api/generate_flashcards", methods=["POST"])
def generate_flashcards():
    data = request.get_json(silent=True) or {}
    notes = (data.get("notes") or "").strip()
    if not notes:
        return jsonify({"error": "notes are required"}), 400

    try:
        parsed_cards = ask_gemini_for_json(notes, model="gemini-2.5-flash", max_output_tokens=800, temperature=0.35)
        result_cards = []
        for fc in parsed_cards:
            if isinstance(fc, dict) and "question" in fc and "answer" in fc:
                result_cards.append({"front": str(fc["question"]), "back": str(fc["answer"])})
        return jsonify({"flashcards": result_cards})
    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "debug": repr(e)[:1000],
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(debug=False, port=5000)
