from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol


class SystemContext(Protocol):
    def enable_editing(self, enabled: bool) -> None: ...
    def set_status(self, text: str) -> None: ...


class SystemState(ABC):
    def __init__(self, context: SystemContext):
        self.context = context

    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def show_funcs(self) -> None: ...


class EditState(SystemState):
    def name(self) -> str:
        return "EDIT"

    def show_funcs(self) -> None:
        self.context.enable_editing(True)
        self.context.set_status("Режим EDIT: можно создавать тренажёры и менять конфигурацию ПО.")


class ViewState(SystemState):
    def name(self) -> str:
        return "VIEW"

    def show_funcs(self) -> None:
        self.context.enable_editing(False)
        self.context.set_status("Режим VIEW: только просмотр, изменения запрещены.")
