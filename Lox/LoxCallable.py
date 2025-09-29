from __future__ import annotations
from typing import Any, TYPE_CHECKING

# To make an abstract LoxCallable class.
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from Interpreter import Interpreter

class LoxCallable(ABC):
    @abstractmethod
    def arity(self) -> list[int]:
        pass

    @abstractmethod
    def call(self, interpreter: Interpreter, arguments: list[Any]) -> None:
        pass