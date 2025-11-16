from typing import TextIO
from dataclasses import dataclass
from .saves_reader import SavesReader
from .parser import Parser as WantedSavesParser, evaluate_ast
from .utils import any_index, queue_val, sort_queue

@dataclass
class PercentNode:
  count: int = 0
  children: dict[str, "PercentNode"] | None = None

  def __add__(self, other):
    if isinstance(other, int):
      return self.count + other
    elif isinstance(other, type(self)):
      return self.count + other.count
    else:
      raise TypeError(
        "unsupported operand for +: "
        f"'{type(self).__name__}' and '{type(other).__name__}'"
      )

  def __iadd__(self, other):
    if isinstance(other, int):
      self.count += other
      return self
    elif isinstance(other, type(self)):
      self.count += other.count
      return self
    else:
      raise TypeError(
        "unsupported operand for +=: "
        f"'{type(self).__name__}' and '{type(other).__name__}'"
      )

def _get_nodes(queue: str, node: PercentNode, depth: int):
  # create the nodes if not exist
  nodes = [node]
  for piece in queue[:depth]:
    if node.children is None:
      node.children = {}
    if piece not in node.children:
      node.children[piece] = PercentNode()
    node = node.children[piece]
    nodes.append(node)
  return nodes

def percent(
  filepath: str, 
  wanted_saves: list[str],
  labels: list[str],
  build: str, 
  leftover: str,
  width: int,
  height: int,
  hold: int,
  log_file: TextIO,
  console_print: bool = True,
  include_fails: bool = False,
  over_solves: bool = False,
  all_saves: bool = False,
  tree_depth: int = 0
):
  saveable_counters = [PercentNode() for _ in range(len(wanted_saves))]
  total: PercentNode = PercentNode(0)
  fails = []
  all_saves_dict: dict[str, int] = {}

  wanted_saves_parser = WantedSavesParser() 
  asts = []
  for wanted_save in wanted_saves:
    asts.append(wanted_saves_parser.parse(wanted_save))

  save_reader = SavesReader(filepath, build, leftover, width, height, hold)

  for row in save_reader.read():
    # ignore rows that aren't solveable if out of solves
    if over_solves and not row.solveable:
      continue
    
    if all_saves:
      # all saves will store the saves in a dict
      for save in row.saves:
        if save not in all_saves_dict:
          all_saves_dict[save] = 1
        else:
          all_saves_dict[save] += 1
      total += 1
    else:
      # get first index that satisfies the save
      if len(row.saves) == 0:
        index = None
      else:
        index = any_index(map(lambda ast: evaluate_ast(ast, row.saves), asts))

      if index is not None:
        for node in _get_nodes(row.queue, saveable_counters[index], tree_depth):
          node += 1
      elif include_fails:
        fails.append(row.queue)

      for node in _get_nodes(row.queue, total, tree_depth):
        node += 1

  if all_saves:
    # sort items of the dict
    labels, raw_saveable_counters = [list(t) for t in zip(*sorted(all_saves_dict.items(), key=lambda x: queue_val(x[0])))]
    saveable_counters = [PercentNode(a) for a in raw_saveable_counters]

  print_percent(labels, saveable_counters, total, log_file, console_print, fails, tree_depth)

def _print_tree_percent_helper(pieces: str, curr_node: PercentNode, curr_total_node: PercentNode, tree_depth: int, curr_depth: int = 0):
  output = ""
  save_percent = (curr_node.count / curr_total_node.count) * 100 if curr_total_node.count != 0 else 0

  if curr_depth > 0:
    output += '  ' * (curr_depth - 1) + f'∟ {pieces} -> {save_percent:.2f}% [{curr_node.count}/{curr_total_node.count}]\n'
  
  if curr_depth < tree_depth and curr_node.children is not None and curr_total_node.children is not None:
    for piece in sort_queue(''.join(curr_node.children.keys())):
      output += _print_tree_percent_helper(pieces + piece, curr_node.children[piece], curr_total_node.children[piece], tree_depth, curr_depth + 1)

  return output

def print_percent(
  labels: list[str], 
  saveable_counters: list[PercentNode], 
  total: PercentNode,
  log_file: TextIO, 
  console_print: bool, 
  fails: list[str],
  tree_depth: int,
):
  output = ""

  if fails:
    output += "Fails:\n"
    output += "\n".join(fails)
    output += "\n\n"

  for label, saveable_counter in zip(labels, saveable_counters):
    save_percent = (saveable_counter.count / total.count) * 100 if total.count != 0 else 0
    output += f"{label}: {save_percent:.2f}% [{saveable_counter.count}/{total.count}]\n"
    if tree_depth == 0:
      continue

    # handling tree
    output += _print_tree_percent_helper('', saveable_counter, total, tree_depth)

  log_file.write(output)

  if console_print: print(output, end='')
