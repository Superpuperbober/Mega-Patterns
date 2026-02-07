from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Protocol


class ISoftware(Protocol):
    def name(self) -> str: ...
    def operation(self) -> str: ...


@dataclass(frozen=True)
class BaseSoftware:
    title: str = "Base Software"

    def name(self) -> str:
        return self.title

    def operation(self) -> str:
        return "Базовое ПО готово к работе."


@dataclass
class Equipment:
    equipment_type: str
    specs: dict
    functions: List[str] = field(default_factory=list)
    software: ISoftware = field(default_factory=BaseSoftware)
    base_software: ISoftware | None = None
    build_log: List[str] = field(default_factory=list)

    # Для memento
    base_software_title: str = "Base Software"
    use_online: bool = False
    use_analytics: bool = False
    use_proxy: bool = False
    license_key: str = ""


    def summary(self) -> str:
        funcs = ", ".join(self.functions) if self.functions else "—"
        specs_lines = "\n".join([f"- {k}: {v}" for k, v in self.specs.items()]) or "—"
        return (
            f"Тип: {self.equipment_type}\n"
            f"ПО: {self.software.name()}\n\n"
            f"Спецификации:\n{specs_lines}\n\n"
            f"Функции:\n{funcs}\n\n"
            f"ПО выполняет:\n{self.software.operation()}"
        )

    def reset(self) -> None:
        self.specs = {}
        self.functions = []
        self.software = BaseSoftware()

