import os
from pathlib import Path

def project_absolute_path() -> Path:
    return Path(__file__).resolve().parents[0]

def absolute_path(dir: str) -> str:
    return os.path.join(project_absolute_path(), dir)
