from flask import Flask, jsonify, render_template, request
import csv
import os
from collections import defaultdict
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from numilex.nlp.extractor import analyze_text

app = Flask(__name__)

# Load dataset
def load_dataset(filepath):
    """Load test dataset from CSV"""
    data = []
    if not os.path.exists(filepath):
        return data
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'text': row['text'],
                'expected_category': row['expected_category'],
                'expected_expression': row['expected_expression']
            })
    return data

def calculate_accuracy(dataset, analyzer_func):
    """Calculate accuracy metrics on the dataset"""
    true_labels = []
    pred_labels = []
    results = []
    
    for item in dataset:
        text = item['text']
        expected_category = item['expected_category']
        expected_expr = item['expected_expression']
        
        # Analyze the text
        analysis = analyzer_func(text)
        
        # Find matching expression in results
        found = False
        predicted_category = None
        
        if analysis['success'] and analysis['expressions']:
            for expr in analysis['expressions']:
                # Check if the expected expression is in the detected expressions
                if expected_expr.lower() in expr['expression'].lower() or \
                   expr['expression'].lower() in expected_expr.lower():
                    predicted_category = expr['category']
                    found = True
                    break
        
        if not found:
            predicted_category = 'Quantity'  # Default fallback
        
        true_labels.append(expected_category)
        pred_labels.append(predicted_category)
        
        results.append({
            'text': text[:50] + '...' if len(text) > 50 else text,
            'expected': expected_category,
            'predicted': predicted_category,
            'match': expected_category == predicted_category,
            'expression': expected_expr
        })
    
    # Calculate metrics
    accuracy = accuracy_score(true_labels, pred_labels)
    
    # Per-category metrics
    categories = list(set(true_labels + pred_labels))
    category_metrics = {}
    
    for cat in categories:
        cat_true = [1 if x == cat else 0 for x in true_labels]
        cat_pred = [1 if x == cat else 0 for x in pred_labels]
        
        try:
            precision = precision_score(cat_true, cat_pred, zero_division=0)
            recall = recall_score(cat_true, cat_pred, zero_division=0)
            f1 = f1_score(cat_true, cat_pred, zero_division=0)
        except:
            precision = recall = f1 = 0
        
        category_metrics[cat] = {
            'precision': round(precision, 3),
            'recall': round(recall, 3),
            'f1': round(f1, 3)
        }
    
    return {
        'overall_accuracy': round(accuracy, 3),
        'total_samples': len(dataset),
        'correct': sum(1 for r in results if r['match']),
        'category_metrics': category_metrics,
        'results': results
    }

# Load dataset at startup
DATASET_PATH = os.path.join(os.path.dirname(__file__), 'data', 'test_dataset.csv')
dataset = load_dataset(DATASET_PATH)


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


@app.route("/api/evaluate", methods=["GET"])
def evaluate():
    """Run evaluation on the entire dataset"""
    if not dataset:
        return jsonify({
            "success": False,
            "error": "No dataset found. Please create numilex/data/test_dataset.csv"
        }), 400
    
    metrics = calculate_accuracy(dataset, analyze_text)
    return jsonify({"success": True, "metrics": metrics})


@app.route("/api/test-single", methods=["POST"])
def test_single():
    """Test a single sample from dataset"""
    data = request.get_json(silent=True) or {}
    idx = data.get("index", 0)
    
    if not dataset or idx >= len(dataset):
        return jsonify({"success": False, "error": "Invalid index"}), 400
    
    item = dataset[idx]
    analysis = analyze_text(item['text'])
    
    # Find if expected expression was detected
    found_category = None
    for expr in analysis.get('expressions', []):
        if item['expected_expression'].lower() in expr['expression'].lower() or \
           expr['expression'].lower() in item['expected_expression'].lower():
            found_category = expr['category']
            break
    
    return jsonify({
        "success": True,
        "sample": {
            "text": item['text'],
            "expected_category": item['expected_category'],
            "expected_expression": item['expected_expression'],
            "predicted_category": found_category or "Not Detected",
            "match": found_category == item['expected_category'],
            "analysis": analysis
        }
    })


@app.route("/api/dataset-info", methods=["GET"])
def dataset_info():
    """Get dataset statistics"""
    if not dataset:
        return jsonify({"success": False, "dataset_size": 0})
    
    category_count = defaultdict(int)
    for item in dataset:
        category_count[item['expected_category']] += 1
    
    return jsonify({
        "success": True,
        "dataset_size": len(dataset),
        "categories": dict(category_count)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
