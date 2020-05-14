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


def vary_lookup(index):
    """Lookup information on vary encoded flags for WOFF2 files."""
    t1 = sorted([0, 256, 512, 768, 1024] * 2)
    t2 = sorted([1, 17, 33, 49] * 4)
    t3 = sorted([1, 257, 513] * 4)
    if index not in range(10):
        x_sign = ["-+"][index % 2]

    if index in range(20, 128):
        y_sign = ["--++"][index % 4]

    if index in range(10):
        byte_count = 2
        x_bits = 0
        y_bits = 8
        dx = x_sign = None
        dy = t1[index]
        y_sign = ["-+"][index % 2]

    elif index in range(20):
        byte_count = 2
        x_bits = 8
        y_bits = 0
        dx = t1[index % 10]
        dy = y_sign = None

    elif index in range(36):
        byte_count = 2
        x_bits = y_bits = 4
        dx = 1
        dy = t2[index - 20]

    elif index in range(52):
        byte_count = 2
        x_bits = y_bits = 4
        dx = 17
        dy = t2[index - 36]

    elif index in range(68):
        byte_count = 2
        x_bits = y_bits = 4
        dx = 33
        dy = t2[index - 52]

    elif index in range(84):
        byte_count = 2
        x_bits = y_bits = 4
        dx = 49
        dy = t2[index - 68]

    elif index in range(96):
        byte_count = 3
        x_bits = y_bits = 8
        dx = 1
        dy = t3[index - 84]

    elif index in range(108):
        byte_count = 3
        x_bits = y_bits = 8
        dx = 257
        dy = t3[index - 84]

    elif index in range(120):
        byte_count = 3
        x_bits = y_bits = 8
        dx = 513
        dy = t3[index - 108]

    elif index in range(124):
        byte_count = 4
        x_bits = y_bits = 12
        dx = dy = 0

    else:
        byte_count = 5
        x_bits = y_bits = 16
        dx = dy = 0

    return x_bits, y_bits, dx, dy, x_sign, y_sign
