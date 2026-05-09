from arqii.render.base import PorticoRenderer
from arqii.render.color import ColorMode
from arqii.schema import FitQuality, Layer, PorticoJSON

CAVEAT_LINE = (
    "note: the portico metaphor is stretched for this input -- see --verbose for why."
)


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


class DefaultRenderer(PorticoRenderer):
    def render(
        self,
        data: PorticoJSON,
        *,
        width: int,
        color: ColorMode,
        verbose: bool,
    ) -> str:
        # Color path deferred: snapshot tests pin color=NEVER. ANSI shipping in a
        # follow-up once column-width math accounts for escape sequences.
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

        lines.append(_center(data.roof.label, width))
        # Pediment: 2 stepped rows of ^ growing to architrave width.
        lines.append(_center("^" * (block_width * 3 // 4), width))
        lines.append(_center("^" * block_width, width))
        # Cornice.
        lines.append(indent + "═" * block_width)

        # Columns: ┌┐ caps, ││ shafts, └┘ bases.
        cap_row = indent + _row_of("┌┐", num_pillars, cw)
        shaft_row = indent + _row_of("││", num_pillars, cw)
        label_row = indent + _label_row(data.pillars, cw)
        col_base_row = indent + _row_of("└┘", num_pillars, cw)
        lines.append(cap_row)
        lines.extend([shaft_row] * 3)
        lines.append(label_row)
        lines.extend([shaft_row] * 3)
        lines.append(col_base_row)

        # Stylobate: two stacked ═ lines.
        lines.append(indent + "═" * block_width)
        lines.append(indent + "═" * block_width)

        lines.append(_center(data.base.label, width))

        if verbose:
            lines.extend(_legend(data))

        return "\n".join(line.rstrip() for line in lines) + "\n"
