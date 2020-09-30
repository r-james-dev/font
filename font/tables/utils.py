import struct

s_bit_line_metrics_s = struct.Struct("2bB9b")


class Table(object):
    """Base class for font tables."""

    def __init__(self, tag, data, parent):
        self.tag = tag
        self.data = data
        self.parent = parent
        self.data.seek(0)

    def __repr__(self):
        return " ".join(i for i in "<{} Table>".format(self.tag).split() if i != "")

    def pack(self):
        self.data.seek(0)
        return self.data.read()

    @property
    def checksum(self):
        """Calculate checksum for this table."""
        data = self.pack()
        while len(data) % 4:
            data += b"\0"

        return sum(struct.unpack(f">{len(data) // 4}I", data)) % 2 ** 32


class SBitLineMetrics(object):
    def __init__(self, data):
        (
            self.ascender,
            self.descender,
            self.width_max,
            self.caret_slope_numerator,
            self.caret_slope_denominator,
            self.caret_offset,
            self.min_origin_sb,
            self.min_advance_sb,
            self.max_before_bl,
            self.min_after_bl,
            self.pad1,
            self.pad2,
        ) = s_bit_line_metrics_s.unpack(data.read(12))

    def pack(self):
        return s_bit_line_metrics_s.pack(
            self.ascender,
            self.descender,
            self.width_max,
            self.caret_slope_numerator,
            self.caret_slope_denominator,
            self.caret_offset,
            self.min_origin_sb,
            self.min_advance_sb,
            self.max_before_bl,
            self.min_after_bl,
            self.pad1,
            self.pad2,
        )
