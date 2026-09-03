# NumiLex — Number Expression Extraction & Classification

## Problem Statement
NumiLex is a college NLP project designed to extract numerical expressions from unstructured text and classify each detected expression into one of six semantic categories: Quantity, Percentage, Currency, Measurement, Ranking, and Date.

## Objective
The goal is to build an explainable rule-based NLP system that processes raw text, identifies relevant numeric patterns, and classifies them based on surrounding context and linguistic cues.

## Features
- Real text analysis via a Flask REST API
- Numerical expression detection from arbitrary input
- Category classification for six types of expressions
- Context extraction around each match
- Confidence scoring based on rule matching strength
- Highlighted original text and chart summaries
- Professional dashboard interface
- Empty input validation and backend error handling

## NLP Methodology
The pipeline follows a transparent NLP-style workflow:
1. Text input and normalization
2. Preprocessing and token-level cleanup
3. Numerical expression detection using regex and pattern rules
4. Context-aware linguistic analysis for disambiguation
5. Classification based on unit, symbol, and textual cues
6. Structured results and visualization

This project uses rule-based techniques and explainable heuristics instead of a black-box ML model.

## System Architecture
```text
Raw Text
  ↓
Text Preprocessing
  ↓
Numerical Pattern Detection
  ↓
Context & Linguistic Analysis
  ↓
Classification
  ↓
Structured JSON Output
  ↓
Frontend Visualization
```

## Technology Stack
- Python
- Flask
- HTML
- CSS
- JavaScript
- Rule-based NLP patterns

## Installation
1. Open a terminal in the project root.
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run
From the project root:
```bash
python app.py
```
Then open:
```text
http://localhost:5000
```

## API Documentation
### Endpoint
`POST /api/analyze`

### Request
```json
{
  "text": "The laptop costs ₹55,000 and has 16GB RAM."
}
```

### Response
```json
{
  "success": true,
  "text": "The laptop costs ₹55,000 and has 16GB RAM.",
  "statistics": {
    "total": 2,
    "quantity": 0,
    "percentage": 0,
    "currency": 1,
    "measurement": 1,
    "ranking": 0,
    "date": 0
  },
  "expressions": [
    {
      "expression": "₹55,000",
      "category": "Currency",
      "start": 17,
      "end": 24,
      "context": "The laptop costs ₹55,000 and has 16GB RAM.",
      "confidence": 0.99
    }
  ]
}
```

## Example Input
```text
The company generated ₹12.5 crore revenue in 2025, achieved 18.5% growth, hired 500 employees, and expanded to 12 countries. Its server operates at 3.2 GHz and the product received a 4.5/5 rating on 15 August 2025.
```

## Example Output Summary
- Currency: ₹12.5 crore
- Percentage: 18.5%
- Quantity: 500 employees, 12 countries
- Measurement: 3.2 GHz
- Ranking: 4.5/5
- Date: 2025, 15 August 2025

## Project Limitations
- This project uses explainable rule-based NLP rather than deep learning.
- Detection depends on carefully designed patterns and context heuristics.
- Ambiguous cases such as bare years may require contextual clues.

## Future Enhancements
- Add support for more entity types and domain-specific patterns
- Integrate spaCy-based tokenization and POS tagging
- Expand the rule engine for more multilingual inputs
- Add downloadable JSON exports and CSV reporting

## License
This project is intended for academic and demonstration purposes.
