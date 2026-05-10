from abc import ABC, abstractmethod

from portico.render.color import ColorMode
from portico.schema import PorticoJSON


class PorticoRenderer(ABC):
    @abstractmethod
    def render(
        self,
        data: PorticoJSON,
        *,
        width: int,
        color: ColorMode,
        legend: bool,
        apex_override: tuple[str, str] | None = None,
        apex_seed_label: str | None = None,
    ) -> str:
        """Render the portico as a single string of ASCII (newline-separated lines).

        apex_override -- if provided, replaces the locked (finial, keystone) rows.
        apex_seed_label -- if provided, appended left-justified above the signature.
        """
