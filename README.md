# Plagiarism Detector — Pattern Matching & Automata

Implements **Rabin-Karp**, **KMP**, **N-gram similarity**, and **Aho-Corasick**
(NFA → DFA trie automaton) to detect plagiarism between two documents.

## Project Structure

```
plagiarism_detector/
├── document1.txt           # Sample input document 1
├── document2.txt           # Sample input document 2
├── text_processing.py      # Preprocessing (lowercase, strip, tokenize)
├── rabin_karp.py           # Rabin-Karp rolling-hash matcher
├── kmp.py                  # KMP DFA-based matcher + LPS builder
├── ngram_similarity.py     # N-gram Jaccard similarity (n=1..5)
├── multi_pattern_search.py # Aho-Corasick NFA→DFA trie automaton
├── plagiarism_checker.py   # Orchestrator — composite score & report
├── app.py                  # Flask REST API backend
├── plagiarism_gui.py       # Tkinter desktop GUI
├── index.html              # Standalone web frontend (no server needed)
└── requirements.txt
```

## Quick Start

### Option A — Web Frontend (no server needed)
Just open `index.html` in any browser.
All algorithms run in pure JavaScript — fully self-contained.

### Option B — Flask API + Web Frontend
```bash
pip install -r requirements.txt
python app.py
# API is available at http://localhost:5000
```

API endpoints:
- `POST /api/check`        — JSON `{text1, text2}`
- `POST /api/check-files`  — multipart `{file1, file2}` (.txt)
- `GET  /api/health`       — health check

### Option C — Desktop GUI (Tkinter)
```bash
python plagiarism_gui.py
```
No additional packages needed beyond Python's standard library.

## Algorithm Summary

| File | Automaton | Role |
|---|---|---|
| `text_processing.py` | N/A | Normalize & tokenize input |
| `rabin_karp.py` | Hash-based pseudo-FA | Rolling hash phrase matcher |
| `kmp.py` | DFA (LPS table) | Deterministic prefix-suffix matcher |
| `ngram_similarity.py` | Sliding-window FA | Jaccard similarity via n-grams |
| `multi_pattern_search.py` | NFA → DFA (Aho-Corasick) | Multi-pattern trie automaton |
| `plagiarism_checker.py` | Controller | Weighted composite score |
| `app.py` | — | Flask REST API |
| `plagiarism_gui.py` | — | Tkinter desktop UI |
| `index.html` | — | Standalone web UI |
