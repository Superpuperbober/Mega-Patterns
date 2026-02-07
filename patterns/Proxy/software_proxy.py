from __future__ import annotations
import time
from typing import Optional, List
from domain.equipment import ISoftware


class ProtectedRemoteSoftware:
    """
    Это "реальный объект" (RealSubject).
    Представь, что он тяжёлый, грузится/инициализируется долго и работает с сетью.
    """
    def __init__(self, title: str, load_seconds: float = 1.2) -> None:
        self._title = title
        self._load_seconds = load_seconds
        # имитация тяжёлой инициализации
        time.sleep(self._load_seconds)

    def name(self) -> str:
        return self._title

    def operation(self) -> str:
        return "Реальный модуль ПО выполнен (тяжёлая логика/сеть/драйверы)."


class SoftwareProxy:
    """
    Proxy: контролирует доступ и лениво создаёт реальный объект.
    """
    def __init__(self, title: str, required_license: str = "VALID-KEY") -> None:
        self._title = title
        self._required_license = required_license
        self._real: Optional[ISoftware] = None
        self.log: List[str] = []

    def set_license(self, key: str) -> None:
        self._license_key = key
        self.log.append(f"set_license({key})")

    def name(self) -> str:
        return f"{self._title} (via Proxy)"

    def _check_access(self) -> bool:
        key = getattr(self, "_license_key", "")
        ok = key == self._required_license
        self.log.append(f"check_access() -> {'OK' if ok else 'DENIED'}")
        return ok

    def _ensure_real_loaded(self) -> None:
        if self._real is None:
            self.log.append("lazy_load() -> начинаю загрузку реального ПО")
            self._real = ProtectedRemoteSoftware(self._title)
            self.log.append("lazy_load() -> реальное ПО загружено")

    def operation(self) -> str:
        if not self._check_access():
            return "Доступ запрещён: неверная лицензия."
        self._ensure_real_loaded()
        assert self._real is not None
        self.log.append("delegate.operation() -> передаю управление реальному объекту")
        return self._real.operation()
