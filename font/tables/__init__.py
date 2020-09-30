from . import (
    avar,
    bhed,
    cvt,
    EBSC,
    fpgm,
    fvar,
    gasp,
    gcid,
    head,
    hhea,
    LTSH,
    maxp,
    prep,
    meta,
    utils,
)
import io


def new_table(tag, data, parent):
    data = io.BytesIO(data)
    if tag == "avar":
        return avar.AxisVariationsTable(tag, data, parent)

    if tag == "bhed":
        return bhed.BitmapFontHeaderTable(tag, data, parent)

    if tag == "cvt ":
        return cvt.ControlValueTable(tag, data, parent)

    if tag == "EBSC":
        return EBSC.EmbeddedBitmapScalingTable(tag, data, parent)

    if tag == "fpgm":
        return fpgm.FontProgramTable(tag, data, parent)

    if tag == "fvar":
        return fvar.FontVariationsTable(tag, data, parent)

    if tag == "gasp":
        return gasp.GridFittingAndScanConversionProcedureTable(tag, data, parent)

    if tag == "gcid":
        return gcid.GlyphToCIDMappingTable(tag, data, parent)

    if tag == "head":
        return head.FontHeaderTable(tag, data, parent)

    if tag == "hhea":
        return hhea.HorizontalHeaderTable(tag, data, parent)

    if tag == "LTSH":
        return LTSH.LinearThresholdTable(tag, data, parent)

    if tag == "maxp":
        return maxp.MaximunProfileTable(tag, data, parent)

    if tag == "prep":
        return prep.ControlValueProgramTable(tag, data, parent)

    if tag == "meta":
        return meta.MetadataTable(tag, data, parent)

    else:
        return utils.Table(tag, data, parent)
