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
    models: List[EquipmentModel] = field(default_factory=list)

    def summary(self) -> str:
        result: str
        
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
    specs: dict = field(default_factory=dict)
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
        specs_lines = "\n".join([f"- {k}: {v}" for k, v in self.specs.items()]) if self.specs else "—"
        return (
            f"  Название: {self.name}\n"
            f"  ПО: {self.software.name()}\n"
            f"  ПО выполняет: {self.software.operation()}\n"
            f"  Спецификации:\n  {specs_lines}\n"
            f"  Функции: {funcs}\n"
            f"  Базовая программа: {self.base_software.name() if self.base_software else 'Отсутствует'}\n"
        )

    def reset(self) -> None:
        self.specs = {}
        self.functions = []
        self.software = BaseSoftware()
    
# equipments: List[Equipment] = []

# equipment1 = EquipmentType()
# equipment1.name = "Велик"

# model1 = EquipmentModel()
# model1.name = "Велик 0001"
# model1.base_software = BaseSoftware()

# model2 = EquipmentModel()
# model2.name = "Велик 0002"
# model2.base_software = BaseSoftware()

# model3 = EquipmentModel()
# model3.name = "Велик 0003"
# model3.base_software = BaseSoftware()

# equipment1.models = [model1, model2, model3]

# equipment2 = EquipmentType()
# equipment2.name = "Бабочка"

# model5 = EquipmentModel()
# model5.name = "Супер пупер бабочка 0001"
# model5.base_software = BaseSoftware()

# equipment2.models = [model5]

# equipment3 = EquipmentType()
# equipment3.name = "Скакалка"

# model4 = EquipmentModel()
# model4.name = "Скакалка 7000"
# model4.base_software = BaseSoftware()

# equipment3.models = [model4]

# # Создание оборудования 4
# equipment4 = EquipmentType()
# equipment4.name = "Беговая дорожка"

# model6 = EquipmentModel()
# model6.name = "Бег дор 0004"
# model6.base_software = BaseSoftware()

# model7 = EquipmentModel()
# model7.name = "Бег дор 0001"
# model7.base_software = BaseSoftware()

# equipment4.models = [model7, model6]

# equipments = [equipment1, equipment2, equipment3, equipment4]

# for equipment in equipments:
#     print(equipment.summary())
#     print()