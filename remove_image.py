import sys
import os
import argparse
from io import StringIO
from PyPDF2 import PdfWriter as PdfFileWriter, PdfReader as PdfFileReader
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfArray, PdfName

parser = argparse.ArgumentParser(
    description='Remove images from PDFs to reduce size.')
parser.add_argument('input_pdf', help='input pdf file')
parser.add_argument('-a', '--aggressive', action='store_true',
                    help='Use aggressive strategy provided by PyPDF2 to remove images.')
parser.add_argument('-i', '--ignore-side-effects', action='store_true',
                    help='Ignore side effects of removing images. This may cause other /XObjects to be removed, if some /Image are deeply nested inside /XObjects that contains other subtypes of data.')
parser.add_argument('-r', '--remove-size', type=int,
                    help='Force remove images with size above SIZE bytes, even if it is not displayed or referenced. Default: 100000')

result_filename = "pdfs/image_removed.pdf"
arg_strip_size = 100000
arg_ignore_side_effects = False


# This is cherry-picked from a pdfrw official example.
def find_objects(source, valid_types=(PdfName.XObject,),
                 valid_subtypes=(PdfName.Image,),
                 no_follow=(PdfName.Parent,),
                 isinstance=isinstance, id=id, sorted=sorted,
                 reversed=reversed, PdfDict=PdfDict):
    '''
        Find all the objects of a particular kind in a document
        or array.  Defaults to looking for Form and Image XObjects.
        This could be done recursively, but some PDFs
        are quite deeply nested, so we do it without
        recursion.
        Note that we don't know exactly where things appear on pages,
        but we aim for a sort order that is (a) mostly in document order,
        and (b) reproducible.  For arrays, objects are processed in
        array order, and for dicts, they are processed in key order.
    '''
    container = (PdfDict, PdfArray)

    # Allow passing a list of pages, or a dict
    if isinstance(source, PdfDict):
        source = [source]
    else:
        source = list(source)

    visited = set()
    source.reverse()
    while source:
        obj = source.pop()
        arr = []
        if not isinstance(obj, container):
            continue
        myid = id(obj)
        if myid in visited:
            continue
        visited.add(myid)
        if isinstance(obj, PdfDict):
            if obj.Type in valid_types and obj.Subtype in valid_subtypes:
                yield obj
            arr = [y for (x, y) in sorted(obj.iteritems())
                   if x not in no_follow]
        else:
            # TODO: This forces resolution of any indirect objects in
            # the array.  It may not be necessary.  Don't know if
            # reversed() does any voodoo underneath the hood.
            # It's cheap enough for now, but might be removeable.
            obj and obj[0]
            arr = obj
        source.extend(reversed(arr))


def remove_image(pdf_filename, aggressive=False):
    """
    Remove image from pdf file.
    params:
        pdf_filename: the pdf file to remove image
    """

    print("Linearizing input PDF...")
    os.system(f"qpdf --linearize --replace-input \"{pdf_filename}\"")

    input_pdf = PdfFileReader(open(pdf_filename, "rb"), strict=True)
    output_pdf = PdfFileWriter()

    for i in range(len(input_pdf.pages)):
        page = input_pdf.pages[i]
        output_pdf.add_page(page)

    # output_pdf.remove_images(ignore_byte_string_object=aggressive)
    # output_pdf.remove_images()

    output_pdf.add_metadata(input_pdf.metadata or {})

    with open(result_filename, "wb") as outputStream:
        # sys.stderr = StringIO()  # to suppress warnings
        output_pdf.write(outputStream)
        # sys.stderr = sys.__stderr__

    print("Linearizing result PDF...")
    os.system(f"qpdf --linearize --replace-input \"{result_filename}\"")


def strip_objects(pdf, heuristic_compare_info_obj_list, compare_keys=("Width", "Height", "Length")):
    for i, page in enumerate(pdf.pages):
        # skip empty pages
        if not page.Resources.XObject:
            continue

        # Map all the objects in the page using the objects id as the key and
        # the resource name as the value.
        name_map = {indirect_obj.indirect[0]: name for name,
                    indirect_obj in page.Resources.XObject.items()}

        has_deleted = False

        before_keys = page.Resources.XObject.keys()

        for compare_info in heuristic_compare_info_obj_list:
            for obj_id in name_map:
                obj = page.Resources.XObject[name_map[obj_id]]
                if obj is None:
                    print(f"P{i} - skipping missing object", obj_id)
                    continue

                if "/Resources" in obj:
                    """Handle nested /XObjects.
                    >>> obj["/Resources"]
                    {
                      '/ProcSet': [ '/PDF', '/Text', '/ImageC', '/ImageB' ],
                      '/XObject': {
                        '/Im0': {
                          '/Height': '955',
                          '/Subtype': '/Image',
                          '/Type': '/XObject',
                          '/Width': '1103',
                          '/Length': '286609'
                        }
                      }
                    }
                    """

                    resources_obj = obj["/Resources"]
                    can_delete_resource = True
                    has_matching_nested_obj = False
                    total_length = 0
                    if "/Length" in obj:
                        total_length = int(obj["/Length"])

                    if "/XObject" in resources_obj:
                        obj_unwrap_root = resources_obj["/XObject"]
                        for nested_id, nested_obj in obj_unwrap_root.items():
                            if nested_obj is None:
                                continue

                            if "/Length" in nested_obj:
                                total_length += int(nested_obj["/Length"])

                            if "/Type" not in nested_obj or nested_obj["/Type"] != "/XObject":
                                can_delete_resource = False
                                print(
                                    f"P{i} - encountered an XObject that contains non-XObject object", nested_obj, obj_id)
                                continue
                            if "/Subtype" not in nested_obj or nested_obj["/Subtype"] != "/Image":
                                can_delete_resource = False
                                print(
                                    f"P{i} - encountered an XObject that contains non-Image XObject", nested_obj, obj_id)
                                continue

                            does_nested_obj_match = True

                            for key in compare_keys:
                                if key in compare_info and key in nested_obj and compare_info[key] == nested_obj[key]:
                                    does_nested_obj_match = False
                                    break

                            if does_nested_obj_match:
                                print(
                                    f"P{i} - found matching nested XObject {nested_id} in {obj_id}")
                                has_matching_nested_obj = True

                    if has_matching_nested_obj and (can_delete_resource or arg_ignore_side_effects):
                        print(f"P{i} - deleting object", obj_id,
                              "of size", total_length)
                        del page.Resources.XObject[name_map[obj_id]]
                        has_deleted = True
                        break
                    elif has_matching_nested_obj:
                        print(
                            f"P{i} - object {obj_id} has matching nested objects but cannot be deleted due to side-effects. Specify -f to ignore this.")
                else:
                    does_obj_match = True

                    for key in compare_keys:
                        if ('/' + key) not in obj or obj['/' + key] != compare_info[key]:
                            does_obj_match = False
                            break

                    if does_obj_match:
                        print(f"P{i} - deleting object", obj_id,
                              "of size", "/Length" in obj and obj["/Length"] or -1)
                        del page.Resources.XObject[name_map[obj_id]]
                        has_deleted = True
                        break

        after_keys = page.Resources.XObject.keys()

        if has_deleted:
            print(f"P{i} - before: {str(before_keys)}, after: {str(after_keys)}")

    return pdf


def main():
    if len(sys.argv) < 2:
        parser.print_help()
        return

    args = parser.parse_args()

    global arg_strip_size, arg_ignore_side_effects
    arg_strip_size = args.remove_size or arg_strip_size
    arg_ignore_side_effects = args.ignore_side_effects or arg_ignore_side_effects

    aggressive = args.aggressive or False

    pdf_filename = args.input_pdf

    print(f"Pruning images from {pdf_filename}...")
    remove_image(pdf_filename, aggressive)

    result_pdf = PdfReader(result_filename)
    strip_obj_info_list = []
    for obj in find_objects(result_pdf.pages):
        if obj.Length and int(obj.Length) > arg_strip_size:
            strip_obj_info_list.append({
                "Width": obj.Width,
                "Height": obj.Height,
                "Length": obj.Length
            })

    print(f"Stripping /Image /XObjects larger than {arg_strip_size}...")
    strip_objects(result_pdf, strip_obj_info_list)

    PdfWriter().write(result_filename, result_pdf)
    print(f"Final result PDF saved as {result_filename}")


if __name__ == "__main__":
    main()
else:
    print("This script is not intended to be imported.")
