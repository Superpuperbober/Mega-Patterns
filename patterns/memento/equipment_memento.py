from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import copy


@dataclass(frozen=True)
class EquipmentMemento:
    equipment_type: str
    specs: Dict[str, Any]
    functions: List[str]

    base_software_title: str
    use_online: bool
    use_analytics: bool
    use_proxy: bool
    license_key: str


class Caretaker:
    """
    Хранит историю memento и умеет undo/redo.
    """
    def __init__(self) -> None:
        self._history: list[EquipmentMemento] = []
        self._index: int = -1  # указывает на текущий memento

    def backup(self, memento: EquipmentMemento) -> None:
        # если мы откатились назад и потом сохраняем новое — стираем ветку redo
        if self._index < len(self._history) - 1:
            self._history = self._history[: self._index + 1]

        self._history.append(memento)
        self._index += 1

    def can_undo(self) -> bool:
        return self._index > 0

    def can_redo(self) -> bool:
        return self._index < len(self._history) - 1

    def undo(self) -> Optional[EquipmentMemento]:
        if not self.can_undo():
            return None
        self._index -= 1
        return self._history[self._index]

    def redo(self) -> Optional[EquipmentMemento]:
        if not self.can_redo():
            return None
        self._index += 1
        return self._history[self._index]

    def info(self) -> str:
        return f"History: {len(self._history)} snapshots, current index: {self._index}"
