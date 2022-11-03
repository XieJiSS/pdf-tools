import sys
import os
from PyPDF2 import PdfFileWriter, PdfFileReader

help_msg = r"""Usage:
$ python3 split.py <input.pdf> <start_page> <end_page>
$ python3 split.py <input.pdf> <result_pdfs_count>
"""


def split_pdf(pdf_filename, result_filename, start_page, end_page):
    """
    Extract specific pages from a pdf file, and save to a new pdf file.
    params:
        pdf_filename: the pdf file to be extracted
        result_filename: the new pdf file to be saved
        start_page: the start page number, inclusive, 0-based
        end_page: the end page number, exclusive, 0-based
    """
    input_pdf = PdfFileReader(open(pdf_filename, "rb"))
    output_pdf = PdfFileWriter()

    for i in range(start_page, end_page):
        page = input_pdf.pages[i]
        output_pdf.addPage(page)

    output_pdf.remove_images()
    output_pdf.add_metadata(input_pdf.metadata or {})

    with open(result_filename, "wb") as outputStream:
        output_pdf.write(outputStream)

    os.system(f"qpdf --linearize --replace-input \"{result_filename}\"")


def main():
    if len(sys.argv) < 3:
        print(help_msg)
        return

    if len(sys.argv) == 4:
        pdf_filename = sys.argv[1]
        start_page = int(sys.argv[2])
        end_page = int(sys.argv[3])
        result_filename = f"{pdf_filename[:-4]}_{start_page + 1}_{end_page}.pdf"
        split_pdf(pdf_filename, result_filename, start_page, end_page)
        print(f"Result PDF saved as {result_filename}.")
        return

    if len(sys.argv) == 3:
        pdf_filename = sys.argv[1]
        result_pdfs_count = int(sys.argv[2])
        input_pdf = PdfFileReader(open(pdf_filename, "rb"))
        pages_count = len(input_pdf.pages)
        pages_per_pdf = pages_count // result_pdfs_count
        for i in range(result_pdfs_count - 1):
            start_page = i * pages_per_pdf
            end_page = (i + 1) * pages_per_pdf
            result_filename = f"{pdf_filename[:-4]}_{start_page + 1}_{end_page}.pdf"
            split_pdf(pdf_filename, result_filename, start_page, end_page)
            print(f"Result PDF saved as {result_filename}.")
        start_page = (result_pdfs_count - 1) * pages_per_pdf
        end_page = pages_count
        result_filename = f"{pdf_filename[:-4]}_{start_page + 1}_{end_page}.pdf"
        split_pdf(pdf_filename, result_filename, start_page, end_page)
        print(f"Result PDF saved as {result_filename}.")
        return


if __name__ == "__main__":
    main()
else:
    print("This script is not intended to be imported.")
