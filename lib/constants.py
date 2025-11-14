from os import path

BAG = 'TILJSZO'

HOLD = 1

DIRNAME = path.dirname(path.dirname(__file__))
DEFAULT_SAVES_JSON = path.join(DIRNAME, "saves.json")
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_PATH_FILE = path.join(DEFAULT_OUTPUT_DIR, "path.csv")
DEFAULT_LAST_OUTPUT_FILE = path.join(DEFAULT_OUTPUT_DIR, "last_output.txt")
DEFAULT_FILTERED_PATH_FILE = path.join(DEFAULT_OUTPUT_DIR, "filtered_path.csv")

WANTED_SAVE_COMMENT_DELIMITOR = '#'
WANTED_SAVE_DELIMITOR = ','
