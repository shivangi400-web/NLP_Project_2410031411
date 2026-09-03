from flask import Flask, jsonify, render_template, request

from numilex.nlp.extractor import analyze_text

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze_route():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    if not isinstance(text, str):
        return jsonify({
            "success": False,
            "error": "Request body must include a string 'text' field."
        }), 400

    if not text.strip():
        return jsonify({
            "success": False,
            "error": "Input text is empty."
        }), 400

    if len(text) > 25000:
        return jsonify({
            "success": False,
            "error": "Input text is too long. Please provide fewer than 25,000 characters."
        }), 413

    try:
        result = analyze_text(text)
        if not result["success"]:
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as exc:  # pragma: no cover - defensive backend error handling
        return jsonify({
            "success": False,
            "error": f"Backend error: {str(exc)}"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
