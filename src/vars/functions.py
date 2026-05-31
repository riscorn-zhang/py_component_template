from pathlib import Path
from src.vars.runtimes import APP_CURRENT_DIR


def generate_anoymous_pkg_name():
    import uuid

    return f"_anon_pkg_{uuid.uuid4().hex}"


def absolute_path(p: str) -> str:
    return str(Path(APP_CURRENT_DIR) / p)
