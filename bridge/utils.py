from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Any, Dict
import yaml


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_path(path_str: str, base: Path | None = None) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    return (base or project_root()).joinpath(p).resolve()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_config(config_path: str) -> Dict[str, Any]:
    path = resolve_path(config_path)
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def now_ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def append_log(log_file: Path, message: str) -> None:
    ensure_dir(log_file.parent)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(f"[{now_ts()}] {message}\n")
