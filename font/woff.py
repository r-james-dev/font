from . import otf, tables, utils
import io
import struct
import zlib

HEADER_SIZE = 44
TABLE_SIZE = 20

header_s = struct.Struct(">3I2HI2H5I")
table_s = struct.Struct(">5I")


class File(object):
    """Web Open Font Format 1.0 file."""

    __slots__ = [
        "major_version",
        "metadata",
        "minor_version",
        "privatedata",
        "sfnt_version",
        "tables",
    ]

    def __init__(self):
        """Generate an empty WOFF file."""
        self.major_version = 0
        self.metadata = b""
        self.minor_version = 0
        self.privatedata = b""
        self.sfnt_version = None
        self.tables = []

    @classmethod
    def from_bytes(cls, bytes):
        """Generate a WOFF file from a string of bytes."""
        fp = io.BytesIO(bytes)
        return cls.from_file(fp)

    @classmethod
    def from_file(cls, fp):
        """Generate a WOFF file from a file object."""
        file_length = len(fp.read())
        fp.seek(0)
        obj = cls()
        (
            signature,
            obj.sfnt_version,
            _,  # length unneeded
            num_tables,
            reserved,
            total_sfnt_size,
            obj.major_version,
            obj.minor_version,
            meta_offset,
            meta_length,
            meta_orig_length,
            priv_offset,
            priv_length,
        ) = header_s.unpack(fp.read(HEADER_SIZE))
        if utils.tag2str(signature) != "wOFF":
            raise Exception(
                "Invalid file signature; expected: 'wOFF', received: '{}'".format(
                    signature
                )
            )

        if reserved:
            raise Exception(
                "Invalid reserved value in file header; expected: 0x0000, received: {}".format(
                    "0x" + hex(reserved)[2:].zfill(4)
                )
            )

        if total_sfnt_size % 4:
            raise Exception(
                "Invalid provided sfnt size ({}); size must be a multiple of four".format(
                    total_sfnt_size
                )
            )

        ranges = [
            range(HEADER_SIZE),
            range(HEADER_SIZE, HEADER_SIZE + num_tables * TABLE_SIZE),
        ]

        for _ in range(num_tables):
            tag, offset, comp, length, checksum = table_s.unpack(fp.read(TABLE_SIZE))

            ranges.append(range(offset, offset + comp))

            start = fp.tell()
            fp.seek(offset)

            if comp == length:
                # data left uncompressed
                table = tables.new_table(utils.tag2str(tag), fp.read(length))

            elif comp < length:
                # decompress data
                try:
                    table = tables.new_table(
                        utils.tag2str(tag), zlib.decompress(fp.read(comp))
                    )

                except zlib.error:
                    raise Exception(
                        "Invalid {} table; failed to decompress".format(
                            utils.tag2str(tag)
                        )
                    )

            else:
                raise Exception(
                    "Invalid {} table; compressed length is larger than original".format(
                        utils.tag2str(tag)
                    )
                )

            obj.tables.append(table)

            if checksum != table.checksum:
                raise Exception(
                    "Invalid {} table checksum; expected: {}, received: {}".format(
                        table.tag, table.checksum, checksum
                    )
                )

        obj.tables.sort(key=lambda table: utils.str2tag(table.tag))

        obj.metadata = b""
        if meta_length:
            fp.seek(meta_offset)
            try:
                obj.metadata = zlib.decompress(fp.read(meta_length))
                if len(obj.metadata) != meta_orig_length:
                    # invalid metadata section
                    obj.metadata = b""

                else:
                    ranges.append(range(meta_offset, meta_offset + meta_length))

            except zlib.error:
                obj.metadata = b""

        obj.privatedata = b""
        if priv_length:
            fp.seek(priv_offset)
            obj.privatedata = fp.read(priv_length)
            ranges.append(range(priv_offset, priv_offset + priv_length))

        if utils.check_range_overlap(ranges):
            raise Exception("Invalid file; overlapping sections")

        return obj

    def to_bytes(self):
        """Returns a newly constructed bytes representation of the file."""
        self.tables.sort(key=lambda table: utils.str2tag(table.tag))
        tables = b""
        data = b""
        offset = HEADER_SIZE + (TABLE_SIZE * len(self.tables))
        for table in self.tables:
            if table.tag == "head":
                table.checksum_adjustment = 0
                table.checksum_adjustment = utils.calc_checksum_adjustment(self)

            table_data = table.pack()

            orig_length = len(table_data)
            comp = zlib.compress(table_data)
            if len(comp) >= orig_length:
                # do not compress if doing so increases the size of the data or has not effect
                comp = table_data

            data += comp

            tables += table_s.pack(
                utils.str2tag(table.tag),
                offset,
                len(comp),
                orig_length,
                table.checksum,
            )

            offset += len(comp)
            while offset % 4:
                offset += 1
                data += b"\0"

        data = tables + data

        meta_offset = meta_orig_length = meta_length = 0
        if self.metadata:
            meta_offset = offset
            comp = zlib.compress(self.metadata)
            meta_length = len(comp)
            data += comp
            offset += meta_length

        priv_offset = priv_length = 0
        if self.privatedata:
            while offset % 4:
                offset += 1
                data += b"\0"

            priv_offset = offset
            data += self.privatedata

        return (
            header_s.pack(
                utils.str2tag("wOFF"),
                self.sfnt_version,
                len(data) + 44,
                len(self.tables),
                0,
                len(self.to_otf().to_bytes()),
                self.major_version,
                self.minor_version,
                meta_offset,
                meta_length,
                len(self.metadata),
                priv_offset,
                len(self.privatedata),
            )
            + data
        )

    def to_otf(self):
        """Generate an OTF file object from this WOFF file."""
        otf_f = otf.File()
        otf_f.sfnt_version = self.sfnt_version
        otf_f.tables = self.tables.copy()
        return otf_f
