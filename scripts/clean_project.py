from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]

REMOVE_DIRS = {
    '__pycache__',
    'venv',
    '.venv',
    'env',
    'ENV',
    '.idea',
    '.vscode',
    '.pytest_cache',
}

REMOVE_FILES = {
    'db.sqlite3',
    '.DS_Store',
    'Thumbs.db',
}

REMOVE_SUFFIXES = {
    '.pyc',
    '.pyo',
    '.log',
}

removed = []

for path in sorted(ROOT.rglob('*'), reverse=True):
    if path.name in REMOVE_DIRS and path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
        removed.append(str(path.relative_to(ROOT)))
        continue

    if path.is_file() and (path.name in REMOVE_FILES or path.suffix in REMOVE_SUFFIXES):
        path.unlink(missing_ok=True)
        removed.append(str(path.relative_to(ROOT)))

print('Cleaned project')
print(f'Removed items: {len(removed)}')
for item in removed[:200]:
    print('-', item)

if len(removed) > 200:
    print(f'... and {len(removed) - 200} more')
