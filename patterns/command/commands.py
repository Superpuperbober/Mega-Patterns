from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from patterns.memento import EquipmentMemento


class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    # не все команды обязаны иметь undo
    def undo(self) -> None:
        raise NotImplementedError


class AppContext(ABC):
    """
    Мини-интерфейс того, что командам нужно от приложения.
    (Чтобы команды не зависели от конкретной реализации GUI.)
    """
    @abstractmethod
    def has_equipment(self) -> bool: ...
    @abstractmethod
    def get_snapshot(self) -> EquipmentMemento: ...
    @abstractmethod
    def restore_snapshot(self, snapshot: EquipmentMemento) -> None: ...
    @abstractmethod
    def push_snapshot(self, snapshot: EquipmentMemento) -> None: ...
    @abstractmethod
    def undo_snapshot(self) -> Optional[EquipmentMemento]: ...
    @abstractmethod
    def redo_snapshot(self) -> Optional[EquipmentMemento]: ...
    @abstractmethod
    def refresh_all(self) -> None: ...

    # “действия” системы (что именно меняем)
    @abstractmethod
    def set_decorators_state(self, online: bool, analytics: bool) -> None: ...
    @abstractmethod
    def set_proxy_state(self, enabled: bool, license_key: str) -> None: ...


class ApplyDecoratorsCommand(Command):
    def __init__(self, ctx: AppContext, online: bool, analytics: bool) -> None:
        self._ctx = ctx
        self._online = online
        self._analytics = analytics
        self._before: Optional[EquipmentMemento] = None

    def execute(self) -> None:
        if not self._ctx.has_equipment():
            return
        self._before = self._ctx.get_snapshot()
        self._ctx.set_decorators_state(self._online, self._analytics)
        self._ctx.push_snapshot(self._ctx.get_snapshot())
        self._ctx.refresh_all()

    def undo(self) -> None:
        if self._before:
            self._ctx.restore_snapshot(self._before)
            self._ctx.refresh_all()


class ApplyProxyCommand(Command):
    def __init__(self, ctx: AppContext, enabled: bool, license_key: str) -> None:
        self._ctx = ctx
        self._enabled = enabled
        self._license_key = license_key
        self._before: Optional[EquipmentMemento] = None

    def execute(self) -> None:
        if not self._ctx.has_equipment():
            return
        self._before = self._ctx.get_snapshot()
        self._ctx.set_proxy_state(self._enabled, self._license_key)
        self._ctx.push_snapshot(self._ctx.get_snapshot())
        self._ctx.refresh_all()

    def undo(self) -> None:
        if self._before:
            self._ctx.restore_snapshot(self._before)
            self._ctx.refresh_all()


class SaveSnapshotCommand(Command):
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    def execute(self) -> None:
        if not self._ctx.has_equipment():
            return
        self._ctx.push_snapshot(self._ctx.get_snapshot())
        self._ctx.refresh_all()


class UndoCommand(Command):
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    def execute(self) -> None:
        m = self._ctx.undo_snapshot()
        if m is not None:
            self._ctx.restore_snapshot(m)
            self._ctx.refresh_all()


class RedoCommand(Command):
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    def execute(self) -> None:
        m = self._ctx.redo_snapshot()
        if m is not None:
            self._ctx.restore_snapshot(m)
            self._ctx.refresh_all()
