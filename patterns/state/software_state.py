from __future__ import annotations
from abc import ABC, abstractmethod


class SoftwareState(ABC):
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def operation(self, ctx: "StatefulSoftware") -> str: ...


class SetupState(SoftwareState):
    def name(self) -> str:
        return "SETUP"

    def operation(self, ctx: "StatefulSoftware") -> str:
        return "Режим настройки: можно изменять конфигурацию ПО."


class IdleState(SoftwareState):
    def name(self) -> str:
        return "IDLE"

    def operation(self, ctx: "StatefulSoftware") -> str:
        return "Режим ожидания: ПО готово к запуску тренировки."


class TrainingState(SoftwareState):
    def name(self) -> str:
        return "TRAINING"

    def operation(self, ctx: "StatefulSoftware") -> str:
        return "Тренировка запущена: ПО активно работает."


class LockedState(SoftwareState):
    def name(self) -> str:
        return "LOCKED"

    def operation(self, ctx: "StatefulSoftware") -> str:
        return "ПО заблокировано: отсутствует лицензия или доступ."

class StatefulSoftware:
    def __init__(self, base_title: str) -> None:
        self._base_title = base_title
        self._state: SoftwareState = SetupState()

    def set_state(self, state: SoftwareState) -> None:
        self._state = state

    def name(self) -> str:
        return f"{self._base_title} [{self._state.name()}]"

    def operation(self) -> str:
        return self._state.operation(self)
