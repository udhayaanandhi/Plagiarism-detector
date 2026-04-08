"""
app.py — Flask REST API for Plagiarism Detector
Endpoints:
  POST /api/check          — JSON body {text1, text2}
  POST /api/check-files    — multipart/form-data {file1, file2}
  GET  /api/health         — health check
"""

import os, json
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from text_processing  import preprocess
from plagiarism_checker import check_plagiarism

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024   # 2 MB


# ── helpers ────────────────────────────────────────────────────────────

def _run(raw1, raw2):
    t1 = preprocess(raw1)
    t2 = preprocess(raw2)
    return check_plagiarism(t1, t2)


# ── routes ─────────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/api/check', methods=['POST'])
def check_text():
    """Accept plain text via JSON."""
    data = request.get_json(force=True)
    text1 = data.get('text1', '').strip()
    text2 = data.get('text2', '').strip()
    if not text1 or not text2:
        return jsonify({'error': 'Both text1 and text2 are required.'}), 400
    try:
        result = _run(text1, text2)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/check-files', methods=['POST'])
def check_files():
    """Accept two uploaded .txt files."""
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({'error': 'Both file1 and file2 are required.'}), 400
    f1 = request.files['file1']
    f2 = request.files['file2']
    try:
        text1 = f1.read().decode('utf-8', errors='ignore')
        text2 = f2.read().decode('utf-8', errors='ignore')
        result = _run(text1, text2)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
