"""
plagiarism_checker.py
Main orchestrator: runs all four detection methods and produces
a unified JSON-serialisable report.
"""

from text_processing      import preprocess, tokenize
from rabin_karp           import find_common_phrases_rk
from kmp                  import find_common_phrases_kmp
from ngram_similarity     import multi_ngram_similarity
from multi_pattern_search import multi_pattern_plagiarism


def _score_from_matches(matches, text2):
    """Rough similarity % based on matched character coverage in text2."""
    if not matches:
        return 0.0
    covered = set()
    for m in matches:
        phrase = m['phrase']
        for pos in m['positions_in_doc2']:
            covered.update(range(pos, pos + len(phrase)))
    return round(min(len(covered) / max(len(text2), 1) * 100, 100), 2)


def check_plagiarism(text1: str, text2: str) -> dict:
    """
    Run all detection algorithms on two preprocessed text strings.
    Returns a structured report dict.
    """
    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)

    # ── Rabin-Karp ────────────────────────────────────────────────────
    rk_matches  = find_common_phrases_rk(text1, text2, min_words=4)
    rk_score    = _score_from_matches(rk_matches, text2)

    # ── KMP ───────────────────────────────────────────────────────────
    kmp_matches = find_common_phrases_kmp(text1, text2, min_words=4)
    kmp_score   = _score_from_matches(kmp_matches, text2)

    # ── N-gram similarity ─────────────────────────────────────────────
    ngram_results = multi_ngram_similarity(tokens1, tokens2, ns=(1, 2, 3, 4, 5))
    ngram_score   = ngram_results[3]['score']   # use 3-gram as representative

    # ── Aho-Corasick ──────────────────────────────────────────────────
    ac_result   = multi_pattern_plagiarism(tokens1, text2, phrase_len=4)
    ac_score    = round(
        len(ac_result['unique_matches']) /
        max(ac_result['pattern_count'], 1) * 100, 2
    )

    # ── Composite score (weighted average) ────────────────────────────
    composite = round(
        0.25 * rk_score +
        0.25 * kmp_score +
        0.30 * ngram_score +
        0.20 * ac_score,
        2
    )

    verdict = (
        "High Plagiarism"   if composite >= 50 else
        "Moderate Overlap"  if composite >= 25 else
        "Low Similarity"
    )

    return {
        'composite_score': composite,
        'verdict': verdict,
        'rabin_karp': {
            'score': rk_score,
            'matches': rk_matches
        },
        'kmp': {
            'score': kmp_score,
            'matches': kmp_matches
        },
        'ngram': ngram_results,
        'aho_corasick': ac_result
    }
