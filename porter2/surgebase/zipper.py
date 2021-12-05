"""
The so file generated from porter2.go is over 2.4 MB.
This makes it worth the extra step of bzipping it
which reduces it's size to about 0.8MB
"""

import bz2
from importlib import resources
from pathlib import Path

from porter2 import surgebase

with resources.as_file(resources.files(surgebase)) as f:
    SO_PATH = f / Path("_porter2.so")
BZ_SO_PATH = SO_PATH.with_suffix(".bz")


def bzip_so() -> None:
    with open(SO_PATH, "rb") as so_fh:
        so_bin = so_fh.read()

    bz = bz2.compress(so_bin, compresslevel=9)
    with open(BZ_SO_PATH, "wb") as bz_fh:
        bz_fh.write(bz)


def get_so() -> Path:
    if not SO_PATH.is_file():
        with open(BZ_SO_PATH, "rb") as bz_fh:
            bz = bz_fh.read()
        with open((SO_PATH), "wb") as so_fh:
            so_fh.write(bz2.decompress(bz))
    return SO_PATH


if __name__ == "__main__":

    bzip_so()
