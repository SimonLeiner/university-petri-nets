"""This module contains the Interface Patterns."""

from abc import ABCMeta
from abc import abstractmethod


class InterfacePattern(metaclass=ABCMeta):
    """Base Class for Interface Patterns"""

    def __repr__(self) -> str:
        """String representation of the ExecutionHandler object."""
        return f"<{self.__class__.__name__}>"

    @abstractmethod
    def send_message() -> None:
        raise NotImplementedError
