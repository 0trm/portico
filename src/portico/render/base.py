from abc import ABC, abstractmethod

from portico.render.color import ColorMode
from portico.schema import StructureJSON


class StructureRenderer(ABC):
    @abstractmethod
    def render(
        self,
        data: StructureJSON,
        *,
        width: int,
        color: ColorMode,
        verbose: bool,
        apex_override: tuple[str, str] | None = None,
        apex_seed_label: str | None = None,
    ) -> str:
        """Render the structure as a single string of ASCII (newline-separated lines).

        apex_override -- if provided, replaces the locked (finial, keystone) rows.
        apex_seed_label -- if provided, appended left-justified above the signature.
        """
