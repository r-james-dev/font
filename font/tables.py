from .utils import tag2str
import io
import struct

uint16 = struct.Struct(">H")

head_s = struct.Struct(">2H3I2H2q4h2H3h")
hhea_s = struct.Struct(">2H3hH11hH")
maxp_header_s = struct.Struct(">IH")
maxp_header_v1_s = struct.Struct(">13H")
gasp_s = struct.Struct(">2H")


def new_table(tag, data, **attrs):
    data = io.BytesIO(data)
    if tag == "cvt ":
        return ControlValueTable(tag, data, **attrs)

    if tag == "fpgm":
        return FontProgramTable(tag, data, **attrs)

    if tag == "gasp":
        return GridFittingAndScanConversionProcedureTable(tag, data, **attrs)

    if tag == "head":
        return FontHeaderTable(tag, data, **attrs)

    if tag == "hhea":
        return HorizontalHeaderTable(tag, data, **attrs)

    if tag == "maxp":
        return MaximunProfileTable(tag, data, **attrs)

    if tag == "prep":
        return ControlValueProgramTable(tag, data, **attrs)

    # no specific table object for this table type
    return Table(tag, data, **attrs)


class Table(object):
    """Base class for font tables."""

    def __init__(self, tag, data, **attrs):
        self.tag = tag
        self.data = data
        self.attrs = attrs

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

        return sum(struct.unpack(">{}I".format(len(data) // 4), data)) % 2 ** 32


class ControlValueTable(Table):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        fword_count = len(self.data.read()) // 2
        self.data.seek(0)
        self.values = struct.unpack(">{}h".format(fword_count), self.data.read())

    def pack(self):
        return struct.pack(">{}h".format(len(self.values)), *self.values)


class ControlValueProgramTable(Table):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        uint8_count = len(self.data.read())
        self.data.seek(0)
        self.values = struct.unpack("{}B".format(uint8_count), self.data.read())

    def pack(self):
        return struct.pack(">{}h".format(len(self.values)), *self.values)


class FontProgramTable(Table):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        uint8_count = len(self.data.read())
        self.data.seek(0)
        self.values = struct.unpack("{}B".format(uint8_count), self.data.read())

    def pack(self):
        return struct.pack(">{}h".format(len(self.values)), *self.values)


class FontHeaderTable(Table):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        (
            self.major_version,
            self.minor_version,
            self.font_revision,
            self.checksum_adjustment,
            _,
            self.flags,
            self.units_per_em,
            self.created,
            self.modified,
            self.x_min,
            self.y_min,
            self.x_max,
            self.y_max,
            self.mac_style,
            self.lowest_rec_ppem,
            self.font_direction_hint,
            self.index_to_loc_format,
            self.glyph_data_format,
        ) = head_s.unpack(self.data.read(54))

    @property
    def checksum(self):
        """Calculate checksum for this table."""
        # for purposes of calculating the checksum of a head table the checksum adjustment has to be zero
        tmp = self.checksum_adjustment
        self.checksum_adjustment = 0
        try:
            return super().checksum

        finally:
            self.checksum_adjustment = tmp

    def pack(self):
        return head_s.pack(
            self.major_version,
            self.minor_version,
            self.font_revision,
            self.checksum_adjustment,
            0x5F0F3CF5,
            self.flags,
            self.units_per_em,
            self.created,
            self.modified,
            self.x_min,
            self.y_min,
            self.x_max,
            self.y_max,
            self.mac_style,
            self.lowest_rec_ppem,
            self.font_direction_hint,
            self.index_to_loc_format,
            self.glyph_data_format,
        )


class GridFittingAndScanConversionProcedureTable(Table):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.version, num_ranges = gasp_s.unpack(self.data.read(4))
        self.ranges = []
        for _ in range(num_ranges):
            record = {}
            record["rangeMaxPPEM"], record["rangeGaspBehavior"] = gasp_s.unpack(
                self.data.read(4)
            )
            self.ranges.append(record)

    def pack(self):
        data = gasp_s.pack(self.version, len(self.ranges))
        for record in self.ranges:
            data += gasp_s.pack(record["rangeMaxPPEM"], record["rangeGaspBehavior"])

        return data


class HorizontalHeaderTable(Table):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        (
            self.major_version,
            self.minor_version,
            self.ascender,
            self.descender,
            self.line_gap,
            self.advance_width_max,
            self.min_left_side_bearing,
            self.min_right_side_bearing,
            self.x_max_extent,
            self.caret_slope_rise,
            self.caret_slope_run,
            self.caret_offset,
            _,
            _,
            _,
            _,
            self.metric_data_format,
            self.number_of_h_metrics,
        ) = hhea_s.unpack(self.data.read(36))

    def pack(self):
        return hhea_s.pack(
            self.major_version,
            self.minor_version,
            self.ascender,
            self.descender,
            self.line_gap,
            self.advance_width_max,
            self.min_left_side_bearing,
            self.min_right_side_bearing,
            self.x_max_extent,
            self.caret_slope_rise,
            self.caret_slope_run,
            self.caret_offset,
            0,
            0,
            0,
            0,
            self.metric_data_format,
            self.number_of_h_metrics,
        )


class MaximunProfileTable(Table):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.version, self.num_glyphs = maxp_header_s.unpack(self.data.read(6))
        self.version /= 2 ** 16
        if self.version == 1:
            (
                self.max_points,
                self.max_contours,
                self.max_composite_points,
                self.max_composite_contours,
                self.max_zones,
                self.max_twilight_points,
                self.max_storage,
                self.max_function_defs,
                self.max_instruction_defs,
                self.max_stack_elements,
                self.max_size_of_instructions,
                self.max_component_elements,
                self.max_component_depth,
            ) = maxp_header_v1_s.unpack(self.data.read(26))

    def pack(self):
        data = maxp_header_s.pack(int(self.version * 2 ** 16), self.num_glyphs)
        if self.version == 1:
            data += maxp_header_v1_s.pack(
                self.max_points,
                self.max_contours,
                self.max_composite_points,
                self.max_composite_contours,
                self.max_zones,
                self.max_twilight_points,
                self.max_storage,
                self.max_function_defs,
                self.max_instruction_defs,
                self.max_stack_elements,
                self.max_size_of_instructions,
                self.max_component_elements,
                self.max_component_depth,
            )

        return data
