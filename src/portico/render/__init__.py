from portico.render.color import ColorMode
from portico.render.styles.default import DefaultRenderer
from portico.schema import PorticoJSON

DEFAULT_WIDTH = 80
MAX_WIDTH = 100


def render(
    data: PorticoJSON,
    *,
    width: int = DEFAULT_WIDTH,
    color: ColorMode = ColorMode.NEVER,
    verbose: bool = False,
    apex_override: tuple[str, str] | None = None,
    apex_seed_label: str | None = None,
) -> str:
    return DefaultRenderer().render(
        data,
        width=width,
        color=color,
        verbose=verbose,
        apex_override=apex_override,
        apex_seed_label=apex_seed_label,
    )
