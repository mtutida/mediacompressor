from pathlib import Path

APP_NAME = "MediaCompressorPro"
APP_PHASE = "17.1"

# single source of truth
_counter_path = Path(__file__).resolve().parent.parent / ".build_counter"

try:
    BUILD_COUNTER = _counter_path.read_text().strip()
except Exception:
    BUILD_COUNTER = "0"

APP_VERSION = BUILD_COUNTER
BUILD_ID = f"BUILD_{BUILD_COUNTER}"
