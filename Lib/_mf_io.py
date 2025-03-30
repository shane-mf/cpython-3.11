import os
import stat
import errno
from _pyio_base import RawIOBase, DEFAULT_BUFFER_SIZE, UnsupportedOperation
from mf_customs import logger
from io_c import (__all__, SEEK_SET, SEEK_CUR, SEEK_END)

class _FileInfo:
    path: str
    fd: int
    inheritable: bool
    st_mode: int
    st_size: int
    pos: int
    st_data: bytes

    def __init__(self, path: str, fd: int, inheritable: bool, st_mode: int):
        self.path = path
        self.fd = fd
        self.inheritable = inheritable
        self.st_mode = st_mode
        self.pos = 0
        self.st_data = b'hello,mf:virtual-fs.abcdefghijklmnopqrstuvwxyzhahaen.'
        self.st_size = len(self.st_data)

_cur_fd = 0
_path_to_fd_map: dict[str, int] = {}
_fd_to_file_info_map: dict[int, _FileInfo] = {}

def mf_opener(path: str, flags: int, mode: int):
    # raise OSError(12347, f"mf_opener: {path}")
    global _cur_fd
    if path not in _path_to_fd_map:
        _cur_fd += 1
        _path_to_fd_map[path] = _cur_fd
        _fd_to_file_info_map[_cur_fd] = _FileInfo(path, _cur_fd, True, stat.S_IFREG)
    else:
        _cur_fd = _path_to_fd_map[path]

    logger.debug(f"mf_opener: {path}, {flags}: {_cur_fd}")
    return _cur_fd

def mf_close(fd: int):
    del _fd_to_file_info_map[fd]

def mf_set_inheritable(fd: int, inheritable: bool):
    logger.debug(f"TODO: set_inheritable: {fd}, {inheritable}")

def mf_fstat(fd: int):
    logger.debug(f"TODO: fstat: {fd}")
    # if fd == 0:
    #     # 程序启动时，会lsstat fd:0 ?
    #     return os.stat(fd)
    # raise OSError(errno.EBADF, f"mf_opener: {_cur_fd} {_fd_to_file_info_map}")
    return _fd_to_file_info_map[fd]

def mf_lseek(fd: int, pos: int, whence: int) -> int:
    file_info = _fd_to_file_info_map[fd]
    if whence == SEEK_SET:
        file_info.pos = pos
    elif whence == SEEK_CUR:
        file_info.pos += pos
    elif whence == SEEK_END:
        file_info.pos = file_info.st_size + pos
    return file_info.pos

def mf_read(fd: int, size: int):
    file_info = _fd_to_file_info_map[fd]
    if file_info.pos + size > file_info.st_size:
        size = file_info.st_size - file_info.pos
    data = file_info.st_data[file_info.pos:file_info.pos + size]
    file_info.pos += size
    return data

def mf_write(fd: int, data: bytes):
    file_info = _fd_to_file_info_map[fd]
    file_info.st_data += data
    file_info.st_size = len(file_info.st_data)
    return len(data)

def mf_ftruncate(fd: int, size: int):
    file_info = _fd_to_file_info_map[fd]
    file_info.st_data = file_info.st_data[:size]
    file_info.st_size = size

class FileIO(RawIOBase):
    _fd = -1
    _created = False
    _readable = False
    _writable = False
    _appending = False
    _seekable = None
    _closefd = True

    def __init__(self, file, mode='r', closefd=True, opener=None):
        if opener is not None:
            import warnings
            warnings.warn('custom opener is not supported', ResourceWarning,
                          stacklevel=2, source=self)

        if self._fd >= 0:
            try:
                if self._closefd:
                    mf_close(self._fd)
            finally:
                self._fd = -1
            self._fd = -1

        if isinstance(file, float):
            raise TypeError('integer argument expected, got float')
        if isinstance(file, int):
            fd = file
            if fd < 0:
                raise ValueError('negative file descriptor')
        else:
            fd = -1

        if not isinstance(mode, str):
            raise TypeError('invalid mode: %s' % (mode,))
        if not set(mode) <= set('xrwab+'):
            raise ValueError('invalid mode: %s' % (mode,))
        if sum(c in 'rwax' for c in mode) != 1 or mode.count('+') > 1:
            raise ValueError('Must have exactly one of create/read/write/append '
                             'mode and at most one plus')

        if 'x' in mode:
            self._created = True
            self._writable = True
            flags = os.O_EXCL | os.O_CREAT
        elif 'r' in mode:
            self._readable = True
            flags = 0
        elif 'w' in mode:
            self._writable = True
            flags = os.O_CREAT | os.O_TRUNC
        elif 'a' in mode:
            self._writable = True
            self._appending = True
            flags = os.O_APPEND | os.O_CREAT

        if '+' in mode:
            self._readable = True
            self._writable = True

        if self._readable and self._writable:
            flags |= os.O_RDWR
        elif self._readable:
            flags |= os.O_RDONLY
        else:
            flags |= os.O_WRONLY

        flags |= getattr(os, 'O_BINARY', 0)

        noinherit_flag = (getattr(os, 'O_NOINHERIT', 0) or
                          getattr(os, 'O_CLOEXEC', 0))
        flags |= noinherit_flag

        owned_fd = None
        # raise OSError(errno.EBADF, f"FileIO.__init__:{file}")
        try:
            if fd < 0:
                if not closefd:
                    raise ValueError('Cannot use closefd=False with file name')
                fd = mf_opener(file, flags, 0o666)
                owned_fd = fd
                if not noinherit_flag:
                    mf_set_inheritable(fd, False)

            self._closefd = closefd
            fdfstat = mf_fstat(fd)
            try:
                if stat.S_ISDIR(fdfstat.st_mode):
                    raise IsADirectoryError(errno.EISDIR,
                                            os.strerror(errno.EISDIR), file)
            except AttributeError:
                # Ignore the AttributeError if stat.S_ISDIR or errno.EISDIR
                # don't exist.
                pass
            # self._blksize = getattr(fdfstat, 'st_blksize', 0)
            # if self._blksize <= 1:
            #     self._blksize = DEFAULT_BUFFER_SIZE
            self._blksize = DEFAULT_BUFFER_SIZE

            # by @mf: ignore (this is for win32, cygwin)
            # if _setmode:
            #     # don't translate newlines (\r\n <=> \n)
            #     _setmode(fd, os.O_BINARY)

            self.name = file
            if self._appending:
                # For consistent behaviour, we explicitly seek to the
                # end of file (otherwise, it might be done only on the
                # first write()).
                try:
                    mf_lseek(fd, 0, SEEK_END)
                except OSError as e:
                    if e.errno != errno.ESPIPE:
                        raise
        except:
            if owned_fd is not None:
                mf_close(owned_fd)
            raise
        self._fd = fd
        # raise OSError(errno.EBADF, f"FileIO.__init__:{file}")

    def __del__(self):
        if self._fd >= 0 and self._closefd and not self.closed:
            import warnings
            warnings.warn('unclosed file %r' % (self,), ResourceWarning,
                          stacklevel=2, source=self)
            self.close()

    def __getstate__(self):
        raise TypeError(f"cannot pickle {self.__class__.__name__!r} object")

    def __repr__(self):
        class_name = '%s.%s' % (self.__class__.__module__,
                                self.__class__.__qualname__)
        if self.closed:
            return '<%s [closed]>' % class_name
        try:
            name = self.name
        except AttributeError:
            return ('<%s fd=%d mode=%r closefd=%r>' %
                    (class_name, self._fd, self.mode, self._closefd))
        else:
            return ('<%s name=%r mode=%r closefd=%r>' %
                    (class_name, name, self.mode, self._closefd))

    def _checkReadable(self):
        if not self._readable:
            raise UnsupportedOperation('File not open for reading')

    def _checkWritable(self, msg=None):
        if not self._writable:
            raise UnsupportedOperation('File not open for writing')

    def read(self, size=None):
        self._checkClosed()
        self._checkReadable()
        if size is None or size < 0:
            return self.readall()
        try:
            return mf_read(self._fd, size)
        except BlockingIOError:
            return None

    def readall(self):
        self._checkClosed()
        self._checkReadable()
        bufsize = DEFAULT_BUFFER_SIZE
        try:
            pos = mf_lseek(self._fd, 0, SEEK_CUR)
            end = mf_fstat(self._fd).st_size
            if end >= pos:
                bufsize = end - pos + 1
        except OSError:
            pass

        result = bytearray()
        while True:
            if len(result) >= bufsize:
                bufsize = len(result)
                bufsize += max(bufsize, DEFAULT_BUFFER_SIZE)
            n = bufsize - len(result)
            try:
                chunk = mf_read(self._fd, n)
            except BlockingIOError:
                if result:
                    break
                return None
            if not chunk: # reached the end of the file
                break
            result += chunk

        return bytes(result)

    def readinto(self, b):
        m = memoryview(b).cast('B')
        data = self.read(len(m))
        n = len(data)
        m[:n] = data
        return n

    def write(self, b):
        self._checkClosed()
        self._checkWritable()
        try:
            return mf_write(self._fd, b)
        except BlockingIOError:
            return None

    def seek(self, pos, whence=SEEK_SET):
        if isinstance(pos, float):
            raise TypeError('an integer is required')
        self._checkClosed()
        return mf_lseek(self._fd, pos, whence)

    def tell(self):
        self._checkClosed()
        return mf_lseek(self._fd, 0, SEEK_CUR)

    def truncate(self, size=None):
        self._checkClosed()
        self._checkWritable()
        if size is None:
            size = self.tell()
        mf_ftruncate(self._fd, size)
        return size

    def close(self):
        if not self.closed:
            try:
                if self._closefd:
                    mf_close(self._fd)
            finally:
                super().close()

    def seekable(self):
        self._checkClosed()
        return True

    def readable(self):
        self._checkClosed()
        return self._readable

    def writable(self):
        self._checkClosed()
        return self._writable

    def fileno(self):
        self._checkClosed()
        return self._fd

    def isatty(self):
        self._checkClosed()
        return False  # todo: implement

    @property
    def closefd(self):
        return self._closefd

    @property
    def mode(self):
        if self._created:
            if self._readable:
                return 'xb+'
            else:
                return 'xb'
        elif self._appending:
            if self._readable:
                return 'ab+'
            else:
                return 'ab'
        elif self._readable:
            if self._writable:
                return 'rb+'
            else:
                return 'rb'
        else:
            return 'wb'
