import csv
from collections import Counter
from dataclasses import dataclass
from typing import Optional
from .formulas import PCNUM2LONUM, LONUM2BAGCOMP
from .utils import fumen_get_comments, sort_queue
from .constants import BAG, PCSIZE, HOLD

VALID_4L_PCSIZE = {PCSIZE, PCSIZE + HOLD}
VALID_2L_PCSIZE = {PCSIZE // 2, PCSIZE // 2 + HOLD}

COLUMN_QUEUE = 'ツモ'
COLUMN_FUMEN_COUNT = '対応地形数'
COLUMN_USED_PIECES = '使用ミノ'
COLUMN_UNUSED_PIECES = '未使用ミノ'
COLUMN_UNUSED_PIECES_DELIMITOR = ';'
COLUMN_FUMENS = 'テト譜'
COLUMN_FUMENS_DELIMITOR = ';'

REQUIRED_COLUMNS = {COLUMN_QUEUE, COLUMN_UNUSED_PIECES, COLUMN_FUMENS}

@dataclass
class SavesRow:
  saves: list[str]
  solveable: bool
  queue: Optional[str] = None
  fumens: Optional[list[list[str]]] = None

class SavesReader:
  def __init__(self, filepath: str, build_queue: str, pc_num: int, twoline: bool = False):
    self.filepath = filepath
    self.build_queue = build_queue
    self.pc_num = pc_num
    self.twoline = twoline

    bag_comp = LONUM2BAGCOMP(PCNUM2LONUM(pc_num), 6 if twoline else 11)
    self.leading_size = sum(bag_comp[:-1])

    self._file = open(filepath, 'r')
    self.reader = csv.DictReader(self._file)
    if not REQUIRED_COLUMNS.issubset(set(self.reader.fieldnames or [])):
      missing = REQUIRED_COLUMNS - set(self.reader.fieldnames or [])
      raise ValueError(f"Missing required columns: {', '.join(missing)}")

  def __del__(self):
    self._file.close()
    del self._file

  def read(self, assign_queue: bool = False, assign_fumens: bool = False):
    for row in self.reader:
      saves = []
      save_fumens = []

      solveable = row[COLUMN_FUMENS] != ''
      if not solveable:
        save_row = SavesRow([], solveable)
        if assign_queue: save_row.queue = row[COLUMN_QUEUE]
        if assign_fumens: save_row.fumens = []
        yield save_row
        continue

      full_queue = self.build_queue + row[COLUMN_QUEUE]

      # check if valid length
      if not ((len(full_queue) in VALID_4L_PCSIZE) or (self.twoline and len(full_queue) in VALID_2L_PCSIZE)):
        raise RuntimeError(f"Full queue could not produce a {'2' if self.twoline else '4'}l PC. Likely build queue {self.build_queue} is too short")

      # get the rest of the pieces in the last bag
      unused_last_bag = set(BAG) - set(full_queue[self.leading_size:])

      for unused_piece in row[COLUMN_UNUSED_PIECES].split(COLUMN_UNUSED_PIECES_DELIMITOR):
        save = ''.join(unused_last_bag) + unused_piece
        save = sort_queue(save)
        saves.append(save)

        if assign_fumens:
          curr_save_fumens = []
          # find the fumen that didn't use this piece
          for fumen in row[COLUMN_FUMENS].split(COLUMN_FUMENS_DELIMITOR):
            # the comment contains what pieces used in the solve
            comment = fumen_get_comments(fumen)[0]
            fumen_unused_piece = next((Counter(row[COLUMN_QUEUE]) - Counter(comment)).elements())
            if unused_piece == fumen_unused_piece:
              curr_save_fumens.append(fumen)
          save_fumens.append(curr_save_fumens)

      save_row = SavesRow(saves, solveable)
      if assign_queue: save_row.queue = row[COLUMN_QUEUE]
      if assign_fumens: save_row.fumens = save_fumens

      yield save_row

if __name__ == '__main__':
  reader = SavesReader('../output/path.csv', 'OILJO', 3, True)

  for val in reader.read(assign_fumens=False):
    print(val)
