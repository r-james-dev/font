from . import otf, tables, utils
import io
import struct

header_s = struct.Struct(">I2HI")
header_v2_s = struct.Struct(">3I")
uint32 = struct.Struct(">I")

HEADER_SIZE = 12
TABLE_SIZE = 16

UINT32_SIZE = 4


class File(object):
    def __init__(self):
        self.fonts = []

    @classmethod
    def from_bytes(cls, bytes):
        """Generate a TTC file from a string of bytes."""
        return cls.from_file(io.BytesIO(bytes))

    @classmethod
    def from_file(cls, fp):
        obj = cls()
        ttc_tag, major_version, minor_version, num_fonts = header_s.unpack(
            fp.read(HEADER_SIZE)
        )
        offset_table = []
        for _ in range(num_fonts):
            offset_table.append(uint32.unpack(fp.read(UINT32_SIZE))[0])

        if major_version == 2:
            dsig_tag, dsig_length, dsig_offset = header_v2_s.unpack(
                fp.read(HEADER_SIZE)
            )

        obj.fonts = []
        for font_offset in offset_table:
            fp.seek(font_offset)
            otf_f = otf.File()
            otf_f.sfnt_version, num_tables, *_ = otf.header_s.unpack(
                fp.read(HEADER_SIZE)
            )

            ranges = [
                range(HEADER_SIZE),
                range(font_offset, font_offset + HEADER_SIZE + num_tables * TABLE_SIZE),
            ]

            for _ in range(num_tables):
                tag, _, offset, length = otf.table_s.unpack(fp.read(TABLE_SIZE))

                ranges.append(range(offset, offset + length))

                start = fp.tell()
                fp.seek(offset)
                table = tables.new_table(utils.tag2str(tag), fp.read(length), obj)
                fp.seek(start)

                otf_f.tables.append(table)

            otf_f.tables.sort(key=lambda table: utils.str2tag(table.tag))
            obj.fonts.append(otf_f)

        return obj

    def to_bytes(self):
        """Convert this file to bytes and re-use any tables possible."""
        offset = 2 * HEADER_SIZE + len(self.fonts) * UINT32_SIZE
        header = header_s.pack(utils.str2tag("ttcf"), 2, 0, len(self.fonts))
        font_offsets = []

        dsig = None

        data = []
        used = []
        for font in self.fonts:
            font_offsets.append(offset)
            offset += HEADER_SIZE + len(font.tables) * TABLE_SIZE

            font_data = b""
            font_table_data = otf.header_s.pack(
                font.sfnt_version,
                len(font.tables),
                *utils.calc_search_range(len(font.tables))
            )

            font.tables.sort(key=lambda table: utils.str2tag(table.tag))
            for table in font.tables:
                if table.tag == "DSIG":
                    dsig = table
                    continue

                table_data = table.pack()
                for prev in used:
                    if prev[0] == table_data:
                        font_table_data += otf.table_s.pack(
                            utils.str2tag(table.tag), table.checksum, *prev[1]
                        )
                        break

                else:
                    while offset % 4:
                        font_data += b"\0"
                        offset += 1

                    font_data += table_data
                    font_table_data += otf.table_s.pack(
                        utils.str2tag(table.tag),
                        table.checksum,
                        offset,
                        len(table_data),
                    )
                    offset += len(table_data)

            data.append(font_table_data + font_data)

        header += b"".join(uint32.pack(i) for i in font_offsets)
        data = b"".join(data)
        if dsig is None:
            header += header_v2_s.pack(0, 0, 0)

        else:
            while offset % 4:
                data += b"\0"
                offset += 1

            dsig_data = dsig.pack()
            header += header_v2_s.pack(utils.str2tag("DSIG"), len(dsig_data), offset)
            data += dsig_data

        return header + data

    def to_woff(self):
        if len(self.fonts) > 1:
            return [font.to_woff() for font in self.fonts]

        elif len(self.fonts) == 1:
            return self.fonts[0].to_woff()
