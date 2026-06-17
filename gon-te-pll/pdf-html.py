import os
import zipfile
from pypdf import PdfReader, PdfWriter
from sarvamai import SarvamAI

PDF_PATH = "parallel sentences .pdf"
API_KEY = "sk_dniy9j3k_tSFYu3cVAX0Yyw7P7J8JBM1O"
PAGES_PER_CHUNK = 10
HTML_STORAGE_DIR = "saved_html_parallel"

os.makedirs(HTML_STORAGE_DIR, exist_ok=True)

def extract_pdf_to_html_with_sdk():
    client = SarvamAI(api_subscription_key=API_KEY)
    reader = PdfReader(PDF_PATH)
    total_pages = len(reader.pages)

    print(f"Total pages detected: {total_pages}")

    for start_page in range(0, total_pages, PAGES_PER_CHUNK):
        end_page = min(start_page + PAGES_PER_CHUNK, total_pages)
        print(f"\n--- Processing chunk: Pages {start_page + 1} to {end_page} ---")

        chunk_pdf_filename = f"temp_chunk_{start_page+1}_{end_page}.pdf"
        chunk_zip_filename = f"temp_output_{start_page+1}_{end_page}.zip"

        writer = PdfWriter()
        for i in range(start_page, end_page):
            writer.add_page(reader.pages[i])

        with open(chunk_pdf_filename, "wb") as f:
            writer.write(f)

        try:
            job = client.document_intelligence.create_job(
                language="te-IN",
                output_format="html"
            )

            job.upload_file(chunk_pdf_filename)
            job.start()
            status = job.wait_until_complete()

            job.download_output(chunk_zip_filename)

            with zipfile.ZipFile(chunk_zip_filename, 'r') as zip_ref:
                html_files = [name for name in zip_ref.namelist() if name.endswith('.html')]

                if html_files:
                    html_filename_in_zip = html_files[0]
                    extracted_html_path = zip_ref.extract(html_filename_in_zip, HTML_STORAGE_DIR)
                    final_html_name = os.path.join(HTML_STORAGE_DIR, f"pages_{start_page+1}_{end_page}.html")

                    if os.path.exists(final_html_name):
                        os.remove(final_html_name)
                    os.rename(extracted_html_path, final_html_name)
                    print(f"Saved: {final_html_name}")

        except Exception as e:
            print(f"Error: {e}")

        finally:
            if os.path.exists(chunk_pdf_filename):
                os.remove(chunk_pdf_filename)
            if os.path.exists(chunk_zip_filename):
                os.remove(chunk_zip_filename)

if __name__ == "__main__":
    extract_pdf_to_html_with_sdk()
