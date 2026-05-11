from abc import ABC, abstractmethod

from portico.schema import PorticoJSON


class PorticoRenderer(ABC):
    @abstractmethod
    def render(
        self,
        data: PorticoJSON,
        *,
        width: int,
        height: int | None = None,
        legend: bool,
        apex_override: tuple[str, str] | None = None,
        apex_seed_label: str | None = None,
    ) -> str:
        """Render the portico as a single string of ASCII (newline-separated lines).

        height -- if set, the renderer trades wrapped legend for a compact 1-line-per-
            entry legend when the total output would otherwise exceed `height` rows.
        apex_override -- if provided, replaces the locked (finial, keystone) rows.
        apex_seed_label -- if provided, appended left-justified above the signature.
        """
