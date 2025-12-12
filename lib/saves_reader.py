import csv
from collections import Counter
from dataclasses import dataclass
from typing import Optional
from .formulas import WIDTHHEIGHT2NUMPIECES, LONUM2BAGCOMP
from .utils import fumen_get_comments, sort_queue
from .constants import BAG

COLUMN_QUEUE = 'ツモ'
COLUMN_FUMEN_COUNT = '対応地形数'
COLUMN_USED_PIECES = '使用ミノ'
COLUMN_UNUSED_PIECES = '未使用ミノ'
COLUMN_UNUSED_PIECES_DELIMITOR = ';'
COLUMN_FUMENS = 'テト譜'
COLUMN_FUMENS_DELIMITOR = ';'

REQUIRED_COLUMNS = {COLUMN_QUEUE, COLUMN_UNUSED_PIECES, COLUMN_FUMENS}

def _get_unused_last_bag(build: str, leftover: str, bag_comp: list[int]) -> set[str]:
  # assumes that not given an impossible build for the leftover and queues in path file
  non_last_bags = leftover + BAG * (len(bag_comp) - 2)
  last_bag_pieces_used = Counter(build) - Counter(non_last_bags)

  # the pieces used can at most have one of each piece
  unused_last_bag = Counter(BAG) - last_bag_pieces_used

  return set(unused_last_bag.elements())

@dataclass
class SavesRow:
  saves: list[str]
  solveable: bool
  queue: str
  fumens: Optional[list[list[str]]] = None
  line: Optional[dict[str, str]] = None
  warn: Optional[str] = None

class SavesReader:
  def __init__(self, filepath: str, leftover: str, build: str, width: int, height: int, hold: int):
    self.filepath = filepath
    self.leftover = leftover
    self.build = build
    self.width = width
    self.height = height
    self.hold = hold

    bag_comp = LONUM2BAGCOMP(len(self.leftover), WIDTHHEIGHT2NUMPIECES(width, height, hold))
    self.unused_last_bag = _get_unused_last_bag(build, leftover, bag_comp)
    self.leading_size = max(sum(bag_comp[:-1]), len(build))

    self._file = open(filepath, 'r', encoding="utf-8-sig")
    self.reader = csv.DictReader(self._file)
    if not REQUIRED_COLUMNS.issubset(set(self.reader.fieldnames or [])):
      missing = REQUIRED_COLUMNS - set(self.reader.fieldnames or [])
      raise ValueError(f"Missing required columns: {', '.join(missing)}. Columns found instead: {', '.join(self.reader.fieldnames or [])}")


  def __del__(self):
    self._file.close()
    del self._file

  def read(self, assign_fumens: bool = False, assign_line: bool = False):
    fumen_labels = {}

    min_num_pieces = WIDTHHEIGHT2NUMPIECES(self.width, self.height, 0)
    leftover_ctr = Counter(self.leftover)
    build_ctr = Counter(self.build)
    unused_leftover = leftover_ctr - build_ctr # leftover pieces not used

    for row in self.reader:
      saves = []
      save_fumens = []

      solveable = row[COLUMN_FUMENS] != ''
      if not solveable:
        save_row = SavesRow([], solveable, row[COLUMN_QUEUE])
        if assign_fumens: save_row.fumens = []
        if assign_line: save_row.line = row
        yield save_row
        continue

      full_queue = self.build + row[COLUMN_QUEUE]
      
      # since some leftover isn't used then shows up in the queue
      # check if what is expected to be the first pieces is leftover pieces
      if Counter(row[COLUMN_QUEUE][:unused_leftover.total()]) != unused_leftover:
        raise ValueError(f"Found {row[COLUMN_QUEUE]} in path.csv, but expected to start with pieces not used from leftover {''.join(unused_leftover.elements())}")

      # check if valid length
      if min_num_pieces > len(full_queue):
        raise ValueError(f"Full queue could not produce a {self.width}x{self.height} PC. Likely build '{self.build}' ('X' denotes unknown piece) is too short or maybe dimensions of PC is incorrect")

      following_bag = Counter(full_queue[:len(self.leftover) + 7]) - leftover_ctr

      if len(set(following_bag)) != following_bag.total():
        raise ValueError(f"Leftover/build inconsistent with queues in path.csv (e.g. {row[COLUMN_QUEUE]}). Bag expected for first 7 pieces not part of leftover {''.join(following_bag.elements())} but got repeated pieces.")

      # get the rest of the pieces in the last bag
      unseen_last_bag_part = self.unused_last_bag - set(full_queue[self.leading_size:])
      
      queue_ctr = Counter(row[COLUMN_QUEUE])
         
      for unused_piece in row[COLUMN_UNUSED_PIECES].split(COLUMN_UNUSED_PIECES_DELIMITOR):
        save = ''.join(unseen_last_bag_part) + unused_piece
        save = sort_queue(save)
        saves.append(save)

        if assign_fumens:
          curr_save_fumens = []
          # find the fumen that didn't use this piece
          for fumen in row[COLUMN_FUMENS].split(COLUMN_FUMENS_DELIMITOR):
            # TODO: fix code for multihold
            if fumen not in fumen_labels:
              # the comment contains what pieces used in the solve
              # get the sum of the values of the characters store in dict for fast lookup
              fumen_labels[fumen] = Counter(fumen_get_comments(fumen)[0])
            comment = fumen_labels[fumen]

            fumen_unused_piece = queue_ctr - comment
            if Counter(unused_piece) == fumen_unused_piece:
              curr_save_fumens.append(fumen)
          save_fumens.append(curr_save_fumens)

      save_row = SavesRow(saves, solveable, row[COLUMN_QUEUE])
      if assign_fumens: save_row.fumens = save_fumens
      if assign_line: save_row.line = row
      elif min_num_pieces + self.hold < len(full_queue):
        save_row.warn = "More pieces than possibly used in path.csv. Maybe the leftover length isn't correct"

      yield save_row

if __name__ == '__main__':
  reader = SavesReader('../output/path.csv', 'OILJO', 'O', 10, 4, 1)

  for val in reader.read(assign_fumens=False):
    print(val)
