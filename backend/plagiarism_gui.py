"""
plagiarism_gui.py — Tkinter Desktop GUI
Run with: python plagiarism_gui.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading, json, os

from text_processing    import preprocess
from plagiarism_checker import check_plagiarism


# ── colour palette ─────────────────────────────────────────────────────
BG      = '#0d0f14'
SURFACE = '#13161e'
CARD    = '#181c28'
BORDER  = '#232840'
ACCENT  = '#4f8ef7'
GREEN   = '#00d4a0'
RED     = '#f76f4f'
YELLOW  = '#fbbf24'
TEXT    = '#e8ecf4'
MUTED   = '#7a8299'
FONT    = ('Consolas', 10)
FONT_B  = ('Consolas', 10, 'bold')
FONT_H  = ('Consolas', 13, 'bold')


class PlagiarismApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Plagiarism Detector — Pattern Matching & Automata')
        self.geometry('1100x760')
        self.configure(bg=BG)
        self.resizable(True, True)
        self._build_ui()

    # ── UI Construction ────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=SURFACE, pady=12)
        hdr.pack(fill='x')
        tk.Label(hdr, text='PLAGIARISM DETECTOR', font=('Consolas', 16, 'bold'),
                 fg=ACCENT, bg=SURFACE).pack(side='left', padx=20)
        tk.Label(hdr, text='Pattern Matching · KMP · Rabin-Karp · Aho-Corasick · N-gram',
                 font=('Consolas', 9), fg=MUTED, bg=SURFACE).pack(side='left', padx=10)

        # Main body
        body = tk.Frame(self, bg=BG)
        body.pack(fill='both', expand=True, padx=16, pady=12)

        # Left column: inputs
        left = tk.Frame(body, bg=BG)
        left.pack(side='left', fill='both', expand=True)

        self._doc1_text = self._doc_panel(left, 'Document 1', 1)
        self._doc2_text = self._doc_panel(left, 'Document 2', 2)

        # Buttons
        btn_row = tk.Frame(left, bg=BG, pady=8)
        btn_row.pack(fill='x')
        self._btn_run = tk.Button(btn_row, text='▶  RUN ANALYSIS', font=FONT_B,
                                  bg=ACCENT, fg='white', relief='flat', padx=18, pady=7,
                                  cursor='hand2', command=self._run)
        self._btn_run.pack(side='left', padx=(0, 8))
        tk.Button(btn_row, text='✕  Clear', font=FONT, bg=CARD, fg=MUTED,
                  relief='flat', padx=12, pady=7, cursor='hand2',
                  command=self._clear).pack(side='left')

        # Right column: results
        right = tk.Frame(body, bg=BG, width=420)
        right.pack(side='right', fill='both', padx=(14, 0))
        right.pack_propagate(False)

        tk.Label(right, text='RESULTS', font=FONT_B, fg=MUTED, bg=BG).pack(anchor='w', pady=(0, 6))
        self._result_frame = tk.Frame(right, bg=BG)
        self._result_frame.pack(fill='both', expand=True)
        self._score_card  = self._empty_score(self._result_frame)
        self._details_box = scrolledtext.ScrolledText(
            self._result_frame, font=('Consolas', 9), bg=CARD, fg=TEXT,
            relief='flat', bd=0, wrap='word', height=28,
            highlightbackground=BORDER, highlightthickness=1)
        self._details_box.pack(fill='both', expand=True, pady=(10, 0))

    def _doc_panel(self, parent, label, idx):
        frame = tk.Frame(parent, bg=CARD, pady=0)
        frame.pack(fill='both', expand=True, pady=(0, 10))
        frame.configure(highlightbackground=BORDER, highlightthickness=1)

        bar = tk.Frame(frame, bg=SURFACE)
        bar.pack(fill='x')
        tk.Label(bar, text=label, font=FONT_B, fg=TEXT, bg=SURFACE, pady=7, padx=10).pack(side='left')
        tk.Button(bar, text='Open File', font=FONT, bg=CARD, fg=ACCENT, relief='flat',
                  cursor='hand2', padx=8, pady=5,
                  command=lambda i=idx: self._load_file(i)).pack(side='right', padx=6, pady=4)

        txt = scrolledtext.ScrolledText(frame, font=('Consolas', 9), bg=CARD, fg=TEXT,
                                        relief='flat', bd=0, wrap='word', height=10,
                                        insertbackground=ACCENT,
                                        highlightthickness=0)
        txt.pack(fill='both', expand=True, padx=8, pady=(4, 8))
        return txt

    def _empty_score(self, parent):
        f = tk.Frame(parent, bg=SURFACE, padx=16, pady=14,
                     highlightbackground=BORDER, highlightthickness=1)
        f.pack(fill='x')
        tk.Label(f, text='Composite Score', font=FONT, fg=MUTED, bg=SURFACE).pack(anchor='w')
        lbl = tk.Label(f, text='—', font=('Consolas', 28, 'bold'), fg=MUTED, bg=SURFACE)
        lbl.pack(anchor='w')
        verdict = tk.Label(f, text='Run analysis to see results', font=FONT, fg=MUTED, bg=SURFACE)
        verdict.pack(anchor='w')
        f._score_lbl   = lbl
        f._verdict_lbl = verdict
        return f

    # ── Logic ──────────────────────────────────────────────────────────

    def _load_file(self, idx):
        path = filedialog.askopenfilename(filetypes=[('Text files', '*.txt'), ('All', '*.*')])
        if not path:
            return
        with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
            content = fh.read()
        target = self._doc1_text if idx == 1 else self._doc2_text
        target.delete('1.0', 'end')
        target.insert('end', content)

    def _run(self):
        t1 = self._doc1_text.get('1.0', 'end').strip()
        t2 = self._doc2_text.get('1.0', 'end').strip()
        if not t1 or not t2:
            messagebox.showwarning('Missing Input', 'Please enter or load both documents.')
            return
        self._btn_run.configure(state='disabled', text='Analysing…')
        threading.Thread(target=self._analyse, args=(t1, t2), daemon=True).start()

    def _analyse(self, raw1, raw2):
        try:
            c1 = preprocess(raw1)
            c2 = preprocess(raw2)
            result = check_plagiarism(c1, c2)
            self.after(0, lambda: self._show(result))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror('Error', str(e)))
        finally:
            self.after(0, lambda: self._btn_run.configure(state='normal', text='▶  RUN ANALYSIS'))

    def _show(self, r):
        score   = r['composite_score']
        verdict = r['verdict']
        color   = RED if score >= 50 else YELLOW if score >= 25 else GREEN

        self._score_card._score_lbl.configure(text=f"{score:.1f}%", fg=color)
        self._score_card._verdict_lbl.configure(text=verdict, fg=color)

        lines = []
        lines.append(f"{'='*46}")
        lines.append(f"  ALGORITHM SCORES")
        lines.append(f"{'='*46}")
        lines.append(f"  Rabin-Karp      : {r['rabin_karp']['score']:.2f}%")
        lines.append(f"  KMP             : {r['kmp']['score']:.2f}%")
        lines.append(f"  N-gram (3-gram) : {r['ngram'][3]['score']:.2f}%")
        lines.append(f"  Aho-Corasick    : {r['aho_corasick']['match_count']} phrase hits")
        lines.append('')
        lines.append(f"{'='*46}")
        lines.append(f"  N-GRAM BREAKDOWN")
        lines.append(f"{'='*46}")
        for n, v in r['ngram'].items():
            lines.append(f"  {n}-gram: {v['score']:.2f}%  ({v['common_count']} common / {v['total_ngrams_doc1']} in doc1)")

        lines.append('')
        lines.append(f"{'='*46}")
        lines.append(f"  KMP MATCHED PHRASES (top 5)")
        lines.append(f"{'='*46}")
        for m in r['kmp']['matches'][:5]:
            lines.append(f"  • {m['phrase']}")

        lines.append('')
        lines.append(f"{'='*46}")
        lines.append(f"  RABIN-KARP MATCHED PHRASES (top 5)")
        lines.append(f"{'='*46}")
        for m in r['rabin_karp']['matches'][:5]:
            lines.append(f"  • {m['phrase']}")

        lines.append('')
        lines.append(f"{'='*46}")
        lines.append(f"  AHO-CORASICK UNIQUE MATCHES (top 10)")
        lines.append(f"{'='*46}")
        for p in r['aho_corasick']['unique_matches'][:10]:
            lines.append(f"  • {p}")

        self._details_box.configure(state='normal')
        self._details_box.delete('1.0', 'end')
        self._details_box.insert('end', '\n'.join(lines))
        self._details_box.configure(state='disabled')

    def _clear(self):
        self._doc1_text.delete('1.0', 'end')
        self._doc2_text.delete('1.0', 'end')
        self._details_box.configure(state='normal')
        self._details_box.delete('1.0', 'end')
        self._details_box.configure(state='disabled')
        self._score_card._score_lbl.configure(text='—', fg=MUTED)
        self._score_card._verdict_lbl.configure(text='Run analysis to see results', fg=MUTED)


if __name__ == '__main__':
    app = PlagiarismApp()
    app.mainloop()
