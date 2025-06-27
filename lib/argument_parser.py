import argparse
from .constants import DEFAULT_SAVES_JSON, DEFAULT_PATH_FILE, DEFAULT_LAST_OUTPUT_FILE, DEFAULT_FILTERED_PATH_FILE
from .percent import percent
from .utils import is_queue

def parse_percent_args(args):
  '''
  Parse the arguments for percent subcommand to pass to run calculation of save percent
  '''

  wanted_saves = args.wanted_saves

  # out of bounds pc number
  if args.pc_num < 1 or 9 < args.pc_num:
    print("PC Number expected to be within 1-9")
    exit(0)

  # build uses only pieces in TILJSZO
  if not is_queue(args.build_queue):
    print("Build Queue expected to contain only TILJSZO pieces")
    exit(0)

  log_file = open(args.log_path, 'w')

  if args.best_save:
    percent(args.path_file, wanted_saves, args.build_queue, args.pc_num, log_file, args.two_line, args.console_print, args.fails, args.over_solves)
  else:
    for wanted_save in wanted_saves:
      percent(args.path_file, [wanted_save], args.build_queue, args.pc_num, log_file, args.two_line, args.console_print, args.fails, args.over_solves)

  log_file.close()

arg_parser = argparse.ArgumentParser(usage="<cmd> [options]", description="A tool for further expansion of the saves from path.csv")
arg_subparsers = arg_parser.add_subparsers()

percent_parser = arg_subparsers.add_parser("percent", help="Give the percents of saves using the path.csv file with wanted save expression")
percent_parser.set_defaults(func=parse_percent_args)
percent_parser.add_argument("-w", "--wanted-saves", help="the save expression (required if there isn't -k)", metavar="<string>", nargs='+')
# percent_parser.add_argument("-k", "--key", help="use wantedPiecesMap.json for preset wanted saves (required if there isn't a -w)", metavar="<string>", nargs='+')
# percent_parser.add_argument("-a", "--all", help="output all of the saves and corresponding percents (alternative to not having -k nor -w)", action="store_true")
percent_parser.add_argument("-bs", "--best-save", help="instead of listing each wanted save separately, it prioritizes the first then second and so on (requires a -w or -k default: false)", action="store_true")
percent_parser.add_argument("-q", "--build-queue", help="queue of pieces in build order following bags for pc", metavar="<string>", type=str, required=True)
percent_parser.add_argument("-pc", "--pc-num", help="pc number for the setup", metavar="<int>", type=int, required=True)
percent_parser.add_argument("-tl", "--two-line", help="setup is two lines (default: False)", action="store_true")
# percent_parser.add_argument("-td", "--tree-depth", help="set the tree depth of pieces in percent (default: 0)", metavar="<int>", type=int, default=0)
percent_parser.add_argument("-f", "--path-file", help="path file directory (default: output/path.csv)", metavar="<directory>", default=DEFAULT_PATH_FILE, type=str)
percent_parser.add_argument("-lp", "--log-path", help="output file directory (default: output/last_output.txt)", metavar="<directory>", default=DEFAULT_LAST_OUTPUT_FILE, type=str)
percent_parser.add_argument("-pr", "--console-print", help="log to terminal (default: True)", action="store_false")
percent_parser.add_argument("-fa", "--fails", help="include the fail queues for saves in output (default: False)", action="store_true")
percent_parser.add_argument("-os", "--over-solves", help="have the percents be out of when setup is solvable (default: False)", action="store_true")

filter_parser = arg_subparsers.add_parser("filter", help="filter path.csv of fumens that doesn't meet the wanted saves")
filter_parser.add_argument("-w", "--wanted-saves", help="the save expression (required if there isn't -k)", metavar="<string>", nargs='+')
filter_parser.add_argument("-k", "--key", help="use wantedPiecesMap.json for preset wanted saves (required if there isn't a -w)", metavar="<string>", nargs='+')
filter_parser.add_argument("-bs", "--best-save", help="instead of listing each wanted save separately, it prioritizes the first then second and so on (requires a -w or -k default: false)", action="store_true")
# filter_parser.add_argument("-i", "--index", help="index of -k or -w to pick which expression to filter by (default='')", default=None, metavar="<string>", nargs='*')
filter_parser.add_argument("-q", "--build-queue", help="queue of pieces in build order following bags for pc", metavar="<string>", type=str, required=True)
filter_parser.add_argument("-pc", "--pc-num", help="pc number for the setup", metavar="<int>", type=int, required=True)
filter_parser.add_argument("-tl", "--two-line", help="setup is two lines (default: False)", action="store_true")
filter_parser.add_argument("-c", "--cumulative", help="gives percents cumulatively in fumens of a minimal set (default: False)", action="store_true")
filter_parser.add_argument("-f", "--path-file", help="path file directory (default: output/path.csv)", metavar="<directory>", default=DEFAULT_PATH_FILE, type=str)
filter_parser.add_argument("-lp", "--log-path", help="output file directory (default: output/last_output.txt)", metavar="<directory>", default=DEFAULT_LAST_OUTPUT_FILE, type=str)
filter_parser.add_argument("-fp", "--filtered-path", help="output file directory (default: output/last_output.txt)", metavar="<directory>", default=DEFAULT_LAST_OUTPUT_FILE, type=str)
filter_parser.add_argument("-pr", "--console-print", help="log to terminal (default: True)", action="store_false")
filter_parser.add_argument("-s", "--solve", help="setting for how to output solve (minimal, unique, none)(default: minimal)", choices={"minimal", "unique", "none"}, metavar="<string>", default="minimal", type=str)
filter_parser.add_argument("-t", "--tinyurl", help="output the link with tinyurl if possible (default: True)", action="store_false")
filter_parser.add_argument("-fc", "--fumen-code", help="include the fumen code in the output (default: False)", action="store_true")


