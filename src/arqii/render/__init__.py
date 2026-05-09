from arqii.render.color import ColorMode
from arqii.render.styles.default import DefaultRenderer
from arqii.schema import PorticoJSON

DEFAULT_WIDTH = 80
MAX_WIDTH = 100


def render(
    data: PorticoJSON,
    *,
    width: int = DEFAULT_WIDTH,
    color: ColorMode = ColorMode.NEVER,
    verbose: bool = False,
) -> str:
    return DefaultRenderer().render(data, width=width, color=color, verbose=verbose)
