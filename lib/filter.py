import csv
import re
import subprocess
from typing import TextIO
from .saves_reader import SavesReader, COLUMN_QUEUE, COLUMN_FUMEN_COUNT, COLUMN_USED_PIECES, COLUMN_UNUSED_PIECES, COLUMN_FUMENS, COLUMN_UNUSED_PIECES_DELIMITOR, COLUMN_FUMENS_DELIMITOR
from .parser import Parser as WantedSavesParser, evaluate_ast_all
from .utils import fumen_combine, fumen_combine_comments, make_fumen_url, make_tiny

PATH_COLUMNS = [COLUMN_QUEUE, COLUMN_FUMEN_COUNT, COLUMN_USED_PIECES, COLUMN_UNUSED_PIECES, COLUMN_FUMENS]
STRICT_MINIMAL_FILENAME = "path_minimal_strict.md"
STRICT_MINIMAL_QUEUE_DELIMITOR = ","

def filter(
  filepath: str, 
  output_path: str,
  wanted_saves: list[str],
  labels: list[str],
  build: str, 
  leftover: str, 
  pc_num: int, 
  log_file: TextIO,
  twoline: bool = False,
  console_print: bool = True,
  cumulative_percent: bool = False,
  output_type: str = "minimal",
  tinyurl: bool = True,
):
  unique_fumens = set()

  wanted_saves_parser = WantedSavesParser() 
  asts = []
  for wanted_save in wanted_saves:
    asts.append(wanted_saves_parser.parse(wanted_save))

  save_reader = SavesReader(filepath, build, leftover, pc_num, twoline)

  outfile = None
  filtered_path = None
  if output_type != "unique":
    outfile = open(output_path, 'w')
    filtered_path = csv.DictWriter(outfile, PATH_COLUMNS)
    filtered_path.writeheader()

  for row in save_reader.read(assign_fumens=True, assign_line=True):
    # ignore rows that aren't solveable
    # TODO: this give incorrect filtered path
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
    if output_type == "unique":
      unique_fumens |= set(new_fumens)
      continue

    row.line[COLUMN_FUMENS] = COLUMN_FUMENS_DELIMITOR.join(new_fumens)
    
    unused_pieces = row.line[COLUMN_UNUSED_PIECES].split(COLUMN_UNUSED_PIECES_DELIMITOR)
    row.line[COLUMN_UNUSED_PIECES] = COLUMN_UNUSED_PIECES_DELIMITOR.join([unused_pieces[i] for i in indicies])
    
    row.line[COLUMN_FUMEN_COUNT] = str(len(new_fumens))
    row.line[COLUMN_USED_PIECES] = '' # empty as not useful
    
    if filtered_path is not None:
      filtered_path.writerow(row.line)

  if outfile is not None:
    outfile.close()

  if output_type == "unique":
    # combine all the fumens together
    unique_solves = fumen_combine(list(unique_fumens))
    log_file.write(unique_solves)
    if console_print:
      print(unique_solves)
  elif output_type == "minimal":
    generate_minimals(labels, output_path, log_file, console_print, tinyurl, cumulative_percent)

def read_strict_minimals(filepath: str, cumulative_percent: bool = False) -> str:

  with open(filepath, "r") as infile:
    lines = infile.readlines()

  re_success = re.match(r'Success rate: \d{2,3}\.\d{2}% \(\d+ / (\d+)\)', lines[2])
  if re_success is None:
    raise RuntimeError("Expected success rate in strict minimals file but not found")

  total = int(re_success.group(1))
  fumens = re.findall("(v115@[a-zA-Z0-9?/+]*)", lines[6])

  percents = []
  if cumulative_percent:
    queue_set = set()
    cover_queues = []
    # get sets of the queues the solves cover
    for line in lines[16::9]:
      cover_queues.append(set(line.strip().split(STRICT_MINIMAL_QUEUE_DELIMITOR)))

    # greedy find the solve with most coverage
    # first one, always first fumen has equally most coverage
    indicies = []
    queue_set = set()

    # get the solve with largest remaining cover
    for _ in range(len(cover_queues)):
      largest_size = 0
      largest_index = -1
      for i in range(len(cover_queues)):
        if i in indicies:
          continue
        size = len(cover_queues[i] - queue_set)
        if size > largest_size:
          largest_size = size
          largest_index = i

      queue_set |= cover_queues[largest_index]
      cover_count = len(queue_set)
      percent = cover_count / total * 100
      percent = f'{percent:.2f}% ({cover_count}/{total})'
      percents.append(percent)
      indicies.append(largest_index)

    fumens = [fumens[i] for i in indicies]
  else:
    for line in lines[13::9]:
      re_cover = re.match(r"(\d+)", line)
      if re_cover is None:
        raise RuntimeError("Expected number of cover in strict minimals file but not found")

      cover_count = int(re_cover.group(1))

      percent = cover_count / total * 100
      percent = f'{percent:.2f}% ({cover_count}/{total})'
      percents.append(percent)

  return fumen_combine_comments(fumens, percents)

def generate_minimals(labels: list[str], filtered_path: str, log_file: TextIO, console_print: bool, tinyurl: bool, cumulative_percent: bool):
  subprocess.run(['sfinder-minimal', filtered_path])

  fumen = read_strict_minimals(STRICT_MINIMAL_FILENAME, cumulative_percent)

  line = fumen
  if tinyurl:
    try:
      line = make_tiny(make_fumen_url(fumen))
    except:
      line = "Tinyurl did not accept fumen due to url length"

  line = f"True minimal for {','.join(labels)}:\n{line}"

  log_file.write(line + '\n')
  if console_print:
    print(line)
  
