import argparse
import json
from collections import Counter
from .constants import (
  DEFAULT_SAVES_JSON, 
  DEFAULT_PATH_FILE, 
  DEFAULT_LAST_OUTPUT_FILE, 
  DEFAULT_FILTERED_PATH_FILE, 
  WANTED_SAVE_COMMENT_DELIMITOR, 
  WANTED_SAVE_DELIMITOR, 
  DEFAULT_WIDTH,
  DEFAULT_HEIGHT,
  DEFAULT_HOLD
)
from .formulas import PCNUM2LONUM
from .percent import percent
from .filter import filter
from .utils import is_queue

def parse_wanted_saves(raw_keys: list[str], raw_wanted_saves: list[str], saves_path: str) -> tuple[list[str], list[str]]:
  # get the wanted saves
  data = []
  wanted_saves = []
  labels = []
  
  if raw_keys:
    with open(saves_path, 'r', encoding="utf8") as savesfile:
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

def parse_leftover_build(leftover, leftover_length, build, pc_num, hold) -> tuple[str, str]:
  # build uses only pieces in TILJSZO
  if build is not None and not is_queue(build):
    print("Build expected to contain only TILJSZO pieces")
    exit(0)

  # build uses only pieces in TILJSZO
  if not leftover and build is not None:
    print("-l must be set")
    exit(0)

  leftover = leftover.split('-')

  # valid leftover
  if len(leftover) > 2:
    print("Leftover should contain at most one '-'")
    exit(0)
  if not all(map(is_queue, leftover)):
    print("Leftover expected to contain only TILJSZO pieces aside from '-'")
    exit(0)

  if pc_num is not None:
    # inconsistent pc num and leftover length
    if leftover_length is not None and PCNUM2LONUM(pc_num) != leftover_length:
      print("Leftover length and PC number are inconsistent")
      exit(0)

    leftover_length = PCNUM2LONUM(pc_num)

  # only the leftover and checks if the options make sense
  if len(leftover) == 1 and build is not None:
    if pc_num is not None and leftover_length != len(leftover[0]):
      print("PC number doesn't match the actual length of leftover")
      exit(0)
    if leftover_length is not None and leftover_length != len(leftover[0]):
      print("Leftover length doesn't match the actual length of leftover")
      exit(0)
 
  if leftover_length is None:
    # leftover length not set from the options
    print("Either -pc or -ll must be set")
    exit(0)
  if leftover_length < 1 or leftover_length > 7:
    print("Leftover length out of valid 1-7 range")
    exit(0)

  if len(leftover) == 1 and len(leftover[0]) < leftover_length:
    leftover.append('')

  if len(leftover) == 2 and len(leftover[0]) > hold and len(leftover[1]) > 0:
    # the leftover held more than possible to hold
    print("More leftover pieces unused than possible to hold")
    exit(0)

  if len(leftover) == 1 and build is not None:
    leftover = leftover[0]
  elif len(leftover) == 2:
    used_leftover_length = leftover_length - len(leftover[0])
    build = 'X' * used_leftover_length + leftover[1]
    leftover = 'X' * used_leftover_length + leftover[0]

  leftover_ctr = Counter(leftover)
  build_ctr = Counter(build)
  only_leftover_build = build_ctr < leftover_ctr # build is only using leftover
  unused_leftover = leftover_ctr - build_ctr # leftover pieces not used

  # check if build and leftover even make sense with the hold
  if not only_leftover_build and unused_leftover.total() > hold:
    # more unused leftover pieces than what can be held
    print(f"Not possible to build {build} with given leftover {leftover} with hold {hold}")
    exit(0)

  return leftover, build

def parse_percent_args(args):
  '''
  Parse the arguments for percent subcommand to pass to run calculation of save percent
  '''
  if not (args.key or args.wanted_saves or args.all):
    print("Expected -k, -w, or -a to be set")
    exit(0)

  # valid dimensions to do a PC
  if (args.width * args.height) % 4 != 0:
    print("Width and height does not produce an area divisible by 4 necessary for a PC")
    exit(0)

  leftover, build = parse_leftover_build(args.leftover, args.leftover_length, args.build, args.pc_num, args.hold)

  log_file = open(args.log_path, 'w', encoding="utf8")
  try:
    if args.all:
      percent(args.path_file, [], [], leftover, build, args.width, args.height, args.hold, log_file, not args.no_print, args.fails, args.over_solves, args.all)
      log_file.close()
      return

    wanted_saves, labels = parse_wanted_saves(args.key, args.wanted_saves, args.saves_path)

    if args.best_save:
      percent(args.path_file, wanted_saves, labels, leftover, build, args.width, args.height, args.hold, log_file, not args.no_print, args.fails, args.over_solves, False, args.tree_depth)
    else:
      for wanted_save, label in zip(wanted_saves, labels):
        percent(args.path_file, [wanted_save], [label], leftover, build, args.width, args.height, args.hold, log_file, not args.no_print, args.fails, args.over_solves, False, args.tree_depth)
  except ValueError as e:
    print(e)

  log_file.close()

def parse_filter_args(args):
  '''
  Parse the arguments for filter subcommand to pass to filter out path file
  '''
  if not (args.key or args.wanted_saves):
    print("Expected -k or -w to be set")
    exit(0)

  # valid dimensions to do a PC
  if (args.width * args.height) % 4 != 0:
    print("Width and height does not produce an area divisible by 4 necessary for a PC")
    exit(0)

  leftover, build = parse_leftover_build(args.leftover, args.leftover_length, args.build, args.pc_num, args.hold)

  log_file = open(args.log_path, 'w', encoding="utf8")
  wanted_saves, labels = parse_wanted_saves(args.key, args.wanted_saves, args.saves_path)
  
  try:
    if args.best_save:
      filter(args.path_file, wanted_saves, labels, leftover, build, args.width, args.height, args.hold, log_file, not args.no_print, args.cumulative, args.solve, args.filtered_path, args.tinyurl)
    else:
      if args.index < -len(wanted_saves) or args.index >= len(wanted_saves):
        print(f"Index out of bounds for wanted saves")

      filter(args.path_file, [wanted_saves[args.index]], [labels[args.index]], leftover, build, args.width, args.height, args.hold, log_file, not args.no_print, args.cumulative, args.solve, args.filtered_path, args.tinyurl)
  except ValueError as e:
    print(e)

  log_file.close()

arg_parser = argparse.ArgumentParser(usage="<cmd> [options]", description="A tool for further expansion of the saves from path.csv")
arg_subparsers = arg_parser.add_subparsers()

percent_parser = arg_subparsers.add_parser("percent", help="Give the percents of saves using the path.csv file with wanted save expression")
percent_parser.set_defaults(func=parse_percent_args)
percent_parser.add_argument("-w", "--wanted-saves", help="the save expression (required if there isn't -k nor -a)", metavar="<string>", nargs='+')
percent_parser.add_argument("-k", "--key", help="use preset wanted saves in the saves json (required if there isn't a -w nor -a)", metavar="<string>", nargs='+')
percent_parser.add_argument("-a", "--all", help="output all of the saves and corresponding percents (alternative to not having -k nor -w)", action="store_true")
percent_parser.add_argument("-bs", "--best-save", help="instead of listing each wanted save separately, it prioritizes the first then second and so on (requires a -w or -k default: false)", action="store_true")
percent_parser.add_argument("-b", "--build", help="pieces in the build of the setup. Ignored if -l has '-' in expression", metavar="<string>", type=str)
percent_parser.add_argument("-l", "--leftover", help="leftover pieces for this pc. Supports T-IO for still have T from leftover and used IO from following bag. Not specified implies building setup exactly with all leftover pieces", metavar="<string>", type=str, default='')
percent_parser.add_argument("-pc", "--pc-num", help="pc number for setup", metavar="<int>", type=int)
percent_parser.add_argument("-ll", "--leftover-length", help="length of leftover alternative to -pc", metavar="<int>", type=int)
percent_parser.add_argument("-he", "--height", help="height of pc (default: 4)", metavar="<int>", type=int, default=DEFAULT_HEIGHT)
percent_parser.add_argument("-wi", "--width", help="width of pc (default: 10)", metavar="<int>", type=int, default=DEFAULT_WIDTH)
percent_parser.add_argument("-ho", "--hold", help="number of hold (default: 1)", metavar="<int>", type=int, default=DEFAULT_HOLD)
percent_parser.add_argument("-td", "--tree-depth", help="set the tree depth of pieces in percent (default: 0)", metavar="<int>", type=int, default=0)
percent_parser.add_argument("-f", "--path-file", help="path filepath (default: output/path.csv)", metavar="<filepath>", default=DEFAULT_PATH_FILE, type=str)
percent_parser.add_argument("-lp", "--log-path", help="output filepath (default: output/last_output.txt)", metavar="<filepath>", default=DEFAULT_LAST_OUTPUT_FILE, type=str)
percent_parser.add_argument("-sp", "--saves-path", help="path to json file with preset wanted saves (default: GITROOT/saves.json)", metavar="<filepath>", default=DEFAULT_SAVES_JSON, type=str)
percent_parser.add_argument("-np", "--no-print", help="don't log to terminal", action="store_true")
percent_parser.add_argument("-fa", "--fails", help="include the fail queues for saves in output (default: False)", action="store_true")
percent_parser.add_argument("-os", "--over-solves", help="have the percents be out of when setup is solvable (default: False)", action="store_true")

filter_parser = arg_subparsers.add_parser("filter", help="filter path.csv of fumens that doesn't meet the wanted saves")
filter_parser.set_defaults(func=parse_filter_args)
filter_parser.add_argument("-w", "--wanted-saves", help="the save expression (required if there isn't -k)", metavar="<string>", nargs='+')
filter_parser.add_argument("-k", "--key", help="use preset wanted saves in the saves json (required if there isn't a -w nor -a)", metavar="<string>", nargs='+')
filter_parser.add_argument("-i", "--index", help="index of -k or -w to pick which expression to filter by (default=0)", metavar="<int>", type=int, default=0)
filter_parser.add_argument("-b", "--build", help="pieces in the build of the setup. Ignored if -l has '-' in expression", metavar="<string>", type=str)
filter_parser.add_argument("-l", "--leftover", help="leftover pieces for this pc. Supports T-IO for still have T from leftover and used IO from following bag. Not specified implies building setup exactly with all leftover pieces", metavar="<string>", type=str, default='')
filter_parser.add_argument("-pc", "--pc-num", help="pc number for setup", metavar="<int>", type=int)
filter_parser.add_argument("-ll", "--leftover-length", help="length of leftover alternative to -pc", metavar="<int>", type=int)
filter_parser.add_argument("-he", "--height", help="height of pc (default: 4)", metavar="<int>", type=int, default=DEFAULT_HEIGHT)
filter_parser.add_argument("-wi", "--width", help="width of pc (default: 10)", metavar="<int>", type=int, default=DEFAULT_WIDTH)
filter_parser.add_argument("-ho", "--hold", help="number of hold (default: 1)", metavar="<int>", type=int, default=DEFAULT_HOLD)
filter_parser.add_argument("-bs", "--best-save", help="instead of listing each wanted save separately, it prioritizes the first then second and so on (default: False)", action="store_true")
filter_parser.add_argument("-c", "--cumulative", help="gives percents cumulatively in fumens of a minimal set (default: False)", action="store_true")
filter_parser.add_argument("-f", "--path-file", help="path filepath (default: output/path.csv)", metavar="<filepath>", default=DEFAULT_PATH_FILE, type=str)
filter_parser.add_argument("-lp", "--log-path", help="output filepath (default: output/last_output.txt)", metavar="<filepath>", default=DEFAULT_LAST_OUTPUT_FILE, type=str)
filter_parser.add_argument("-sp", "--saves-path", help="path to json file with preset wanted saves (default: GITROOT/saves.json)", metavar="<filepath>", default=DEFAULT_SAVES_JSON, type=str)
filter_parser.add_argument("-fp", "--filtered-path", help="output filtered path file with solve of \"file\" (default: output/filtered_path.txt)", metavar="<filepath>", default=DEFAULT_FILTERED_PATH_FILE, type=str)
filter_parser.add_argument("-np", "--no-print", help="don't log to terminal", action="store_true")
filter_parser.add_argument("-s", "--solve", help="setting for how to output solve (minimal, unique, file) (default: minimal)", choices={"minimal", "unique", "file"}, metavar="<string>", default="minimal", type=str)
filter_parser.add_argument("-t", "--tinyurl", help="output the link with tinyurl if possible", action="store_true")

