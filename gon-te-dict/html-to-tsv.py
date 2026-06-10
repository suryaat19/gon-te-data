import os
import csv
import re
from bs4 import BeautifulSoup

HTML_STORAGE_DIR = "saved_html_chunks"
OUTPUT_TSV = "gon_te_01.tsv"

TELUGU_RE = re.compile(r'[\u0C00-\u0C7F]')
LATIN_RE = re.compile(r'[a-zA-Z]')
WORD_RE = re.compile(r'[\u0C00-\u0C7Fa-zA-Z0-9]+')
BRACKET_RE = re.compile(r'\[.*?\]')
GRAMMAR_RE = re.compile(r'\b(n|adj|adv|v|vi|vt|advl|num|pro|conj|interj)\b\.')
PREFIX_RE = re.compile(r'^[\-\.\d\(\)]+\s*')
FILE_SORT_RE = re.compile(r'pages_(\d+)_')
SPLIT_RE = re.compile(r'\.\s+')
SPACE_RE = re.compile(r'\s+')

def has_telugu(text):
    return bool(TELUGU_RE.search(text))

def has_latin(text):
    return bool(LATIN_RE.search(text))

def word_count(text):
    return len(WORD_RE.findall(text))

def is_clean_sentence(text):
    if BRACKET_RE.search(text):
        return False
    if GRAMMAR_RE.search(text):
        return False
    return True

def parse_html_to_tsv():
    parallel_sentences = []
    html_files = [f for f in os.listdir(HTML_STORAGE_DIR) if f.endswith(".html")]

    def sort_key(filename):
        match = FILE_SORT_RE.search(filename)
        return int(match.group(1)) if match else 0

    html_files.sort(key=sort_key)

    for filename in html_files:
        filepath = os.path.join(HTML_STORAGE_DIR, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        text = soup.get_text(separator=" ")
        text = SPACE_RE.sub(' ', text).strip()
        sentences = [s.strip() for s in SPLIT_RE.split(text) if s.strip()]

        i = 0
        while i < len(sentences) - 2:
            s1 = sentences[i]
            s2 = sentences[i+1]
            s3 = sentences[i+2]

            if has_telugu(s1) and has_latin(s2) and not has_telugu(s2) and has_telugu(s3):
                if word_count(s1) > 2 and word_count(s2) > 2 and word_count(s3) > 2:
                    if is_clean_sentence(s1) and is_clean_sentence(s3):
                        gondi = PREFIX_RE.sub('', s1).strip()
                        telugu = PREFIX_RE.sub('', s3).strip()

                        parallel_sentences.append([gondi, telugu])
                        i += 3
                        continue
            i += 1

    with open(OUTPUT_TSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(["Gondi_Sentence", "Telugu_Sentence"])
        writer.writerows(parallel_sentences)

if __name__ == "__main__":
    parse_html_to_tsv()
