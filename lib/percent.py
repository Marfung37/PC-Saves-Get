from typing import TextIO
from .saves_reader import SavesReader
from .parser import Parser as WantedSavesParser, evaluate_ast

def percent(
  filepath: str, 
  wanted_saves: str,
  build_queue: str, 
  pc_num: int, 
  log_file: TextIO,
  twoline: bool = False,
  console_print: bool = True,
  include_fails: bool = False
):
  saveable_counter = 0
  total = 0
  fails = []

  wanted_saves_parser = WantedSavesParser() 
  ast = wanted_saves_parser.parse(wanted_saves) 

  save_reader = SavesReader(filepath, build_queue, pc_num, twoline)
  assign_queue = include_fails

  for row in save_reader.read(assign_queue=assign_queue):
    if evaluate_ast(ast, row.saves):
      saveable_counter += 1
    elif include_fails:
      fails.append(row.queue)
    total += 1

  print_percent(wanted_saves, saveable_counter, total, log_file, console_print, fails)

def print_percent(wanted_saves: str, saveable_counter: int, total: int, log_file: TextIO, console_print: bool, fails: list[str]):
  save_percent = (saveable_counter / total) * 100
  output = ""

  if fails:
    output += "Fails:\n"
    output += "\n".join(fails)
    output += "\n\n"

  output += f"{wanted_saves}: {save_percent:.2f}% [{saveable_counter}/{total}]"

  log_file.write(output + '\n')

  if console_print: print(output)
