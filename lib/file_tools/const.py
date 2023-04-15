from enum import IntFlag


class Win32FileAttribute(IntFlag):
    """Microsoft Windows File Attributes

    Reference:
    https://learn.microsoft.com/en-us/windows/win32/fileio/file-attribute-constants

    DEPRECATED: use stat.FILE_ATTRIBUTE_* instead
    https://docs.python.org/3/library/stat.html
    """

    READONLY = 0x1
    HIDDEN = 0x2
    SYSTEM = 0x4
    DIRECTORY = 0x10
    ARCHIVE = 0x20
    DEVICE = 0x40
    NORMAL = 0x80
    TEMPORARY = 0x100
    SPARSE_FILE = 0x200
    REPARSE_POINT = 0x400
    COMPRESSED = 0x800
    OFFLINE = 0x1000
    NOT_CONTENT_INDEXED = 0x2000
    ENCRYPTED = 0x4000
    INTEGRITY_SYSTEM = 0x8000
    VIRTUAL = 0x10000
    NO_SCRUB_DATA = 0x20000
    RECALL_ON_OPEN = 0x40000
    RECALL_ON_DATA_ACCESS = 0x400000
