# travel_lotara/tools/base_tool.py
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """
    Base class for all Agent tools.
    Enforces consistent interface.
    """

    name: str
    description: str

    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool logic.

        Returns:
            Dict[str, Any]: structured result
        """
        pass
