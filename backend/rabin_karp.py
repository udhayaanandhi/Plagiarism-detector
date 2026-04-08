"""
Rabin-Karp Algorithm
Uses rolling hash (polynomial hashing) to detect pattern occurrences.
Automata connection: Hash values act as pseudo-states; a match occurs
when both hash AND content agree — mimicking state acceptance in FA.
"""

BASE = 256       # Number of characters in input alphabet
MOD  = 101       # A prime number to reduce hash collisions

def _hash(s, length):
    """Compute initial polynomial hash for s[:length]."""
    h = 0
    for i in range(length):
        h = (h * BASE + ord(s[i])) % MOD
    return h

def rabin_karp_search(text, pattern):
    """
    Return list of starting indices where pattern is found in text.
    Uses rolling hash to slide efficiently over text.
    """
    n, m = len(text), len(pattern)
    if m > n:
        return []

    matches = []
    pattern_hash = _hash(pattern, m)
    text_hash    = _hash(text, m)

    # Highest place value for rolling: BASE^(m-1) % MOD
    h = pow(BASE, m - 1, MOD)

    for i in range(n - m + 1):
        if text_hash == pattern_hash:
            # Hash match — verify character by character (spurious hit guard)
            if text[i:i + m] == pattern:
                matches.append(i)

        if i < n - m:
            # Roll hash forward: remove leftmost char, add new rightmost char
            text_hash = (BASE * (text_hash - ord(text[i]) * h) + ord(text[i + m])) % MOD
            if text_hash < 0:
                text_hash += MOD

    return matches

def find_common_phrases_rk(text1, text2, min_words=4):
    """
    Extract phrases of at least min_words from text1 and search them in text2
    using Rabin-Karp. Returns list of matched phrases and their positions.
    """
    words1 = text1.split()
    results = []

    for length in range(min_words, min(10, len(words1) + 1)):
        for i in range(len(words1) - length + 1):
            phrase = ' '.join(words1[i:i + length])
            positions = rabin_karp_search(text2, phrase)
            if positions:
                results.append({
                    'phrase': phrase,
                    'positions_in_doc2': positions,
                    'word_start_in_doc1': i,
                    'word_length': length
                })

    # Deduplicate: keep only longest non-overlapping matches
    results.sort(key=lambda x: -x['word_length'])
    seen = set()
    unique = []
    for r in results:
        key = r['phrase']
        if not any(key in u['phrase'] or u['phrase'] in key for u in unique):
            unique.append(r)
            seen.add(key)

    return unique[:20]   # cap at 20 results
