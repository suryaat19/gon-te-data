import os
import csv
import re
from bs4 import BeautifulSoup

HTML_STORAGE_DIR = "saved_html_parallel"
OUTPUT_TSV = "gon_te_pages_1_80.tsv"

CLEAN_PREFIX_RE = re.compile(r'^[➥➡→\-\>\s\•\*\d\.\:]+')
SPACE_RE = re.compile(r'\s+')
LATIN_RE = re.compile(r'[a-zA-Z]')

def extract_strict_dom():
    parallel_sentences = []

    if not os.path.exists(HTML_STORAGE_DIR):
        print(f"Directory {HTML_STORAGE_DIR} not found.")
        return

    html_files = [f for f in os.listdir(HTML_STORAGE_DIR) if f.endswith(".html")]
    html_files.sort(key=lambda f: int(re.search(r'\d+', f).group()) if re.search(r'\d+', f) else 0)

    for filename in html_files:
        filepath = os.path.join(HTML_STORAGE_DIR, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        for tbody in soup.find_all('tbody'):
            for tr in tbody.find_all('tr'):
                tds = tr.find_all('td')

                if not tds:
                    continue

                first_td_text = tds[0].get_text(strip=True)

                if re.match(r'^\d+\.?$', first_td_text):
                    if len(tds) >= 2:
                        target_td = tds[1]
                    else:
                        continue
                else:
                    target_td = tds[0]

                lines = [line.strip() for line in target_td.get_text(separator="\n").split("\n") if line.strip()]

                if len(lines) >= 2:
                    gondi_raw = lines[0]
                    telugu_raw = lines[1]

                    if LATIN_RE.search(gondi_raw) or LATIN_RE.search(telugu_raw):
                        continue

                    gondi_clean = CLEAN_PREFIX_RE.sub('', gondi_raw).strip()
                    telugu_clean = CLEAN_PREFIX_RE.sub('', telugu_raw).strip()

                    gondi_clean = SPACE_RE.sub(' ', gondi_clean)
                    telugu_clean = SPACE_RE.sub(' ', telugu_clean)

                    if gondi_clean and telugu_clean:
                        parallel_sentences.append([gondi_clean, telugu_clean])

    with open(OUTPUT_TSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(["Gondi_Sentence", "Telugu_Sentence"])
        writer.writerows(parallel_sentences)

    print(f"Extraction complete.")
    print(f"Successfully compiled {len(parallel_sentences)} sentences based on exact DOM rules.")

if __name__ == "__main__":
    extract_strict_dom()
