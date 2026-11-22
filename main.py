#!/usr/bin/env python3
"""news-image-20261122 entrypoint (Python stdlib only).

The entry image is rendered by build_image.py (Pillow, run at build time) and
ships in this repository as entry.png. This program only validates the bounty
limits and copies the PNG byte-for-byte to the output directory, so the run is
fully deterministic: two runs produce identical bytes.

Bounty limits: PNG file, size <= 1 MiB, dimensions <= 1024 x 1024.
"""
import os
import shutil
import struct

MAX_BYTES = 1024 * 1024
MAX_DIM = 1024


def png_dimensions(path):
    with open(path, "rb") as f:
        header = f.read(33)
    if len(header) < 33 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("entry.png is not a PNG file")
    # First chunk must be IHDR: length (4) + type (4) + width (4) + height (4).
    length, ctype = struct.unpack(">I4s", header[8:16])
    if ctype != b"IHDR" or length != 13:
        raise ValueError("entry.png has no IHDR chunk first")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        raise FileNotFoundError("entry.png missing next to main.py")
    size = os.path.getsize(src)
    if size > MAX_BYTES:
        raise ValueError("entry.png is %d bytes, over the 1 MiB limit" % size)
    width, height = png_dimensions(src)
    if width > MAX_DIM or height > MAX_DIM:
        raise ValueError("entry.png is %dx%d, over the 1024x1024 limit"
                         % (width, height))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, out_path)


if __name__ == "__main__":
    main()
