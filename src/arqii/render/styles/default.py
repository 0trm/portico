from arqii.render.base import PorticoRenderer
from arqii.render.color import ColorMode
from arqii.schema import FitQuality, Layer, PorticoJSON

CAVEAT_LINE = (
    "note: the portico metaphor is stretched for this input -- see --verbose for why."
)

TOP_MARK = "__***__"


def _truncate(s: str, max_len: int) -> str:
    if max_len <= 0:
        return ""
    if len(s) <= max_len:
        return s
    if max_len == 1:
        return "…"
    return s[: max_len - 1] + "…"


def _center(s: str, width: int) -> str:
    if len(s) >= width:
        return s[:width]
    pad = width - len(s)
    left = pad // 2
    right = pad - left
    return " " * left + s + " " * right


def _banner(theme: str, title: str, width: int) -> str:
    lead = f"── {theme}: {title} "
    if len(lead) >= width:
        return lead[:width]
    return lead + "─" * (width - len(lead))


def _pillar_column_width(width: int, num_pillars: int) -> int:
    """Per-pillar column width. Shrinks before truncating labels (spec §5)."""
    ideal = 16
    available = max(0, width - 6)
    max_cw = available // num_pillars
    if max_cw >= ideal:
        return ideal
    return max(4, max_cw)


def _row_of(symbol: str, num: int, cw: int) -> str:
    return "".join(_center(symbol, cw) for _ in range(num))


def _label_row(pillars: list[Layer], cw: int) -> str:
    return "".join(_center(_truncate(p.label, cw - 1), cw) for p in pillars)


def _legend(data: PorticoJSON) -> list[str]:
    lines = ["", "legend:", f"  ^  {data.roof.label}: {data.roof.summary}"]
    lines.extend(f"  ii {p.label}: {p.summary}" for p in data.pillars)
    lines.append(f"  _  {data.base.label}: {data.base.summary}")
    return lines


def _slope_line(line_width: int) -> str:
    if line_width < 2:
        return ""
    if line_width == 2:
        return "/\\"
    return "/" + "═" * (line_width - 2) + "\\"


def _box_top(box_width: int) -> str:
    if box_width < 2:
        return ""
    return "╔" + "═" * (box_width - 2) + "╗"


def _box_mid(box_width: int, label: str) -> str:
    if box_width < 2:
        return ""
    inner = box_width - 2
    return "║" + _center(_truncate(label, inner), inner) + "║"


def _box_bottom(box_width: int) -> str:
    if box_width < 2:
        return ""
    return "╚" + "═" * (box_width - 2) + "╝"


class DefaultRenderer(PorticoRenderer):
    def render(
        self,
        data: PorticoJSON,
        *,
        width: int,
        color: ColorMode,
        verbose: bool,
    ) -> str:
        # Color path deferred: snapshot tests pin color=NEVER.
        _ = color

        lines: list[str] = []

        if data.fit_quality == FitQuality.STRETCHED:
            lines.append(CAVEAT_LINE)
            lines.append("")

        lines.append(_banner(data.theme, data.title, width))
        lines.append("")

        num_pillars = len(data.pillars)
        cw = _pillar_column_width(width, num_pillars)
        block_width = cw * num_pillars
        indent = " " * max(0, (width - block_width) // 2)

        # --- Roof ---
        lines.append(_center(TOP_MARK, width))

        # Stepped pediment slopes (B-22, B-12), then 3-row roof box (B-6).
        if block_width - 22 >= 4:
            lines.append(_center(_slope_line(block_width - 22), width))
        if block_width - 12 >= 4:
            lines.append(_center(_slope_line(block_width - 12), width))

        roof_box_width = block_width - 6
        if roof_box_width >= 6:
            lines.append(_center(_box_top(roof_box_width), width))
            lines.append(_center(_box_mid(roof_box_width, data.roof.label), width))
            lines.append(_center(_box_bottom(roof_box_width), width))

        # Slope row (B wide), then ~ cornice (B-2 wide) sitting just above the abacus.
        lines.append(_center(_slope_line(block_width), width))
        if block_width - 2 >= 1:
            lines.append(_center("~" * (block_width - 2), width))

        # --- Columns: ▀██▀ abacus, ██ shafts (2 above + 2 below the label), ▄██▄ plinth.
        cap_row = indent + _row_of("▀██▀", num_pillars, cw)
        shaft_row = indent + _row_of("██", num_pillars, cw)
        label_row = indent + _label_row(data.pillars, cw)
        plinth_row = indent + _row_of("▄██▄", num_pillars, cw)
        lines.append(cap_row)
        lines.extend([shaft_row] * 2)
        lines.append(label_row)
        lines.extend([shaft_row] * 2)
        lines.append(plinth_row)

        # --- Base: ^ row mirroring the roof's ~, then stylobate (B+4) and base box (B+6).
        if block_width - 2 >= 1:
            lines.append(_center("^" * (block_width - 2), width))

        sty_width = block_width + 4
        if sty_width <= width:
            lines.append(_center("═" * sty_width, width))

        base_box_width = block_width + 6
        if base_box_width >= 6 and base_box_width <= width:
            lines.append(_center(_box_top(base_box_width), width))
            lines.append(_center(_box_mid(base_box_width, data.base.label), width))
            lines.append(_center(_box_bottom(base_box_width), width))

        if verbose:
            lines.extend(_legend(data))

        return "\n".join(line.rstrip() for line in lines) + "\n"
