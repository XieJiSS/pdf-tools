import sys
import os
from PyPDF2 import PdfFileWriter, PdfFileReader
from io import StringIO


help_msg = r"""Usage:
$ python3 side_by_side.py <input1.pdf> <input2.pdf> [args]

Arguments:
  --no-blank-cover     Do not add a blank cover page to the result PDF.

Note: [args], if provided, must be at the tail of the argument list.
"""

result_filename = "pdfs/side_by_side_merged.pdf"
blank_cover = True


def merge_side_by_side(pdf_filename1, pdf_filename2):
    """
    Merge two pdf files side by side.
    params:
        pdf_filename1: the first pdf file
        pdf_filename2: the second pdf file
    """
    input_pdf1 = PdfFileReader(open(pdf_filename1, "rb"), strict=False)
    input_pdf2 = PdfFileReader(open(pdf_filename2, "rb"), strict=False)
    output_pdf = PdfFileWriter()

    w, h = input_pdf1.pages[0].mediabox.width, input_pdf1.pages[0].mediabox.height

    # add an additional cover page to deal with Preview.app's two-page mode
    output_pdf.add_blank_page(width=float(w), height=float(h))

    for i in range(len(input_pdf1.pages)):
        page1 = input_pdf1.pages[i]
        page2 = input_pdf2.pages[i]
        output_pdf.addPage(page1)
        output_pdf.addPage(page2)

    output_pdf.add_metadata(input_pdf1.metadata or input_pdf2.metadata or {})

    with open(result_filename, "wb") as outputStream:
        sys.stderr = StringIO()  # to suppress warnings
        output_pdf.write(outputStream)
        sys.stderr = sys.__stderr__

    os.system(f"qpdf --linearize --replace-input \"{result_filename}\"")


def main():
    if len(sys.argv) < 3:
        print(help_msg)
        return

    pdf_filename1 = sys.argv[1]
    pdf_filename2 = sys.argv[2]

    global blank_cover
    if len(sys.argv) == 4 and sys.argv[3] == "--no-blank-cover":
        blank_cover = False

    print(f"Merging {pdf_filename1} and {pdf_filename2}...")
    merge_side_by_side(pdf_filename1, pdf_filename2)
    print(f"Result PDF saved as {result_filename}")


if __name__ == "__main__":
    main()
else:
    print("This script is not intended to be imported.")
