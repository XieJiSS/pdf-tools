# pdf-tools

Install PyPDF2 and pdfrw via `python3 -m pip install requirements.txt`. Also install qpdf before using any script. Make sure qpdf can be found directly in your `PATH`.

`remove_image.py` combines PyPDF2 and pdfrw's functionalities to achieve a better result. All scripts uses qpdf to produce a linearized PDF result that displays faster under bad network condition.

```shell
$ python3 remove_image.py "./pdfs/For Space OCR.pdf"
$ ls -alh ./pdfs
-rw-r--r--   1 host  staff    25M Nov  3 14:24 For Space OCR.pdf
-rw-r--r--   1 host  staff   9.7M Nov  7 11:20 image_removed_pypdf2_only.pdf
-rw-r--r--   1 host  staff   956K Nov  7 11:20 image_removed_pypdf2_pdfrw.pdf
$ python3 remove_image.py --aggressive "./pdfs/For Space OCR.pdf"
$ ls -alh ./pdfs/image_removed.pdf
-rw-r--r--   1 host  staff   699K Nov  7 11:21 image_removed_pypdf2_aggressive_pdfrw.pdf
```

Note that the PDF produced by `side_by_side.py` works better with PDF readers that supports Two-Page View, e.g. Preview.app:

![side_by_side_example](https://vip2.loli.io/2022/11/07/z564bEWAoptTgxN.png)
