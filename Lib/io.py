# this file is changed by @shane:
# Use the pure Python implementation instead of the C implementation
# the original io.py moved to io_c.py

__all__ = ["BlockingIOError", "open", "open_code", "IOBase", "RawIOBase",
           "FileIO", "BytesIO", "StringIO", "BufferedIOBase",
           "BufferedReader", "BufferedWriter", "BufferedRWPair",
           "BufferedRandom", "TextIOBase", "TextIOWrapper",
           "UnsupportedOperation", "SEEK_SET", "SEEK_CUR", "SEEK_END",
           "DEFAULT_BUFFER_SIZE", "text_encoding", "IncrementalNewlineDecoder"]

import abc
import _pyio as _io
from _pyio import (DEFAULT_BUFFER_SIZE, BlockingIOError, UnsupportedOperation,
                   open, open_code, FileIO, BytesIO, StringIO, BufferedReader,
                   BufferedWriter, BufferedRWPair, BufferedRandom,
                   IncrementalNewlineDecoder, text_encoding, TextIOWrapper)

def __getattr__(name):
    if name == "OpenWrapper":
        # bpo-43680: Until Python 3.9, _pyio.open was not a static method and
        # builtins.open was set to OpenWrapper to not become a bound method
        # when set to a class variable. _io.open is a built-in function whereas
        # _pyio.open is a Python function. In Python 3.10, _pyio.open() is now
        # a static method, and builtins.open() is now io.open().
        import warnings
        warnings.warn('OpenWrapper is deprecated, use open instead',
                      DeprecationWarning, stacklevel=2)
        global OpenWrapper
        OpenWrapper = open
        return OpenWrapper
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Pretend this exception was created here.
UnsupportedOperation.__module__ = "io"

# for seek()
SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

# Declaring ABCs in C is tricky so we do it here.
# Method descriptions and default implementations are inherited from the C
# version however.
class IOBase(_io.IOBase, metaclass=abc.ABCMeta):
    __doc__ = _io.IOBase.__doc__

class RawIOBase(_io.RawIOBase, IOBase):
    __doc__ = _io.RawIOBase.__doc__

class BufferedIOBase(_io.BufferedIOBase, IOBase):
    __doc__ = _io.BufferedIOBase.__doc__

class TextIOBase(_io.TextIOBase, IOBase):
    __doc__ = _io.TextIOBase.__doc__

RawIOBase.register(FileIO)

for klass in (BytesIO, BufferedReader, BufferedWriter, BufferedRandom,
              BufferedRWPair):
    BufferedIOBase.register(klass)

for klass in (StringIO, TextIOWrapper):
    TextIOBase.register(klass)
del klass

# _WindowsConsoleIO is only in the C implementation, not in _pyio
# So we don't try to import it when using _pyio
"""
try:
    from _io import _WindowsConsoleIO
except ImportError:
    pass
else:
    RawIOBase.register(_WindowsConsoleIO)
"""
