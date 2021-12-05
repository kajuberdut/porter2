import ctypes
from porter2.surgebase.zipper import get_so

SO_PATH = str(get_so())

so = ctypes.cdll.LoadLibrary(SO_PATH)

_stem = so.stem
_stem.argtypes = [ctypes.c_char_p]
_stem.restype = ctypes.c_void_p


def stem(word: str) -> str:
    ptr = _stem(word.encode('utf-8'))
    out = ctypes.string_at(ptr)
    return out.decode('utf-8')
