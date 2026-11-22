#!/usr/bin/env python3
"""Generate the photo gallery index for a Pages deployment."""

import json
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[2]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}


def build_gallery(root):
    gallery = root / "photo-gallery"
    albums = []
    if not gallery.is_dir():
        raise FileNotFoundError(f"Gallery directory not found: {gallery}")

    for folder in sorted(gallery.iterdir(), key=lambda path: path.name.casefold()):
        if not folder.is_dir() or folder.name.startswith(".") or folder.is_symlink():
            continue
        photos = [
            "/" + quote(path.relative_to(root).as_posix(), safe="/")
            for path in sorted(folder.iterdir(), key=lambda path: path.name.casefold())
            if path.is_file() and not path.is_symlink()
            and path.suffix.lower() in IMAGE_EXTENSIONS and not path.name.startswith(".")
        ]
        albums.append({
            "id": folder.name,
            "title": folder.name.replace("-", " ").replace("_", " "),
            "photos": photos,
        })

    output = root / "assets" / "gallery.json"
    output.write_text(json.dumps(albums, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build_gallery(ROOT)
