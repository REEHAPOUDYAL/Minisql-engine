from pathlib import Path
from typing import Literal

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
TABLES_DIR = DATA_DIR / "tables"
TABLES_DIR.mkdir(exist_ok=True)

INDEX_DIR = DATA_DIR / "indices"
INDEX_DIR.mkdir(exist_ok=True)
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

DEFAULT_ENCODING = "utf-8"
MAX_RECORD_SIZE = 4096
BUFFER_SIZE = 8192

FileMode = Literal["r", "w", "a", "rb", "wb", "ab"]
DEFAULT_FILE_MODE: FileMode = "rb"
SUPPORTED_DATA_TYPES = ["INT", "FLOAT", "STRING", "BOOL"]
AUTO_COMMIT = True
DEBUG_MODE = False
