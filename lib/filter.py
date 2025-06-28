from typing import TextIO
import csv
from .saves_reader import SavesReader, COLUMN_QUEUE, COLUMN_FUMEN_COUNT, COLUMN_USED_PIECES, COLUMN_UNUSED_PIECES, COLUMN_FUMENS, COLUMN_UNUSED_PIECES_DELIMITOR, COLUMN_FUMENS_DELIMITOR
from .parser import Parser as WantedSavesParser, evaluate_ast_all

PATH_COLUMNS = [COLUMN_QUEUE, COLUMN_FUMEN_COUNT, COLUMN_USED_PIECES, COLUMN_UNUSED_PIECES, COLUMN_FUMENS]

def filter(
  filepath: str, 
  output_path: str,
  wanted_saves: list[str],
  build_queue: str, 
  pc_num: int, 
  log_file: TextIO,
  twoline: bool = False,
  console_print: bool = True,
  cumulative_percent: bool = False,
  output_type: str = "minimal",
  tinyurl: bool = True,
  fumen_code: bool = False
):
  wanted_saves_parser = WantedSavesParser() 
  asts = []
  for wanted_save in wanted_saves:
    asts.append(wanted_saves_parser.parse(wanted_save))

  save_reader = SavesReader(filepath, build_queue, pc_num, twoline)

  outfile = open(output_path, 'w')
  filtered_path = csv.DictWriter(outfile, PATH_COLUMNS)
  filtered_path.writeheader()

  for row in save_reader.read(assign_fumens=True, assign_line=True):
    # ignore rows that aren't solveable
    if not row.solveable:
      continue

    # get first index that satisfies the save
    indicies = []

    for ast in asts:
      indicies = evaluate_ast_all(ast, row.saves)
      if len(indicies) > 0:
        break

    if row.fumens is None:
      raise RuntimeError("Expected fumens to be populated from save reader")
    if row.line is None:
      raise RuntimeError("Expected line to be populated from save reader")
    
    new_fumens = []
    for i in indicies:
      new_fumens += row.fumens[i]
    row.line[COLUMN_FUMENS] = COLUMN_FUMENS_DELIMITOR.join(new_fumens)
    
    unused_pieces = row.line[COLUMN_UNUSED_PIECES].split(COLUMN_UNUSED_PIECES_DELIMITOR)
    row.line[COLUMN_UNUSED_PIECES] = COLUMN_UNUSED_PIECES_DELIMITOR.join([unused_pieces[i] for i in indicies])
    
    row.line[COLUMN_FUMEN_COUNT] = str(len(new_fumens))
    row.line[COLUMN_USED_PIECES] = '' # empty as not useful
    
    filtered_path.writerow(row.line)

  outfile.close()
