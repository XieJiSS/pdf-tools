import os
import re
import sys

from PIL import Image

from typing import List

image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]


def merge_images_to_pdf(image_folder: str, pdf_output_path: str):
    images: List[Image.Image] = []

    image_files: List[str] = []
    for filename in os.listdir(image_folder):
        if os.path.isdir(filename):
            continue

        if os.path.splitext(filename)[1].lower() in image_extensions:
            image_files.append(os.path.join(image_folder, filename))

    # sort
    image_files.sort()

    for image_file in image_files:
        images.append(Image.open(image_file))

    images[0].save(
        pdf_output_path,
        "PDF",
        resolution=100.0,
        save_all=True,
        append_images=images[1:],
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 merge_images_to_pdf.py <image_folder>")
        exit(1)

    image_folder = sys.argv[1]
    pdf_output_path = os.path.join(image_folder, "merged.pdf")

    merge_images_to_pdf(image_folder, pdf_output_path)

    print(f"PDF saved as {pdf_output_path}")
