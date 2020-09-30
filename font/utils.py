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


def decode_triplet_encoding(index):
    data = [None] * 7
    sequence1 = sorted([0, 256, 512, 768, 1024] * 2)
    sequence2 = sorted([1, 17, 33, 49] * 4)
    sequence3 = sorted([1, 257, 513] * 4)
    if index in range(10):
        data[0] = 2
        data[1] = 0
        data[2] = 8
        data[4] = sequence1[index]

    elif index in range(20):
        data[0] = 2
        data[1] = 8
        data[2] = 0
        data[3] = sequence1[index - 10]

    elif index in range(36):
        data[0] = 2
        data[1] = data[2] = 4
        data[3] = 1
        data[4] = sequence2[index - 20]

    elif index in range(52):
        data[0] = 2
        data[1] = data[2] = 4
        data[3] = 17
        data[4] = sequence2[index - 36]

    elif index in range(68):
        data[0] = 2
        data[1] = data[2] = 4
        data[3] = 33
        data[4] = sequence2[index - 52]

    elif index in range(84):
        data[0] = 2
        data[1] = data[2] = 4
        data[3] = 49
        data[4] = sequence2[index - 68]

    elif index in range(96):
        data[0] = 3
        data[1] = data[2] = 8
        data[3] = 1
        data[4] = sequence3[index - 84]

    elif index in range(108):
        data[0] = 3
        data[1] = data[2] = 8
        data[3] = 257
        data[4] = sequence3[index - 96]

    elif index in range(120):
        data[0] = 3
        data[1] = data[2] = 8
        data[3] = 513
        data[4] = sequence3[index - 108]

    elif index in range(124):
        data[0] = 4
        data[1] = data[2] = 12
        data[3] = data[4] = 0

    elif index in range(128):
        data[0] = 5
        data[1] = data[2] = 16
        data[3] = data[4] = 0

    if index in range(10):
        data[6] = "-+"[index % 2]

    else:
        data[5] = "-+"[index % 2]
        if index > 20:
            data[6] = "--++"[index % 4]

    return data


known_table_lookup = [
    "cmap",
    "head",
    "hhea",
    "hmtx",
    "maxp",
    "name",
    "OS/2",
    "post",
    "cvt ",
    "fpgm",
    "glyf",
    "loca",
    "prep",
    "CFF ",
    "VORG",
    "EBDT",
    "EBLC",
    "gasp",
    "hdmx",
    "kern",
    "LTSH",
    "PCLT",
    "VDMX",
    "vhea",
    "vmtx",
    "BASE",
    "GDEF",
    "GPOS",
    "GSUB",
    "EBSC",
    "JSTF",
    "MATH",
    "CBDT",
    "CBLC",
    "COLR",
    "CPAL",
    "SVG ",
    "sbix",
    "acnt",
    "avar",
    "bdat",
    "bloc",
    "bsln",
    "cvar",
    "fdsc",
    "feat",
    "fmtx",
    "fvar",
    "gvar",
    "hsty",
    "just",
    "lcar",
    "mort",
    "morx",
    "opbd",
    "prop",
    "trak",
    "Zapf",
    "Silf",
    "Glat",
    "Gloc",
    "Feat",
    "Sill",
    "arbitrary",
]
