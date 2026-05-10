from arqii.render.base import PorticoRenderer
from arqii.render.color import ColorMode
from arqii.schema import FitQuality, PorticoJSON

CAVEAT_LINE = (
    "note: the portico metaphor is stretched for this input -- see --verbose for why."
)

REFUSAL_INTRO = "this input does not have enough structure to build a portico from."

APEX_FINIAL = "***"
APEX_KEYSTONE = "===  ◇  ==="

SIGNATURE_SUFFIX = " built with _ii^ ──"


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


def _signature_line(width: int) -> str:
    if width < len(SIGNATURE_SUFFIX) + 4:
        return SIGNATURE_SUFFIX.lstrip()
    return "─" * (width - len(SIGNATURE_SUFFIX)) + SIGNATURE_SUFFIX


def _pillar_column_width(width: int, num_pillars: int) -> int:
    """Per-pillar column width. Shrinks before forcing labels to wrap (spec §5)."""
    ideal = 16
    available = max(0, width - 6)
    max_cw = available // num_pillars
    if max_cw >= ideal:
        return ideal
    return max(4, max_cw)


def _row_of(symbol: str, num: int, cw: int) -> str:
    return "".join(_center(symbol, cw) for _ in range(num))


def _legend(data: PorticoJSON) -> list[str]:
    lines = ["", "legend:", f"  ^  {data.roof.label}: {data.roof.summary}"]
    lines.extend(f"  ii {p.label}: {p.summary}" for p in data.pillars)
    base_labels = " | ".join(data.base.labels)
    lines.append(f"  _  {base_labels}: {data.base.summary}")
    return lines


def _slope_line(line_width: int, fill: str = "═") -> str:
    if line_width < 4:
        return ""
    return "//" + fill * (line_width - 4) + "\\\\"


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


def _split_label(label: str, cw: int) -> tuple[str, str, bool]:
    """Split a too-long label into 2 rows.

    Returns (line1, line2, safety_truncated). Both lines fit in cw - 1 chars.
    safety_truncated = True if the label exceeded 2*(cw-1) and line2 was ellipsized.
    """
    space = cw - 1

    # Safety net: even 2 rows can't hold it.
    if len(label) > 2 * space:
        return label[:space], label[space : 2 * space - 1] + "…", True

    # Try rightmost word boundary in first cw chars.
    break_chars = (" ", "-", "+")
    for i in range(min(cw, len(label) - 1), 0, -1):
        if label[i] in break_chars:
            if label[i] == " ":
                cand1, cand2 = label[:i], label[i + 1 :]
            else:
                cand1, cand2 = label[: i + 1], label[i + 1 :]
            if len(cand1) <= space and len(cand2) <= space:
                return cand1, cand2, False

    # Balanced char split (guaranteed to fit since len <= 2*space).
    mid = (len(label) + 1) // 2
    return label[:mid], label[mid:], False


class DefaultRenderer(PorticoRenderer):
    def render(
        self,
        data: PorticoJSON,
        *,
        width: int,
        color: ColorMode,
        verbose: bool,
        apex_override: tuple[str, str] | None = None,
        apex_seed_label: str | None = None,
    ) -> str:
        # Color path deferred: snapshot tests pin color=NEVER.
        _ = color

        lines: list[str] = []
        truncations: list[tuple[str, str]] = []  # only safety-net path adds entries

        # Refusal path: the analyzer judged this input non-decomposable. Emit a
        # banner + reason + signature instead of forcing a portico.
        if data.fit_quality == FitQuality.NOT_APPLICABLE:
            lines.append(_banner(data.theme, data.title, width))
            lines.append("")
            lines.append("  " + REFUSAL_INTRO)
            if data.notes_on_fit:
                lines.append("")
                lines.append(f"  reason: {data.notes_on_fit}")
            if verbose:
                lines.extend(_legend(data))
            lines.append("")
            lines.append(_signature_line(width))
            return "\n".join(line.rstrip() for line in lines) + "\n"

        if data.fit_quality == FitQuality.STRETCHED:
            lines.append(CAVEAT_LINE)
            lines.append("")

        lines.append(_banner(data.theme, data.title, width))
        lines.append("")

        num_pillars = len(data.pillars)
        cw = _pillar_column_width(width, num_pillars)
        block_width = cw * num_pillars
        indent = " " * max(0, (width - block_width) // 2)

        # --- Apex composition: finial above keystone (2 rows).
        finial, keystone = apex_override or (APEX_FINIAL, APEX_KEYSTONE)
        lines.append(_center(finial, width))
        lines.append(_center(keystone, width))

        # --- Upper pediment slope (block - 8) + roof box (block - 6).
        upper_slope_width = block_width - 8
        if upper_slope_width >= 4:
            lines.append(_center(_slope_line(upper_slope_width), width))

        roof_box_width = block_width - 6
        if roof_box_width >= 6:
            roof_inner = roof_box_width - 2
            roof_shown = _truncate(data.roof.label, roof_inner)
            if roof_shown != data.roof.label:
                truncations.append((roof_shown, data.roof.label))
            lines.append(_center(_box_top(roof_box_width), width))
            lines.append(_center(_box_mid(roof_box_width, data.roof.label), width))
            lines.append(_center(_box_bottom(roof_box_width), width))

        # --- Lower pediment (block wide, ~ infill) + top cornice (░, block-2).
        lines.append(_center(_slope_line(block_width, fill="~"), width))
        if block_width - 2 >= 1:
            lines.append(_center("░" * (block_width - 2), width))

        # --- Columns: cap, 2 shafts, label(s), 2 shafts, plinth.
        cap_row = indent + _row_of("▀██▀", num_pillars, cw)
        shaft_row = indent + _row_of("██", num_pillars, cw)
        plinth_row = indent + _row_of("▄██▄", num_pillars, cw)

        wrap_active = any(len(p.label) > cw - 1 for p in data.pillars)

        lines.append(cap_row)
        lines.extend([shaft_row] * 2)

        if wrap_active:
            row1_cells: list[str] = []
            row2_cells: list[str] = []
            for p in data.pillars:
                if len(p.label) > cw - 1:
                    line1, line2, safety = _split_label(p.label, cw)
                    if safety:
                        truncations.append((line2, p.label))
                    row1_cells.append(_center(line1, cw))
                    row2_cells.append(_center(line2, cw))
                else:
                    # Short label in a wrap-active render: row 2 is shaft fill so
                    # the column reads as continuous through the gap.
                    row1_cells.append(_center(p.label, cw))
                    row2_cells.append(_center("██", cw))
            lines.append(indent + "".join(row1_cells))
            lines.append(indent + "".join(row2_cells))
        else:
            cells = [_center(p.label, cw) for p in data.pillars]
            lines.append(indent + "".join(cells))

        lines.extend([shaft_row] * 2)
        lines.append(plinth_row)

        # --- Bottom cornice region: ░ (block-2) then ^ (block). No stylobate.
        if block_width - 2 >= 1:
            lines.append(_center("░" * (block_width - 2), width))
        if block_width >= 1:
            lines.append(_center("^" * block_width, width))

        # --- Base box (block + 4).
        base_box_width = block_width + 4
        joined_base = " | ".join(data.base.labels)
        if base_box_width >= 6 and base_box_width <= width:
            base_inner = base_box_width - 2
            base_shown = _truncate(joined_base, base_inner)
            if base_shown != joined_base:
                truncations.append((base_shown, joined_base))
            lines.append(_center(_box_top(base_box_width), width))
            lines.append(_center(_box_mid(base_box_width, joined_base), width))
            lines.append(_center(_box_bottom(base_box_width), width))

        if verbose:
            lines.extend(_legend(data))
        elif truncations:
            lines.append("")
            lines.append("truncated labels:")
            for shown, full in truncations:
                lines.append(f"  {shown} → {full}")

        # Signature mirrors the opening banner -- announces "this output is done".
        lines.append("")
        if apex_seed_label is not None:
            lines.append(apex_seed_label)
        lines.append(_signature_line(width))

        return "\n".join(line.rstrip() for line in lines) + "\n"
