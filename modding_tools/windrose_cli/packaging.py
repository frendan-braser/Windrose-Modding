from __future__ import annotations

import zipfile
from pathlib import Path


def package_pak_variant(pak_path: Path, zip_path: Path | None = None) -> Path:
    if not pak_path.exists():
        raise FileNotFoundError(f"Pak not found: {pak_path}")
    target = zip_path or pak_path.with_suffix(".zip")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(pak_path, pak_path.name)
    return target

