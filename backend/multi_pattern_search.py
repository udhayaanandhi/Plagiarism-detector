"""
Aho-Corasick Multi-Pattern Matcher
Builds a Trie (NFA) from all patterns, then adds failure links
to convert it into a DFA-like automaton. Searches all patterns
simultaneously in O(n + m + z) time.
"""

from collections import deque

class AhoCorasick:
    def __init__(self):
        # Each node: {'children': {char: node_id}, 'fail': 0, 'output': []}
        self.goto   = [{}]      # goto[state][char] -> next_state
        self.fail   = [0]       # failure links (DFA fallback)
        self.output = [[]]      # patterns that end at this state

    # ------------------------------------------------------------------ #
    #  Phase 1: Build Trie (NFA)
    # ------------------------------------------------------------------ #
    def _new_state(self):
        self.goto.append({})
        self.fail.append(0)
        self.output.append([])
        return len(self.goto) - 1

    def add_pattern(self, pattern):
        """Insert a pattern into the trie."""
        state = 0
        for ch in pattern:
            if ch not in self.goto[state]:
                self.goto[state][ch] = self._new_state()
            state = self.goto[state][ch]
        self.output[state].append(pattern)

    # ------------------------------------------------------------------ #
    #  Phase 2: Build failure links (NFA → DFA)
    # ------------------------------------------------------------------ #
    def build(self):
        """
        BFS over trie depth levels.
        Failure link of a state s reached by edge (parent, ch):
          - If parent's failure has a ch-transition → use it.
          - Else recursively follow failure links up.
        Also propagate output sets through failure links.
        """
        queue = deque()
        # Depth-1 states: failure goes to root (state 0)
        for ch, s in self.goto[0].items():
            self.fail[s] = 0
            queue.append(s)

        while queue:
            r = queue.popleft()
            for ch, s in self.goto[r].items():
                queue.append(s)
                state = self.fail[r]
                # Follow failure links until we find a state with a ch-transition
                while state != 0 and ch not in self.goto[state]:
                    state = self.fail[state]
                self.fail[s] = self.goto[state].get(ch, 0)
                if self.fail[s] == s:
                    self.fail[s] = 0
                # Merge outputs: patterns reachable via failure from s
                self.output[s] += self.output[self.fail[s]]

    # ------------------------------------------------------------------ #
    #  Phase 3: Search
    # ------------------------------------------------------------------ #
    def search(self, text):
        """
        Slide text through the DFA.
        Returns list of (end_index, pattern) for every match.
        """
        state = 0
        results = []
        for i, ch in enumerate(text):
            while state != 0 and ch not in self.goto[state]:
                state = self.fail[state]   # DFA fallback transition
            state = self.goto[state].get(ch, 0)
            for pat in self.output[state]:
                results.append((i - len(pat) + 1, pat))
        return results


def build_and_search(patterns, text):
    """Convenience wrapper: build automaton from patterns, search text."""
    ac = AhoCorasick()
    for p in patterns:
        ac.add_pattern(p)
    ac.build()
    return ac.search(text)


def multi_pattern_plagiarism(text1_tokens, text2, phrase_len=4):
    """
    Extract phrases of phrase_len words from text1 as patterns,
    then run Aho-Corasick over text2. Returns matched phrases.
    """
    words = text1_tokens
    patterns = list({
        ' '.join(words[i:i + phrase_len])
        for i in range(len(words) - phrase_len + 1)
    })

    matches = build_and_search(patterns, text2)
    unique_matches = list({m[1] for m in matches})

    return {
        'pattern_count': len(patterns),
        'match_count': len(matches),
        'unique_matches': sorted(unique_matches),
        'raw': matches
    }
