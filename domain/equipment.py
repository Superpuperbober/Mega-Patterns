from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Protocol
from abc import ABC, abstractmethod

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


class Equipment(ABC):
    name: str = ""

    @abstractmethod
    def summary(self) -> str:
        raise NotImplementedError
    

@dataclass
class EquipmentType(Equipment):
    name: str = ""
    models: List["EquipmentModel"] = field(default_factory=list)  # ✅ в кавычках

    def summary(self) -> str:
        result = "-" * 8 + f"\nТип тренажера: {self.name}\n"
        if not self.models:
            result += "Модели отсутствуют\n"
        else:
            for model in self.models:
                result += model.summary() + "\n"
        result += "-" * 8 + "\n"
        return result


@dataclass
class EquipmentModel(Equipment):
    name: str = ""
    equipment_type: str = ""   # ✅ вернуть (тип, к которому относится модель)

    specs: dict = field(default_factory=dict)
    functions: List[str] = field(default_factory=list)
    software: ISoftware = field(default_factory=BaseSoftware)

    # memento state
    base_software_title: str = "Base Software"
    use_online: bool = False
    use_analytics: bool = False
    use_proxy: bool = False
    license_key: str = ""

    build_log: List[str] = field(default_factory=list)

    def summary(self) -> str:
        funcs = ", ".join(self.functions) if self.functions else "—"
        specs_lines = "\n".join([f"- {k}: {v}" for k, v in self.specs.items()]) if self.specs else "—"
        return (
            f"Тип: {self.equipment_type}\n"
            f"Модель: {self.name}\n"
            f"ПО: {self.software.name()}\n\n"
            f"Спецификации:\n{specs_lines}\n\n"
            f"Функции:\n{funcs}\n\n"
            f"ПО выполняет:\n{self.software.operation()}"
        )
