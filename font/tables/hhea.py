from .utils import Table
import struct

hhea_s = struct.Struct(">2H3hH11hH")


class HorizontalHeaderTable(Table):
    def __init__(self, *args):
        super().__init__(*args)
        (
            _,
            _,
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
            _,
            self.number_of_h_metrics,
        ) = hhea_s.unpack(self.data.read(36))
        del self.data

    def pack(self):
        return hhea_s.pack(
            1,
            0,
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
            0,
            self.number_of_h_metrics,
        )
