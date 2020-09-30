from .utils import Table
import struct

head_s = struct.Struct(">2H3I2H2Q4h2H3h")


class FontHeaderTable(Table):
    def __init__(self, *args):
        super().__init__(*args)
        (
            _,
            _,
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
        del self.data

    @property
    def checksum(self):
        """Calculate checksum for this table."""
        tmp = self.checksum_adjustment
        self.checksum_adjustment = 0
        value = super().checksum
        self.checksum_adjustment = tmp
        return value

    def pack(self):
        return head_s.pack(
            1,
            0,
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
