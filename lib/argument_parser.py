import argparse
import json
from .constants import DEFAULT_SAVES_JSON, DEFAULT_PATH_FILE, DEFAULT_LAST_OUTPUT_FILE, DEFAULT_FILTERED_PATH_FILE, WANTED_SAVE_COMMENT_DELIMITOR, WANTED_SAVE_DELIMITOR
from .percent import percent
from .filter import filter
from .utils import is_queue
from .formulas import PCNUM2LONUM

def parse_wanted_saves(raw_keys: list[str], raw_wanted_saves: list[str], saves_path: str) -> tuple[list[str], list[str]]:
  # get the wanted saves
  data = []
  wanted_saves = []
  labels = []
  
  if raw_keys:
    with open(saves_path, 'r') as savesfile:
      saves_map = json.loads(savesfile.read())
    for key in raw_keys:
      if key not in saves_map:
        print(f"Key {key} not found in {saves_path}")
        exit(0)
      data += saves_map[key]
  if raw_wanted_saves:
    for raw_wanted_save in raw_wanted_saves:
      data += raw_wanted_save.split(WANTED_SAVE_DELIMITOR)

  for ele in data:
    ele_split = ele.split(WANTED_SAVE_COMMENT_DELIMITOR)
    if len(ele_split) > 2:
      print(f"Too many {WANTED_SAVE_COMMENT_DELIMITOR} in {ele}")
      exit(0)

    if len(ele_split) == 1:
      wanted_save = (label := ele_split[0])
    else:
      wanted_save, label = ele_split
    wanted_saves.append(wanted_save)
    labels.append(label)

  return wanted_saves, labels

def parse_percent_args(args):
  '''
  Parse the arguments for percent subcommand to pass to run calculation of save percent
  '''
  if not (args.key or args.wanted_saves or args.all):
    print("Expected -k, -w, or -a to be set")
    exit(0)

  # out of bounds pc number
  if args.pc_num < 1 or 9 < args.pc_num:
    print("PC Number expected to be within 1-9")
    exit(0)

  # build uses only pieces in TILJSZO
  if not is_queue(args.build) or not is_queue(args.leftover):
    print("Build and Leftover expected to contain only TILJSZO pieces")
    exit(0)

  # leftover isn't right length
  if len(args.leftover) != PCNUM2LONUM(args.pc_num):
    print(f"Leftover expected to contain {PCNUM2LONUM(args.pc_num)} pieces for pc {args.pc_num}")
    exit(0)

  log_file = open(args.log_path, 'w')
  if args.all:
    percent(args.path_file, [], [], args.build, args.leftover, args.pc_num, log_file, args.two_line, args.console_print, args.fails, args.over_solves, args.all)
    log_file.close()
    return

  wanted_saves, labels = parse_wanted_saves(args.key, args.wanted_saves, args.saves_path)

  if args.best_save:
    percent(args.path_file, wanted_saves, labels, args.build, args.leftover, args.pc_num, log_file, args.two_line, args.console_print, args.fails, args.over_solves, False, args.tree_depth)
  else:
    for wanted_save, label in zip(wanted_saves, labels):
      percent(args.path_file, [wanted_save], [label], args.build, args.leftover, args.pc_num, log_file, args.two_line, args.console_print, args.fails, args.over_solves, False, args.tree_depth)

  log_file.close()

def parse_filter_args(args):
  '''
  Parse the arguments for filter subcommand to pass to filter out path file
  '''
  if not (args.key or args.wanted_saves):
    print("Expected -k or -w to be set")
    exit(0)

  # out of bounds pc number
  if args.pc_num < 1 or 9 < args.pc_num:
    print("PC Number expected to be within 1-9")
    exit(0)

  # build uses only pieces in TILJSZO
  if not is_queue(args.build) or not is_queue(args.leftover):
    print("Build and Leftover expected to contain only TILJSZO pieces")
    exit(0)

  # leftover isn't right length
  if len(args.leftover) != PCNUM2LONUM(args.pc_num):
    print(f"Leftover expected to contain {PCNUM2LONUM(args.pc_num)} pieces for pc {args.pc_num}")
    exit(0)

  log_file = open(args.log_path, 'w')

  wanted_saves, labels = parse_wanted_saves(args.key, args.wanted_saves, args.saves_path)


  if args.best_save:
    filter(args.path_file, args.filtered_path, wanted_saves, labels, args.build, args.leftover, args.pc_num, log_file, args.two_line, args.console_print, args.cumulative, args.solve, args.tinyurl)
  else:
    if args.index < -len(wanted_saves) or args.index >= len(wanted_saves):
      print(f"Index out of bounds for wanted saves")

    filter(args.path_file, args.filtered_path, [wanted_saves[args.index]], [labels[args.index]], args.build, args.leftover, args.pc_num, log_file, args.two_line, args.console_print, args.cumulative, args.solve, args.tinyurl)

  log_file.close()

arg_parser = argparse.ArgumentParser(usage="<cmd> [options]", description="A tool for further expansion of the saves from path.csv")
arg_subparsers = arg_parser.add_subparsers()

percent_parser = arg_subparsers.add_parser("percent", help="Give the percents of saves using the path.csv file with wanted save expression")
percent_parser.set_defaults(func=parse_percent_args)
percent_parser.add_argument("-w", "--wanted-saves", help="the save expression (required if there isn't -k nor -a)", metavar="<string>", nargs='+')
percent_parser.add_argument("-k", "--key", help="use preset wanted saves in the saves json (required if there isn't a -w nor -a)", metavar="<string>", nargs='+')
percent_parser.add_argument("-a", "--all", help="output all of the saves and corresponding percents (alternative to not having -k nor -w)", action="store_true")
percent_parser.add_argument("-bs", "--best-save", help="instead of listing each wanted save separately, it prioritizes the first then second and so on (requires a -w or -k default: false)", action="store_true")
percent_parser.add_argument("-b", "--build", help="pieces in the build of the setup", metavar="<string>", type=str, required=True)
percent_parser.add_argument("-l", "--leftover", help="pieces leftover for this pc", metavar="<string>", type=str, required=True)
percent_parser.add_argument("-pc", "--pc-num", help="pc number for the setup", metavar="<int>", type=int, required=True)
percent_parser.add_argument("-tl", "--two-line", help="setup is two lines (default: False)", action="store_true")
percent_parser.add_argument("-td", "--tree-depth", help="set the tree depth of pieces in percent (default: 0)", metavar="<int>", type=int, default=0)
percent_parser.add_argument("-f", "--path-file", help="path filepath (default: output/path.csv)", metavar="<filepath>", default=DEFAULT_PATH_FILE, type=str)
percent_parser.add_argument("-lp", "--log-path", help="output filepath (default: output/last_output.txt)", metavar="<filepath>", default=DEFAULT_LAST_OUTPUT_FILE, type=str)
percent_parser.add_argument("-sp", "--saves-path", help="path to json file with preset wanted saves (default: GITROOT/saves.json)", metavar="<filepath>", default=DEFAULT_SAVES_JSON, type=str)
percent_parser.add_argument("-pr", "--console-print", help="log to terminal (default: True)", action="store_false")
percent_parser.add_argument("-fa", "--fails", help="include the fail queues for saves in output (default: False)", action="store_true")
percent_parser.add_argument("-os", "--over-solves", help="have the percents be out of when setup is solvable (default: False)", action="store_true")

filter_parser = arg_subparsers.add_parser("filter", help="filter path.csv of fumens that doesn't meet the wanted saves")
filter_parser.set_defaults(func=parse_filter_args)
filter_parser.add_argument("-w", "--wanted-saves", help="the save expression (required if there isn't -k)", metavar="<string>", nargs='+')
filter_parser.add_argument("-k", "--key", help="use wantedPiecesMap.json for preset wanted saves (required if there isn't a -w)", metavar="<string>", nargs='+')
filter_parser.add_argument("-i", "--index", help="index of -k or -w to pick which expression to filter by (default=0)", metavar="<int>", type=int, default=0)
filter_parser.add_argument("-b", "--build", help="pieces in the build of the setup", metavar="<string>", type=str, required=True)
filter_parser.add_argument("-l", "--leftover", help="pieces leftover for this pc", metavar="<string>", type=str, required=True)
filter_parser.add_argument("-pc", "--pc-num", help="pc number for the setup", metavar="<int>", type=int, required=True)
filter_parser.add_argument("-tl", "--two-line", help="setup is two lines (default: False)", action="store_true")
filter_parser.add_argument("-bs", "--best-save", help="instead of listing each wanted save separately, it prioritizes the first then second and so on (default: False)", action="store_true")
filter_parser.add_argument("-c", "--cumulative", help="gives percents cumulatively in fumens of a minimal set (default: False)", action="store_true")
filter_parser.add_argument("-f", "--path-file", help="path filepath (default: output/path.csv)", metavar="<filepath>", default=DEFAULT_PATH_FILE, type=str)
filter_parser.add_argument("-lp", "--log-path", help="output filepath (default: output/last_output.txt)", metavar="<filepath>", default=DEFAULT_LAST_OUTPUT_FILE, type=str)
filter_parser.add_argument("-sp", "--saves-path", help="path to json file with preset wanted saves (default: GITROOT/saves.json)", metavar="<filepath>", default=DEFAULT_SAVES_JSON, type=str)
filter_parser.add_argument("-fp", "--filtered-path", help="output filtered path file (default: output/filtered_path.txt)", metavar="<filepath>", default=DEFAULT_FILTERED_PATH_FILE, type=str)
filter_parser.add_argument("-pr", "--console-print", help="log to terminal (default: True)", action="store_false")
filter_parser.add_argument("-s", "--solve", help="setting for how to output solve (minimal, unique, none) (default: minimal)", choices={"minimal", "unique", "none"}, metavar="<string>", default="minimal", type=str)
filter_parser.add_argument("-t", "--tinyurl", help="output the link with tinyurl if possible (default: True)", action="store_false")

