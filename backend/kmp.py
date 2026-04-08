"""
Knuth-Morris-Pratt (KMP) Algorithm
Builds an LPS (Longest Prefix Suffix) table that acts as a DFA
transition table: on mismatch, jump to the last valid partial-match
state instead of restarting from 0.
"""

def build_lps(pattern):
    """
    Build the LPS (failure function) table for the pattern.
    lps[i] = length of the longest proper prefix of pattern[0..i]
              that is also a suffix.
    This is the DFA transition table for mismatches.
    """
    m = len(pattern)
    lps = [0] * m
    length = 0   # length of previous longest prefix-suffix
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]   # DFA fallback transition
            else:
                lps[i] = 0
                i += 1
    return lps

def kmp_search(text, pattern):
    """
    Return list of starting indices where pattern occurs in text.
    Uses the LPS table as a DFA to avoid redundant comparisons.
    """
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return []

    lps = build_lps(pattern)
    matches = []
    i = j = 0   # i = text index, j = pattern state (DFA state)

    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
        if j == m:
            matches.append(i - j)   # match found: accepting state reached
            j = lps[j - 1]          # transition back via LPS
        elif i < n and text[i] != pattern[j]:
            if j != 0:
                j = lps[j - 1]      # DFA fallback
            else:
                i += 1
    return matches

def find_common_phrases_kmp(text1, text2, min_words=4):
    """
    Extract phrases from text1 and search them in text2 using KMP.
    Returns matched phrases with positions.
    """
    words1 = text1.split()
    results = []

    for length in range(min_words, min(10, len(words1) + 1)):
        for i in range(len(words1) - length + 1):
            phrase = ' '.join(words1[i:i + length])
            positions = kmp_search(text2, phrase)
            if positions:
                results.append({
                    'phrase': phrase,
                    'positions_in_doc2': positions,
                    'word_start_in_doc1': i,
                    'word_length': length
                })

    # Keep longest unique matches
    results.sort(key=lambda x: -x['word_length'])
    unique = []
    for r in results:
        if not any(r['phrase'] in u['phrase'] or u['phrase'] in r['phrase'] for u in unique):
            unique.append(r)

    return unique[:20]
