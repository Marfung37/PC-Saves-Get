import csv
from typing import TextIO
from .saves_reader import SavesReader, COLUMN_QUEUE, COLUMN_FUMEN_COUNT, COLUMN_USED_PIECES, COLUMN_UNUSED_PIECES, COLUMN_FUMENS, COLUMN_UNUSED_PIECES_DELIMITOR, COLUMN_FUMENS_DELIMITOR
from .parser import Parser as WantedSavesParser, evaluate_ast_all
from .utils import fumen_combine, fumen_combine_comments, make_fumen_url, make_tiny
from .minimal import fumens_to_graph, find_minimal_nodes, find_best_set

PATH_COLUMNS = [COLUMN_QUEUE, COLUMN_FUMEN_COUNT, COLUMN_USED_PIECES, COLUMN_UNUSED_PIECES, COLUMN_FUMENS]

def filter(
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
  cumulative_percent: bool = False,
  output_type: str = "minimal",
  output_path: str = "",
  tinyurl: bool = True,
):
  unique_fumens = set()
  line_queue_fumens_map = {}
  line_fumens = []
  total = 0

  wanted_saves_parser = WantedSavesParser() 
  asts = []
  for wanted_save in wanted_saves:
    asts.append(wanted_saves_parser.parse(wanted_save))

  save_reader = SavesReader(filepath, build, leftover, width, height, hold)

  outfile = None
  filtered_path = None
  if output_type == "file":
    outfile = open(output_path, 'w')
    filtered_path = csv.DictWriter(outfile, PATH_COLUMNS)
    filtered_path.writeheader()

  for row in save_reader.read(assign_fumens=True, assign_line=True):
    # get first index that satisfies the save
    indicies = []

    if row.solveable:
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

    elif output_type == "minimal" and len(new_fumens) > 0:
      line_queue_fumens_map[row.queue] = new_fumens
      line_fumens.append(new_fumens)

    elif filtered_path is not None:
      row.line[COLUMN_FUMENS] = COLUMN_FUMENS_DELIMITOR.join(new_fumens)
      
      unused_pieces = row.line[COLUMN_UNUSED_PIECES].split(COLUMN_UNUSED_PIECES_DELIMITOR)
      row.line[COLUMN_UNUSED_PIECES] = COLUMN_UNUSED_PIECES_DELIMITOR.join([unused_pieces[i] for i in indicies])
      
      row.line[COLUMN_FUMEN_COUNT] = str(len(new_fumens))
      row.line[COLUMN_USED_PIECES] = '' # empty as not useful
   
      filtered_path.writerow(row.line)

    total += 1

  if outfile is not None:
    outfile.close()

  if output_type == "unique":
    # combine all the fumens together
    unique_solves = fumen_combine(list(unique_fumens))
    log_file.write(unique_solves)
    if console_print:
      print(unique_solves)
  elif output_type == "minimal":
    generate_minimals(labels, line_fumens, line_queue_fumens_map, total, log_file, console_print, tinyurl, cumulative_percent)

def generate_minimals(
  labels: list[str], 
  line_fumens: list[list[str]], 
  line_queue_fumens_map: dict[str, list[str]], 
  total: int,
  log_file: TextIO, 
  console_print: bool, 
  tinyurl: bool, 
  cumulative_percent: bool
):
  graph = fumens_to_graph(line_fumens)

  log_file.write(f"{len(graph.edges)} edges, {len(graph.nodes)} nodes\n")
  print(f"{len(graph.edges)} edges, {len(graph.nodes)} nodes")

  minimal_sets = find_minimal_nodes(graph.edges)
  print(f'You must learn {minimal_sets.count} solutions to cover all queues. There are {len(minimal_sets.sets)} combinations of solutions to cover all patterns.');
  
  best_set = find_best_set(minimal_sets.sets, log_file)
  fumen_set = set(map(lambda n: n.key, best_set))

  fumen_queue_map = {}
  for queue, fumens in line_queue_fumens_map.items():
    for fumen in fumens:
      if fumen not in fumen_set: continue

      queues = fumen_queue_map.get(fumen)
      if queues is None:
        fumen_queue_map[fumen] = set()
      fumen_queue_map[fumen].add(queue)

  percents = []

  fumens = []
  cover_queues = list(fumen_queue_map.values())
  if cumulative_percent:

    queue_set = set()

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

      if largest_index == -1:
        raise Exception("Somehow minimal set isn't minimal")

      queue_set |= cover_queues[largest_index]
      cover_count = len(queue_set)
      percent = cover_count / total * 100
      percent = f': {percent:.2f}% ({cover_count}/{total})'
      percents.append(percent)
      indicies.append(largest_index)

    fumens = list(fumen_queue_map.keys())
    fumens = [fumens[i] for i in indicies]
  else:
    items_sorted = sorted(fumen_queue_map.items(), key=lambda item: len(item[1]), reverse=True)
    fumens, cover_queues = zip(*items_sorted)
    fumens = list(fumens)

    for queues in cover_queues:
      cover_count = len(queues)

      percent = cover_count / total * 100
      percent = f': {percent:.2f}% ({cover_count}/{total})'
      percents.append(percent)

  minimal_fumen = fumen_combine_comments(fumens, percents, True)
  
  line = minimal_fumen
  if tinyurl:
    try:
      line = make_tiny(make_fumen_url(minimal_fumen))
    except:
      line = "Tinyurl did not accept fumen due to url length"
  
  line = f"True minimal for {','.join(labels)}:\n{line}"
  
  log_file.write(line + '\n')
  if console_print:
    print(line)
  
