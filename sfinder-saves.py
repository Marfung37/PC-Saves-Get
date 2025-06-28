from lib.argument_parser import arg_parser
import sys

if __name__ == "__main__":
  args = arg_parser.parse_args(sys.argv[1:])
  if vars(args):
    args.func(args)
  else:
    arg_parser.print_help()
