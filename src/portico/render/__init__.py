from portico.render.styles.default import DefaultRenderer
from portico.schema import PorticoJSON

DEFAULT_WIDTH = 80
MAX_WIDTH = 100


def render(
    data: PorticoJSON,
    *,
    width: int = DEFAULT_WIDTH,
    height: int | None = None,
    legend: bool = True,
    apex_override: tuple[str, str] | None = None,
    apex_seed_label: str | None = None,
) -> str:
    return DefaultRenderer().render(
        data,
        width=width,
        height=height,
        legend=legend,
        apex_override=apex_override,
        apex_seed_label=apex_seed_label,
    )
