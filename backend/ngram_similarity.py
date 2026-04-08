"""
N-gram Similarity
Generates n-grams by sliding a fixed-size window (like a sliding-state
machine) across the token list. Measures Jaccard similarity between
the two n-gram sets.
"""

def generate_ngrams(tokens, n):
    """
    Produce all n-grams from a token list.
    Each window position i is a 'state' emitting tokens[i:i+n].
    """
    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]

def jaccard_similarity(set1, set2):
    """Jaccard index: |intersection| / |union|."""
    s1, s2 = set(set1), set(set2)
    if not s1 and not s2:
        return 0.0
    intersection = s1 & s2
    union = s1 | s2
    return len(intersection) / len(union)

def ngram_similarity(tokens1, tokens2, n=3):
    """
    Compute n-gram similarity between two token lists.
    Returns similarity score (0.0–1.0) and common n-grams.
    """
    grams1 = generate_ngrams(tokens1, n)
    grams2 = generate_ngrams(tokens2, n)

    score = jaccard_similarity(grams1, grams2)
    common = list(set(grams1) & set(grams2))
    common_phrases = [' '.join(g) for g in common]

    return {
        'n': n,
        'score': round(score * 100, 2),
        'total_ngrams_doc1': len(grams1),
        'total_ngrams_doc2': len(grams2),
        'common_count': len(common),
        'common_phrases': sorted(common_phrases)
    }

def multi_ngram_similarity(tokens1, tokens2, ns=(1, 2, 3, 4, 5)):
    """Run similarity for multiple n values and return results."""
    return {n: ngram_similarity(tokens1, tokens2, n) for n in ns}
