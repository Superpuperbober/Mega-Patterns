from __future__ import annotations
from abc import ABC
from domain.equipment import ISoftware


class SoftwareDecorator(ABC):
    """Базовый декоратор: хранит обёрнутый объект и делегирует вызовы."""
    def __init__(self, wrapped: ISoftware) -> None:
        self._wrapped = wrapped

    def name(self) -> str:
        return self._wrapped.name()

    def operation(self) -> str:
        return self._wrapped.operation()


class OnlineSoftwareDecorator(SoftwareDecorator):
    def name(self) -> str:
        return f"{self._wrapped.name()} + Online"

    def operation(self) -> str:
        base = self._wrapped.operation()
        return base + "\n" + "Подключение к интернету: выполнено. Синхронизация включена."


class AnalyticsDecorator(SoftwareDecorator):
    def name(self) -> str:
        return f"{self._wrapped.name()} + Analytics"

    def operation(self) -> str:
        base = self._wrapped.operation()
        return base + "\n" + "Сбор статистики: включен. Метрики тренировки сохраняются."
