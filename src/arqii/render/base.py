from abc import ABC, abstractmethod

from arqii.render.color import ColorMode
from arqii.schema import PorticoJSON


class PorticoRenderer(ABC):
    @abstractmethod
    def render(
        self,
        data: PorticoJSON,
        *,
        width: int,
        color: ColorMode,
        verbose: bool,
    ) -> str:
        """Render the portico as a single string of ASCII (newline-separated lines)."""
