import sys
from pdf2image.pdf2image import convert_from_path


def to_jpg(pdf_filename, result_basename=None):
    """
    Convert a pdf file to a jpg file.
    params:
        pdf_filename: the pdf file to be converted
        result_filename: the new jpg file to be saved
    """
    if result_basename is None:
        result_basename = pdf_filename[:-4]

    images = convert_from_path(pdf_filename)

    for i, image in enumerate(images):
        image.save(f"{result_basename}_{i + 1}.jpg", "JPEG")


def to_png(pdf_filename, result_basename=None):
    """
    Convert a pdf file to a png file.
    params:
        pdf_filename: the pdf file to be converted
        result_filename: the new png file to be saved
    """
    if result_basename is None:
        result_basename = pdf_filename[:-4]

    images = convert_from_path(pdf_filename)

    for i, image in enumerate(images):
        image.save(f"{result_basename}_{i + 1}.png", "PNG")


def main():
    # python3 to_image.py -j <pdf> [<result_basename>]
    # python3 to_image.py -p <pdf> [<result_basename>]
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 to_image.py -j <pdf> [<result_basename>]  Convert to jpg")
        print("  python3 to_image.py -p <pdf> [<result_basename>]  Convert to png")
        return

    pdf_filename = sys.argv[2]
    result_basename = None if len(sys.argv) < 4 else sys.argv[3]

    if sys.argv[1] == "-j":
        to_jpg(pdf_filename, result_basename)
    elif sys.argv[1] == "-p":
        to_png(pdf_filename, result_basename)
    else:
        print("Usage:")
        print("  python3 to_image.py -j <pdf> [<result_basename>]  Convert to jpg")
        print("  python3 to_image.py -p <pdf> [<result_basename>]  Convert to png")
        return


if __name__ == "__main__":
    main()
