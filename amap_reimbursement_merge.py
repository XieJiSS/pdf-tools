import re, os, sys
from typing import Optional, TypeVar, TypedDict, Dict, List
from concat import concat_pdf

invoice_re = re.compile(r"^【(?P<provider>.+)-(?P<price>[\d\.]+)元-(?P<trip_count>\d+)个行程】.+?电子发票.pdf$")
itinerary_re = re.compile(r"^【(?P<provider>.+)-(?P<price>[\d\.]+)元-(?P<trip_count>\d+)个行程】.+?电子行程单.pdf$")

T = TypeVar('T')

def unwrap(x: Optional[T]) -> T:
  if x is None:
    raise Exception("unwrapping None")

  return x

class AmapPair(TypedDict):
  invoice_pdf: str | None
  itinerary_pdf: str | None
  provider: str
  price: float
  trip_count: int

def match_files(directory) -> Dict[str, List[AmapPair]]:
  reimbursements: Dict[str, List[AmapPair]] = {}  # provider --> pairs

  for filename in os.listdir(directory):
    if os.path.isdir(filename):
      continue

    if filename == "amap_reimbursement_merged.pdf":
      print("Warning: amap_reimbursement_merged.pdf already exists. This file will be ignored & overwritten.")
      continue

    if invoice_re.match(filename):
      match = unwrap(invoice_re.match(filename))
      provider = match['provider']
      price = float(match['price'])
      trip_count = int(match['trip_count'])

      if provider not in reimbursements:
        reimbursements[provider] = []

      for pair in reimbursements[provider]:
        if pair['price'] == price and pair['trip_count'] == trip_count:
          pair['invoice_pdf'] = os.path.join(directory, filename)
          break
      else:
        reimbursements[provider].append({
          'invoice_pdf': os.path.join(directory, filename),
          'itinerary_pdf': None,
          'provider': provider,
          'price': price,
          'trip_count': trip_count,
        })
    elif itinerary_re.match(filename):
      match = unwrap(itinerary_re.match(filename))
      provider = match['provider']
      price = float(match['price'])
      trip_count = int(match['trip_count'])

      if provider not in reimbursements:
        reimbursements[provider] = []

      for pair in reimbursements[provider]:
        if pair['price'] == price and pair['trip_count'] == trip_count:
          pair['itinerary_pdf'] = os.path.join(directory, filename)
          break
      else:
        reimbursements[provider].append({
          'invoice_pdf': None,
          'itinerary_pdf': os.path.join(directory, filename),
          'provider': provider,
          'price': price,
          'trip_count': trip_count,
        })
    else:
      if not filename.startswith("."):
        print(f"Warning: unrecognized file {filename}")

  return reimbursements

def main():
  if len(sys.argv) < 2:
    print("Usage: python3 amap_reimbursement_merge.py <directory>")
    if sys.platform == "win32":
      os.system("pause")
    return

  directory = sys.argv[1]

  reimbursements = match_files(directory)

  concat_filenames = []
  total_price = 0

  for pairs in reimbursements.values():
    for pair in pairs:
      if pair['invoice_pdf'] is None:
        print(f"Missing invoice for {pair['provider']} {pair['price']} {pair['trip_count']}. Skipping...")
        continue
      if pair['itinerary_pdf'] is None:
        print(f"Missing itinerary for {pair['provider']} {pair['price']} {pair['trip_count']}. Skipping...")
        continue

      if pair['price'] > 200:
        print(f"Warning: price of {pair['provider']} is more than 200.")

      concat_filenames.append(pair['invoice_pdf'])
      concat_filenames.append(pair['itinerary_pdf'])

      total_price += pair['price']

  concat_pdf(concat_filenames, output_pdf_name=os.path.join(directory, "amap_reimbursement_merged.pdf"))

  print(round(total_price, 3))

  if sys.platform == "win32":
    os.system("pause")

if __name__ == '__main__':
  main()
