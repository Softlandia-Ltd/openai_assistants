from typing import Callable
from dataclasses import dataclass


@dataclass
class Tool:
    name: str
    schema: dict
    func: Callable
