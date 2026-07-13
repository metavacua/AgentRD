import sys
from pathlib import Path
# make the shared _paths helper importable from every test under skills/*/tests/
sys.path.insert(0, str(Path(__file__).resolve().parent))
