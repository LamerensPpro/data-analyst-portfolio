import sys
from utils import load_history, load_daily

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "history"
    if mode == "daily":
        load_daily()
    else:
        load_history()