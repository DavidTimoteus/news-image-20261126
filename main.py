"""Entrypoint for the news-image-20261126 bounty entry.

Copies the pre-rendered one-page front page (entry.png, drawn by
render_image.py with Pillow) to /output/entry.png. The image itself is
committed in this repository, so the program needs no network and no
third-party packages: standard library only.

The copy is done in 64 KiB blocks so the program works the same on
any platform, and the destination directory is created if missing.
"""

import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_SOURCE = os.path.join(_HERE, "entry.png")
_TARGET = "/output/entry.png"
_BLOCK = 64 * 1024


def main():
    os.makedirs(os.path.dirname(_TARGET), exist_ok=True)
    with open(_SOURCE, "rb") as src, open(_TARGET, "wb") as dst:
        while True:
            block = src.read(_BLOCK)
            if not block:
                break
            dst.write(block)


if __name__ == "__main__":
    main()
