# this file is changed by @shane:
# Use the pure Python implementation instead of the C implementation
# the original io.py moved to io_c.py

__all__ = ["BlockingIOError", "open", "open_code", "IOBase", "RawIOBase",
           "FileIO", "BytesIO", "StringIO", "BufferedIOBase",
           "BufferedReader", "BufferedWriter", "BufferedRWPair",
           "BufferedRandom", "TextIOBase", "TextIOWrapper",
           "UnsupportedOperation", "SEEK_SET", "SEEK_CUR", "SEEK_END",
           "DEFAULT_BUFFER_SIZE", "text_encoding", "IncrementalNewlineDecoder"]

from _pyio import (DEFAULT_BUFFER_SIZE, BlockingIOError, UnsupportedOperation,
                   open, open_code, FileIO, BytesIO, StringIO, BufferedReader,
                   BufferedWriter, BufferedRWPair, BufferedRandom,
                   IncrementalNewlineDecoder, text_encoding, TextIOWrapper,
                   IOBase, RawIOBase, BufferedIOBase, TextIOBase, SEEK_SET, SEEK_CUR, SEEK_END
                   )


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
