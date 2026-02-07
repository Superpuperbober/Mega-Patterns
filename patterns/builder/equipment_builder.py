from __future__ import annotations
from abc import ABC, abstractmethod
from domain.equipment import Equipment, BaseSoftware


class EquipmentBuilder(ABC):
    @abstractmethod
    def reset(self) -> None: ...
    @abstractmethod
    def set_type(self, equipment_type: str) -> None: ...
    @abstractmethod
    def add_spec(self, key: str, value) -> None: ...
    @abstractmethod
    def add_function(self, func: str) -> None: ...
    @abstractmethod
    def set_software(self, title: str) -> None: ...
    @abstractmethod
    def build(self) -> Equipment: ...


class ConcreteEquipmentBuilder(EquipmentBuilder):
    def __init__(self) -> None:
        self._equipment: Equipment | None = None
        self.reset()

    def reset(self) -> None:
        self._equipment = Equipment(
            equipment_type="(not set)",
            specs={},
            functions=[],
            software=BaseSoftware("Base Software"),
        )

    def set_type(self, equipment_type: str) -> None:
        assert self._equipment is not None
        self._equipment.equipment_type = equipment_type

    def add_spec(self, key: str, value) -> None:
        assert self._equipment is not None
        self._equipment.specs[key] = value

    def add_function(self, func: str) -> None:
        assert self._equipment is not None
        self._equipment.functions.append(func)

    def set_software(self, title: str) -> None:
        assert self._equipment is not None
        self._equipment.software = BaseSoftware(title)

    def build(self) -> Equipment:
        assert self._equipment is not None
        result = self._equipment
        self.reset()  # можно собирать следующий объект тем же builder’ом
        return result


class Director:
    """Знает последовательности сборки типовых конфигураций."""
    def __init__(self, builder: EquipmentBuilder) -> None:
        self._builder = builder

    def make_bike(self) -> Equipment:
        self._builder.reset()
        self._builder.set_type("Велотренажёр")
        self._builder.add_spec("max_resistance", 20)
        self._builder.add_spec("has_pulse_sensor", True)
        self._builder.add_function("Тренировка по пульсу")
        self._builder.add_function("Интервалы")
        self._builder.set_software("Bike Software")
        return self._builder.build()

    def make_treadmill(self) -> Equipment:
        self._builder.reset()
        self._builder.set_type("Беговая дорожка")
        self._builder.add_spec("max_speed_kmh", 18)
        self._builder.add_spec("incline_levels", 12)
        self._builder.add_function("Бег")
        self._builder.add_function("Ходьба")
        self._builder.add_function("Горка")
        self._builder.set_software("Treadmill Software")
        return self._builder.build()

    def make_rowing(self) -> Equipment:
        self._builder.reset()
        self._builder.set_type("Гребной тренажёр")
        self._builder.add_spec("max_power_watts", 600)
        self._builder.add_spec("resistance_system", "magnetic")
        self._builder.add_function("Гребля")
        self._builder.add_function("Кардио")
        self._builder.add_function("Интервалы")
        self._builder.set_software("Rowing Software")
        return self._builder.build()
