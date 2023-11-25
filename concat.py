import sys
import os
from PyPDF2 import PdfWriter as PdfFileWriter, PdfReader as PdfFileReader

help_msg = r"""Usage:
$ python3 concat.py <input1.pdf> <input2.pdf> <input3.pdf>...
"""

result_filename = "pdfs/concated.pdf"


def concat_pdf(pdf_filenames):
    """
    Concat multiple pdf files into one pdf file.
    params:
        pdf_filenames: a list of pdf files to be merged
    """
    output_pdf = PdfFileWriter()
    metadata = {}

    for pdf_filename in pdf_filenames:
        input_pdf = PdfFileReader(open(pdf_filename, "rb"))

        if input_pdf.metadata:
            metadata = input_pdf.metadata

        for i in range(len(input_pdf.pages)):
            page = input_pdf.pages[i]
            output_pdf.add_page(page)

    output_pdf.add_metadata(metadata)

    with open(result_filename, "wb") as outputStream:
        output_pdf.write(outputStream)

    os.system(f"qpdf --linearize --replace-input \"{result_filename}\"")


def main():
    if len(sys.argv) < 2:
        print(help_msg)
        return

    pdf_filenames = sys.argv[1:]
    concat_pdf(pdf_filenames)
    print(f"Result PDF saved as {result_filename}")


if __name__ == "__main__":
    main()
else:
    print("This script is not intended to be imported.")
