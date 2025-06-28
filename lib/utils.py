import py_fumen_py as pf
import re
from .constants import BAG
from typing import Iterable

PIECEVALS = {
  'T': 1,
  'I': 2,
  'L': 3,
  'J': 4,
  'S': 5,
  'Z': 6,
  'O': 7,
}

def _decode_wrapper(fumen: str) -> list[pf.Page]:
  '''
  Decode the fumen with error handling

  Parameter:
      fumen (str): a fumen code

  Return:
      list[Page]: decoded fumen
  '''

  try:
      pages = pf.decode(fumen)
  except:
      raise RuntimeError(f"Fumen {fumen} could not be decoded")

  return pages

def fumen_combine(fumens: list[str]):
  '''
  Combine list of fumen codes into one fumen

  Parameter:
      fumens (list[str]): list of fumen codes to combine

  Return:
      str: fumens combine
  '''
  pages = []

  for fumen in fumens:
    pages += _decode_wrapper(fumen)

  return pf.encode(pages)

def fumen_combine_comments(fumens: list[str], comments: list[str]):
  '''
  Set the comments of the pages of combined fumen of only first pages

  Parameter:
      fumens (list[str]): list of fumens to combine
      comments (list[str]): list of comments to set

  Return:
      str: fumen with the changes
  '''

  pages = []

  for fumen in fumens:
    pages.append(_decode_wrapper(fumen)[0])
  for page, comment in zip(pages, comments):
    page.comment = comment

  return pf.encode(pages)

def fumen_get_comments(fumen: str):
  '''
  Get the comments of the pages of a fumen

  Parameter:
      fumen (str): a fumen code

  Return:
      list[str]: list of the comments in the fumen
  '''
  pages = _decode_wrapper(fumen)
  comments = []

  for page in pages:
    comments.append(page.comment)

  return comments

def sort_queue(queue: str) -> str:
  '''
  Sort a queue with TILJSZO ordering

  Parameter:
      queue (str): A queue with pieces in {T,I,L,J,S,Z,O}

  Return:
      str: a sorted queue following TILJSZO ordering

  '''

  sorted_queue_gen = sorted(queue, key=lambda x: PIECEVALS[x])
  sorted_queue = ''.join(list(sorted_queue_gen))

  return sorted_queue

def is_queue(text: str) -> bool:
  return re.match(f'^[{BAG}]+$', text) is not None

def queue_val(queue: str) -> int:
  return int(''.join((str(PIECEVALS[p]) for p in queue)))

def any_index(seq: Iterable[bool]) -> int | None:
  '''
  Returns the first truthy index
  '''
  return next((i for i, v in enumerate(seq) if v), None)

def all_index(seq: Iterable[bool]) -> list[int]:
  '''
  Returns all truthy indicies
  '''
  return [i for i, val in enumerate(seq) if val]

def make_fumen_url(fumen: str):
  return f"https://fumen.zui.jp/?{fumen}"

def make_tiny(url: str):
  '''
  Query tinyurl to generate a tinyurl
  '''
  import contextlib
  from urllib.parse import urlencode
  from urllib.request import urlopen

  request_url = ('http://tinyurl.com/api-create.php?' + urlencode({'url':url}))
  with contextlib.closing(urlopen(request_url)) as response:
    return response.read().decode('utf-8')
