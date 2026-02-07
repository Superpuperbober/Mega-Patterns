from __future__ import annotations
from abc import ABC, abstractmethod

from domain.equipment import Equipment
from patterns.builder import ConcreteEquipmentBuilder, Director


class EquipmentFactory(ABC):
    @abstractmethod
    def create(self) -> Equipment:
        raise NotImplementedError


class BikeFactory(EquipmentFactory):
    def create(self) -> Equipment:
        director = Director(ConcreteEquipmentBuilder())
        return director.make_bike()


class TreadmillFactory(EquipmentFactory):
    def create(self) -> Equipment:
        director = Director(ConcreteEquipmentBuilder())
        return director.make_treadmill()


class RowingMachineFactory(EquipmentFactory):
    def create(self) -> Equipment:
        director = Director(ConcreteEquipmentBuilder())
        return director.make_rowing()


class FactoryRegistry:
    """Реестр фабрик: GUI работает с ключами и интерфейсом фабрики."""
    def __init__(self) -> None:
        self._factories: dict[str, EquipmentFactory] = {}

    def register(self, key: str, factory: EquipmentFactory) -> None:
        self._factories[key] = factory

    def keys(self) -> list[str]:
        return list(self._factories.keys())

    def get(self, key: str) -> EquipmentFactory:
        return self._factories[key]
