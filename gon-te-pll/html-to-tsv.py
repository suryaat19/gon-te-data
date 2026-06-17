import os
import csv
import re
from bs4 import BeautifulSoup

HTML_STORAGE_DIR = "saved_html_parallel" # Change this if your folder name is different
OUTPUT_TSV = "gon_te_pages_1_80.tsv"

def extract_strict_dom():
    parallel_sentences = []

    if not os.path.exists(HTML_STORAGE_DIR):
        print(f"Directory {HTML_STORAGE_DIR} not found.")
        return

    # Grab and sort HTML files naturally
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

                # Check the first column to identify the table type
                first_td_text = tds[0].get_text(strip=True)

                # Type 1: First column is strictly a number (e.g., "1.", "308.")
                if re.match(r'^\d+\.?$', first_td_text):
                    if len(tds) >= 2:
                        target_td = tds[1]
                    else:
                        continue
                # Type 2: First column contains the number AND the text
                else:
                    target_td = tds[0]

                # Convert the td back to a string so we can explicitly split by <br> tags
                inner_html = "".join([str(c) for c in target_td.contents])

                # Split strictly by <br> or <br/>
                parts = re.split(r'<br\s*/?>', inner_html, flags=re.IGNORECASE)

                if len(parts) >= 2:
                    # Parse out the raw text for the first two lines
                    gondi_raw = BeautifulSoup(parts[0], "html.parser").get_text(strip=True)
                    telugu_raw = BeautifulSoup(parts[1], "html.parser").get_text(strip=True)

                    # RULE: Retain ONLY Telugu Unicode (\u0C00-\u0C7F), spaces, commas, periods (and ?/! for safety)
                    # This automatically drops English numbers like "10" at the start, English scripts, and arrows like ➥
                    gondi_clean = re.sub(r'[^\u0C00-\u0C7F\s\,\.\?\!]', '', gondi_raw)
                    telugu_clean = re.sub(r'[^\u0C00-\u0C7F\s\,\.\?\!]', '', telugu_raw)

                    # Clean up multiple spaces and strip trailing/leading punctuation (like leftover dots from numbers)
                    gondi_clean = re.sub(r'\s+', ' ', gondi_clean).strip(' .')
                    telugu_clean = re.sub(r'\s+', ' ', telugu_clean).strip(' .')

                    if gondi_clean and telugu_clean:
                        parallel_sentences.append([gondi_clean, telugu_clean])

    # Write to TSV
    with open(OUTPUT_TSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(["Gondi_Sentence", "Telugu_Sentence"])
        writer.writerows(parallel_sentences)

    print(f"Extraction complete.")
    print(f"Successfully compiled {len(parallel_sentences)} sentences based on exact DOM rules.")

if __name__ == "__main__":
    extract_strict_dom()
