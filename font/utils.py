from . import otf
import struct


def calc_checksum(data, tag=None):
    """Calculate the checksum """
    while len(data) % 4:
        data += b"\0"

    if tag == "head":
        assert len(data) > 12
        data = data[:8] + b"\0" * 4 + data[12:]

    return sum(struct.unpack(">{}I".format(len(data) // 4), data)) % 2 ** 32


def calc_checksum_adjustment(file):
    """Calculate checksum adjustment for a font file."""
    if not isinstance(file, otf.File):
        file = file.to_otf()

    return (0xB1B0AFBA - calc_checksum(file.to_bytes())) % 2 ** 32


def calc_search_range(num_tables):
    """Calculate the search range, entry selector and range shift for an OTF file."""
    exp = 0
    tmp = num_tables
    while tmp:
        tmp >>= 1
        exp += 1

    entry_selector = max(exp - 1, 0)
    search_range = 16 * 2 ** entry_selector
    range_shift = 16 * num_tables - search_range
    return search_range, entry_selector, range_shift


def check_range_overlap(ranges):
    """Check that no ranges cross into other ranges."""
    return len(set(ranges[0]).intersection(*ranges)) > 0


def str2tag(str):
    """Convert a string to an unsigned 32-bit integer."""
    return (ord(str[0]) << 24) + (ord(str[1]) << 16) + (ord(str[2]) << 8) + ord(str[3])


def tag2str(tag):
    """Convert an unsigned 32-bit integer to a string."""
    return (
        chr(tag >> 24) + chr((tag >> 16) & 255) + chr((tag >> 8) & 255) + chr(tag & 255)
    )
