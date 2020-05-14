from . import tables, woff
from .utils import (
    calc_search_range,
    check_range_overlap,
    str2tag,
    tag2str,
)
import io
import struct

HEADER_SIZE = 12
TABLE_SIZE = 16

header_s = struct.Struct(">I4H")
table_s = struct.Struct(">4I")


class File(object):
    """OpenType Font file."""

    __slots__ = ["sfnt_version", "tables"]

    def __init__(self):
        """Generate an empty OTF file."""
        self.sfnt_version = None
        self.tables = []

    @classmethod
    def from_bytes(cls, bytes):
        """Generate an OTF file from a string of bytes."""
        fp = io.BytesIO(bytes)
        return cls.from_file(fp)

    @classmethod
    def from_file(cls, fp):
        """Generate an OTF file from a file object."""
        obj = cls()
        (
            obj.sfnt_version,
            num_tables,
            search_range,
            entry_selector,
            range_shift,
        ) = header_s.unpack(fp.read(HEADER_SIZE))

        ranges = [range(HEADER_SIZE + num_tables * TABLE_SIZE)]

        for _ in range(num_tables):
            tag, checksum, offset, length = table_s.unpack(fp.read(TABLE_SIZE))

            ranges.append(range(offset, offset + length))

            start = fp.tell()
            fp.seek(offset)
            table = tables.new_table(tag2str(tag), fp.read(length))
            fp.seek(start)

            obj.tables.append(table)
            if checksum != table.checksum:
                raise Exception(
                    "Invalid {} table checksum, expected: {}, received: {}".format(
                        table.tag, table.checksum, checksum
                    )
                )

        obj.tables.sort(key=lambda table: str2tag(table.tag))
        if check_range_overlap(ranges):
            raise Exception("Invalid file; overlapping sections")

        return obj

    def to_bytes(self):
        """Returns a newly constructed bytes representation of the file."""
        self.tables.sort(key=lambda table: str2tag(table.tag))
        search_range, entry_selector, range_shift = calc_search_range(len(self.tables))
        data = header_s.pack(
            self.sfnt_version,
            len(self.tables),
            search_range,
            entry_selector,
            range_shift,
        )
        font_data = b""
        offset = HEADER_SIZE + len(self.tables) * TABLE_SIZE
        for table in self.tables:
            table_data = table.pack()
            data += table_s.pack(
                str2tag(table.tag), table.checksum, offset, len(table_data)
            )
            font_data += table_data
            offset += len(table_data)
            while offset % 4:
                font_data += b"\0"
                offset += 1

        return data + font_data

    def to_woff(self):
        """Generate a WOFF file object from this OTF file."""
        woff_f = woff.File()
        woff_f.sfnt_version = self.sfnt_version
        woff_f.tables = self.tables.copy()
        return woff_f
