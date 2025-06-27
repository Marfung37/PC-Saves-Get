from typing import TextIO
from .saves_reader import SavesReader
from .parser import Parser as WantedSavesParser, evaluate_ast
from .utils import any_index

def percent(
  filepath: str, 
  wanted_saves: list[str],
  labels: list[str],
  build_queue: str, 
  pc_num: int, 
  log_file: TextIO,
  twoline: bool = False,
  console_print: bool = True,
  include_fails: bool = False,
  over_solves: bool = False
):
  saveable_counters = [0] * len(wanted_saves)
  total = 0
  fails = []

  wanted_saves_parser = WantedSavesParser() 
  asts = []
  for wanted_save in wanted_saves:
    asts.append(wanted_saves_parser.parse(wanted_save))

  save_reader = SavesReader(filepath, build_queue, pc_num, twoline)
  assign_queue = include_fails

  for row in save_reader.read(assign_queue=assign_queue):
    # ignore rows that aren't solveable if out of solves
    if over_solves and not row.solveable:
      continue

    index = any_index(map(lambda ast: evaluate_ast(ast, row.saves), asts))

    if index is not None:
      saveable_counters[index] += 1
    elif include_fails:
      fails.append(row.queue)

    total += 1

  print_percent(labels, saveable_counters, total, log_file, console_print, fails)

def print_percent(
  labels: list[str], 
  saveable_counters: list[int], 
  total: int, 
  log_file: TextIO, 
  console_print: bool, 
  fails: list[str]
):
  save_percents = [(saveable_counter / total) * 100 if total != 0 else 0 for saveable_counter in saveable_counters]
  output = ""

  if fails:
    output += "Fails:\n"
    output += "\n".join(fails)
    output += "\n\n"

  for label, save_percent, saveable_counter in zip(labels, save_percents, saveable_counters):
    output += f"{label}: {save_percent:.2f}% [{saveable_counter}/{total}]\n"

  log_file.write(output)

  if console_print: print(output, end='')
