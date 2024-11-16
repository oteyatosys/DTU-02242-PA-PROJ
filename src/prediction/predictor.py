from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Set

from reader.method_signature import MethodSignature
from reader.program import Program

class TestPredictor(ABC):
    @abstractmethod
    def predict(self, old_program: Program, new_program: Program) -> Set[MethodSignature]:
        pass