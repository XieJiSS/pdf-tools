import sys
import os
from PyPDF2 import PdfWriter as PdfFileWriter, PdfReader as PdfFileReader

help_msg = r"""Usage:
$ python3 concat.py <input1.pdf> <input2.pdf> <input3.pdf>...
"""

result_filename = "pdfs/concated.pdf"


def concat_pdf(pdf_filenames, /, output_pdf_name = result_filename):
    """
    Concat multiple pdf files into one pdf file.
    params:
        pdf_filenames: a list of pdf files to be merged
    """
    output_pdf = PdfFileWriter()
    metadata = {}

    for pdf_filename in pdf_filenames:
        try:
            input_pdf = PdfFileReader(open(pdf_filename, "rb"))
        except Exception as e:
            print(f"Warning: failed to open {pdf_filename} due to {e}. Skipping...")
            continue

        if input_pdf.metadata:
            metadata = input_pdf.metadata

        for i in range(len(input_pdf.pages)):
            page = input_pdf.pages[i]
            output_pdf.add_page(page)

    output_pdf.add_metadata(metadata)

    with open(output_pdf_name, "wb") as output_stream:
        output_pdf.write(output_stream)

    os.system(f"qpdf --linearize --replace-input \"{output_pdf_name}\"")


def main():
    if len(sys.argv) < 2:
        print(help_msg)
        return

    pdf_filenames = sys.argv[1:]
    concat_pdf(pdf_filenames)
    print(f"Result PDF saved as {result_filename}")


if __name__ == "__main__":
    main()
