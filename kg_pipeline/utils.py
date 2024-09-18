from pathlib import Path
import os

def get_proj_root() -> Path:
    return Path(os.path.dirname(__file__))


def get_resource_path(relative_path) -> str:
    base_path = os.path.dirname(__file__)  # The directory where this file exists
    return os.path.join(base_path, relative_path)

