import tkinter as tk
from tkinter import ttk, messagebox

from patterns.factory import FactoryRegistry, BikeFactory, TreadmillFactory, RowingMachineFactory
from patterns.decorator import OnlineSoftwareDecorator, AnalyticsDecorator
from patterns.Proxy import SoftwareProxy
from patterns.memento import EquipmentMemento, Caretaker

from patterns.command import (
    Invoker,
    ApplyDecoratorsCommand,
    ApplyProxyCommand,
    SaveSnapshotCommand,
    UndoCommand,
    RedoCommand,
)

from domain.equipment import EquipmentModel, BaseSoftware


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Trainer Software — Patterns Demo (Factory + Builder + Decorator + Proxy + Memento + Command)")
        self.geometry("920x600")

        # Текущий созданный тренажёр (один объект “живёт” между вкладками)
        self.current_equipment: EquipmentModel | None = None


        # реестр фабрик
        self.registry = FactoryRegistry()
        self.registry.register("bike", BikeFactory())
        self.registry.register("treadmill", TreadmillFactory())
        self.registry.register("rowing", RowingMachineFactory())

        # caretaker (memento)
        self.caretaker = Caretaker()

        # invoker (command) — ВАЖНО: до построения UI
        self.invoker = Invoker()
        self.invoker.register("save_snapshot", SaveSnapshotCommand(self))
        self.invoker.register("undo", UndoCommand(self))
        self.invoker.register("redo", RedoCommand(self))

        # строим интерфейс
        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        ttk.Label(
            root,
            text="Демонстрация: Factory → Builder → Decorator → Proxy → Memento (+ Command)",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_factory = ttk.Frame(self.notebook, padding=10)
        self.tab_builder = ttk.Frame(self.notebook, padding=10)
        self.tab_decorator = ttk.Frame(self.notebook, padding=10)
        self.tab_proxy = ttk.Frame(self.notebook, padding=10)
        self.tab_memento = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_factory, text="1) Factory")
        self.notebook.add(self.tab_builder, text="2) Builder")
        self.notebook.add(self.tab_decorator, text="3) Decorator")
        self.notebook.add(self.tab_proxy, text="4) Proxy")
        self.notebook.add(self.tab_memento, text="5) Memento")

        self._build_factory_tab()
        self._build_builder_tab()
        self._build_decorator_tab()
        self._build_proxy_tab()
        self._build_memento_tab()

    def _build_factory_tab(self) -> None:
        ttk.Label(self.tab_factory, text="Выбери тип тренажёра и создай объект через фабрику:").pack(anchor="w")

        row = ttk.Frame(self.tab_factory)
        row.pack(anchor="w", pady=10)

        ttk.Label(row, text="Тип:").pack(side="left")
        self.selected_key = tk.StringVar(value=self.registry.keys()[0])
        ttk.Combobox(
            row,
            textvariable=self.selected_key,
            values=self.registry.keys(),
            state="readonly",
            width=20,
        ).pack(side="left", padx=8)

        ttk.Button(row, text="Создать (Factory)", command=self.on_create).pack(side="left", padx=4)
        ttk.Button(row, text="Очистить", command=self.on_clear).pack(side="left", padx=4)

        ttk.Separator(self.tab_factory).pack(fill="x", pady=10)

        self.factory_output = tk.Text(self.tab_factory, wrap="word", height=18)
        self.factory_output.pack(fill="both", expand=True)

        ttk.Label(
            self.tab_factory,
            text="GUI не создаёт Equipment напрямую — он просит фабрику create().",
            foreground="#444",
        ).pack(anchor="w", pady=(8, 0))

    def _build_builder_tab(self) -> None:
        ttk.Label(
            self.tab_builder,
            text="Здесь видно, как Builder собирал объект (лог шагов сборки).",
        ).pack(anchor="w")

        ttk.Button(self.tab_builder, text="Показать лог сборки (Builder)", command=self.refresh_builder_tab).pack(
            anchor="w", pady=10
        )

        self.builder_output = tk.Text(self.tab_builder, wrap="word", height=22)
        self.builder_output.pack(fill="both", expand=True)

    def _build_decorator_tab(self) -> None:
        ttk.Label(
            self.tab_decorator,
            text="Decorator: добавляй возможности ПО динамически (через Command сохраняем состояние в Memento).",
        ).pack(anchor="w")

        controls = ttk.Frame(self.tab_decorator)
        controls.pack(anchor="w", pady=10)

        self.var_online = tk.BooleanVar(value=False)
        self.var_analytics = tk.BooleanVar(value=False)

        ttk.Checkbutton(controls, text="Online", variable=self.var_online).pack(side="left", padx=(0, 12))
        ttk.Checkbutton(controls, text="Analytics", variable=self.var_analytics).pack(side="left", padx=(0, 12))

        ttk.Button(controls, text="Применить (Command)", command=self.on_apply_decorators_click).pack(side="left", padx=4)
        ttk.Button(controls, text="Сбросить ПО к базовому", command=self.reset_software).pack(side="left", padx=4)

        ttk.Separator(self.tab_decorator).pack(fill="x", pady=10)

        self.decorator_output = tk.Text(self.tab_decorator, wrap="word", height=18)
        self.decorator_output.pack(fill="both", expand=True)

        ttk.Label(
            self.tab_decorator,
            text="Важно: мы не наращиваем бесконечные обёртки — пересобираем ПО по флагам состояния.",
            foreground="#444",
        ).pack(anchor="w", pady=(8, 0))

    def _build_proxy_tab(self) -> None:
        ttk.Label(
            self.tab_proxy,
            text="Proxy: проверка лицензии + ленивая загрузка реального модуля.",
        ).pack(anchor="w")

        controls = ttk.Frame(self.tab_proxy)
        controls.pack(anchor="w", pady=10)

        self.var_use_proxy = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls, text="Использовать Proxy для ПО", variable=self.var_use_proxy).pack(
            side="left", padx=(0, 12)
        )

        ttk.Label(controls, text="License key:").pack(side="left")
        self.license_entry = ttk.Entry(controls, width=20)
        self.license_entry.insert(0, "VALID-KEY")
        self.license_entry.pack(side="left", padx=8)

        ttk.Button(controls, text="Применить Proxy (Command)", command=self.on_apply_proxy_click).pack(side="left", padx=4)
        ttk.Button(controls, text="Вызвать operation()", command=self.run_software_operation).pack(side="left", padx=4)

        ttk.Separator(self.tab_proxy).pack(fill="x", pady=10)

        self.proxy_output = tk.Text(self.tab_proxy, wrap="word", height=18)
        self.proxy_output.pack(fill="both", expand=True)

        ttk.Label(
            self.tab_proxy,
            text="Идея: система работает с ISoftware, а Proxy скрывает проверку/загрузку.",
            foreground="#444",
        ).pack(anchor="w", pady=(8, 0))

    def _build_memento_tab(self) -> None:
        ttk.Label(
            self.tab_memento,
            text="Memento: сохраняем снимки конфигурации и делаем Undo/Redo (через Command+Invoker).",
        ).pack(anchor="w")

        controls = ttk.Frame(self.tab_memento)
        controls.pack(anchor="w", pady=10)

        ttk.Button(
            controls,
            text="Сохранить снимок (Command)",
            command=lambda: self.invoker.execute("save_snapshot"),
        ).pack(side="left", padx=4)

        ttk.Button(
            controls,
            text="Undo (Command)",
            command=lambda: self.invoker.execute("undo"),
        ).pack(side="left", padx=4)

        ttk.Button(
            controls,
            text="Redo (Command)",
            command=lambda: self.invoker.execute("redo"),
        ).pack(side="left", padx=4)

        ttk.Separator(self.tab_memento).pack(fill="x", pady=10)

        self.memento_output = tk.Text(self.tab_memento, wrap="word", height=18)
        self.memento_output.pack(fill="both", expand=True)

        self.refresh_memento_tab()

    # ---------------- helpers: rebuild software ----------------
    def rebuild_software_from_state(self) -> None:
        """
        Пересобирает self.current_equipment.software по сохранённым флагам.
        """
        eq = self.current_equipment
        if not eq:
            return

        software = BaseSoftware(eq.base_software_title)

        if eq.use_online:
            software = OnlineSoftwareDecorator(software)
        if eq.use_analytics:
            software = AnalyticsDecorator(software)
        if eq.use_proxy:
            proxy = SoftwareProxy(title=software.name(), required_license="VALID-KEY")
            proxy.set_license(eq.license_key)
            software = proxy

        eq.software = software

    # ---------------- Logic ----------------
    def on_create(self) -> None:
        key = self.selected_key.get()
        try:
            factory = self.registry.get(key)
        except KeyError:
            messagebox.showerror("Ошибка", f"Неизвестный ключ фабрики: {key}")
            return

        self.current_equipment = factory.create()

        # сброс UI-флагов
        self.var_online.set(False)
        self.var_analytics.set(False)
        if hasattr(self, "var_use_proxy"):
            self.var_use_proxy.set(False)
        if hasattr(self, "license_entry"):
            self.license_entry.delete(0, "end")
            self.license_entry.insert(0, "VALID-KEY")

        # инициализация состояния ПО для memento
        eq = self.current_equipment
        eq.base_software_title = eq.software.name()
        eq.use_online = False
        eq.use_analytics = False
        eq.use_proxy = False
        eq.license_key = ""

        self.rebuild_software_from_state()

        # вывод
        self.factory_output.delete("1.0", "end")
        self.factory_output.insert("1.0", eq.summary())
        self.refresh_builder_tab()
        self.refresh_decorator_tab()

        if hasattr(self, "proxy_output"):
            self.proxy_output.delete("1.0", "end")

        # сбрасываем историю и сохраняем первый снимок
        self.caretaker = Caretaker()
        self.caretaker.backup(self.create_memento_from_current())
        self.refresh_memento_tab()

    def on_clear(self) -> None:
        self.current_equipment = None
        self.factory_output.delete("1.0", "end")
        self.builder_output.delete("1.0", "end")
        self.decorator_output.delete("1.0", "end")
        self.proxy_output.delete("1.0", "end")
        self.memento_output.delete("1.0", "end")

    def refresh_builder_tab(self) -> None:
        self.builder_output.delete("1.0", "end")
        if not self.current_equipment:
            self.builder_output.insert("1.0", "Сначала создай тренажёр во вкладке Factory.")
            return

        log = getattr(self.current_equipment, "build_log", None) or ["(лог сборки пуст)"]
        text = "Лог Builder:\n" + "\n".join(f"- {line}" for line in log)
        self.builder_output.insert("1.0", text)

    def refresh_decorator_tab(self) -> None:
        self.decorator_output.delete("1.0", "end")
        if not self.current_equipment:
            self.decorator_output.insert("1.0", "Сначала создай тренажёр во вкладке Factory.")
            return
        self.decorator_output.insert("1.0", self.current_equipment.summary())

    # ---------------- Command handlers ----------------
    def on_apply_decorators_click(self) -> None:
        if not self.current_equipment:
            messagebox.showwarning("Нет объекта", "Сначала создай тренажёр во вкладке Factory.")
            return

        cmd = ApplyDecoratorsCommand(
            self,
            online=bool(self.var_online.get()),
            analytics=bool(self.var_analytics.get()),
        )
        cmd.execute()

    def on_apply_proxy_click(self) -> None:
        if not self.current_equipment:
            messagebox.showwarning("Нет объекта", "Сначала создай тренажёр во вкладке Factory.")
            return

        enabled = bool(self.var_use_proxy.get())
        key = self.license_entry.get().strip()

        cmd = ApplyProxyCommand(self, enabled=enabled, license_key=key)
        cmd.execute()

        # чуть-чуть текста в Proxy вкладку
        self.proxy_output.delete("1.0", "end")
        self.proxy_output.insert(
            "1.0",
            f"Proxy state applied: enabled={enabled}, license='{key}'.\n"
            f"Текущее ПО: {self.current_equipment.software.name()}",
        )

    def reset_software(self) -> None:
        """
        Сброс к базовой конфигурации: пересоздаём объект через фабрику.
        (Так честно: базу задаёт Builder.)
        """
        if not self.current_equipment:
            return

        key = self.selected_key.get()
        factory = self.registry.get(key)
        self.current_equipment = factory.create()

        eq = self.current_equipment
        eq.base_software_title = eq.software.name()
        eq.use_online = False
        eq.use_analytics = False
        eq.use_proxy = False
        eq.license_key = ""

        self.var_online.set(False)
        self.var_analytics.set(False)
        self.var_use_proxy.set(False)
        self.license_entry.delete(0, "end")
        self.license_entry.insert(0, "VALID-KEY")

        self.rebuild_software_from_state()
        self.refresh_all()

        # новый “первый” снимок
        self.caretaker = Caretaker()
        self.caretaker.backup(self.create_memento_from_current())
        self.refresh_memento_tab()

    # ---------------- Proxy demo ----------------
    def run_software_operation(self) -> None:
        self.proxy_output.delete("1.0", "end")

        if not self.current_equipment:
            self.proxy_output.insert("1.0", "Сначала создай тренажёр во вкладке Factory.")
            return

        software = self.current_equipment.software
        result = software.operation()

        if isinstance(software, SoftwareProxy):
            log_text = "\n".join(f"- {x}" for x in software.log) if getattr(software, "log", None) else "(лог пуст)"
            text = (
                f"software.name(): {software.name()}\n\n"
                f"Результат operation():\n{result}\n\n"
                f"Лог Proxy:\n{log_text}"
            )
        else:
            text = (
                "Текущее ПО НЕ является Proxy.\n"
                "Включи галочку и нажми 'Применить Proxy (Command)'.\n\n"
                f"software.name(): {software.name()}\n\n"
                f"Результат operation():\n{result}"
            )

        self.proxy_output.insert("1.0", text)

    # ---------------- Memento ----------------
    def create_memento_from_current(self) -> EquipmentMemento:
        eq = self.current_equipment
        assert eq is not None

        return EquipmentMemento(
            equipment_type=eq.equipment_type,
            specs=dict(eq.specs),
            functions=list(eq.functions),
            base_software_title=eq.base_software_title,
            use_online=eq.use_online,
            use_analytics=eq.use_analytics,
            use_proxy=eq.use_proxy,
            license_key=eq.license_key,
        )

    def restore_from_memento(self, m: EquipmentMemento) -> None:
        eq = self.current_equipment
        assert eq is not None

        eq.equipment_type = m.equipment_type
        eq.specs = dict(m.specs)
        eq.functions = list(m.functions)

        eq.base_software_title = m.base_software_title
        eq.use_online = m.use_online
        eq.use_analytics = m.use_analytics
        eq.use_proxy = m.use_proxy
        eq.license_key = m.license_key

        self.rebuild_software_from_state()

        # синхронизируем GUI
        self.var_online.set(eq.use_online)
        self.var_analytics.set(eq.use_analytics)
        self.var_use_proxy.set(eq.use_proxy)
        self.license_entry.delete(0, "end")
        self.license_entry.insert(0, eq.license_key or "VALID-KEY")

    def refresh_memento_tab(self) -> None:
        self.memento_output.delete("1.0", "end")

        if not self.current_equipment:
            self.memento_output.insert("1.0", "Сначала создай тренажёр во вкладке Factory.")
            return

        eq = self.current_equipment
        text = (
            f"{self.caretaker.info()}\n\n"
            f"Текущее состояние:\n"
            f"- base_software_title: {eq.base_software_title}\n"
            f"- online: {eq.use_online}\n"
            f"- analytics: {eq.use_analytics}\n"
            f"- proxy: {eq.use_proxy}\n"
            f"- license_key: {eq.license_key}\n\n"
            f"Краткий вывод:\n{eq.summary()}"
        )
        self.memento_output.insert("1.0", text)

    # ---------------- AppContext API for Commands ----------------
    def has_equipment(self) -> bool:
        return self.current_equipment is not None

    def get_snapshot(self):
        return self.create_memento_from_current()

    def restore_snapshot(self, snapshot):
        if not self.current_equipment:
            return
        self.restore_from_memento(snapshot)

    def push_snapshot(self, snapshot):
        self.caretaker.backup(snapshot)

    def undo_snapshot(self):
        return self.caretaker.undo()

    def redo_snapshot(self):
        return self.caretaker.redo()

    def refresh_all(self) -> None:
        if self.current_equipment:
            self.factory_output.delete("1.0", "end")
            self.factory_output.insert("1.0", self.current_equipment.summary())
        self.refresh_builder_tab()
        self.refresh_decorator_tab()
        self.refresh_memento_tab()

    def set_decorators_state(self, online: bool, analytics: bool) -> None:
        eq = self.current_equipment
        if not eq:
            return
        eq.use_online = online
        eq.use_analytics = analytics
        self.var_online.set(online)
        self.var_analytics.set(analytics)
        self.rebuild_software_from_state()

    def set_proxy_state(self, enabled: bool, license_key: str) -> None:
        eq = self.current_equipment
        if not eq:
            return
        eq.use_proxy = enabled
        eq.license_key = license_key
        self.var_use_proxy.set(enabled)
        self.license_entry.delete(0, "end")
        self.license_entry.insert(0, license_key or "VALID-KEY")
        self.rebuild_software_from_state()


if __name__ == "__main__":
    App().mainloop()
