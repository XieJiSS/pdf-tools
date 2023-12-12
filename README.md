# pdf-tools

Install PyPDF2 and pdfrw via `python3 -m pip install -r requirements.txt`.

Also, install `qpdf` before using any script. Make sure `qpdf` can be found directly in your `PATH`.

If you need to use `to_image.py`, you'll also need to have `poppler` installed in your `PATH` as well.

- Windows: https://github.com/oschwartz10612/poppler-windows/releases/latest
- MacOS: `brew install poppler`

`remove_image.py` combines PyPDF2 and pdfrw's functionalities to achieve a better result. All scripts uses qpdf to produce a linearized PDF result that displays faster under bad network condition.

```shell
$ python3 remove_image.py "./pdfs/Space OCR.pdf"
$ ls -alh ./pdfs
-rw-r--r--   1 host  staff    25M Nov  3 14:24 Space OCR.pdf
-rw-r--r--   1 host  staff   9.7M Nov  7 11:20 image_removed_pypdf2_only.pdf
-rw-r--r--   1 host  staff   956K Nov  7 11:20 image_removed_pypdf2_pdfrw.pdf
$ python3 remove_image.py --aggressive "./pdfs/Space OCR.pdf"
$ ls -alh ./pdfs/image_removed_pypdf2_aggressive_pdfrw.pdf
-rw-r--r--   1 host  staff   699K Nov  7 11:21 image_removed_pypdf2_aggressive_pdfrw.pdf
```

Note that the PDF produced by `side_by_side.py` works better with PDF readers that supports Two-Page View, e.g. Preview.app.
