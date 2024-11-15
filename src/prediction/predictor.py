from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Set

from reader.method_signature import MethodSignature

class TestPredictor(ABC):
    @abstractmethod
    def predict(self) -> Set[MethodSignature]:
        pass