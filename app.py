import tkinter as tk
from tkinter import ttk, messagebox

from patterns.factory import FactoryRegistry, BikeFactory, TreadmillFactory, RowingMachineFactory
from patterns.decorator import OnlineSoftwareDecorator, AnalyticsDecorator
from patterns.Proxy import SoftwareProxy
from domain.equipment import Equipment


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Trainer Software — Patterns Demo (Factory + Builder + Decorator)")
        self.geometry("820x560")

        # Текущий созданный тренажёр (один объект “живёт” между вкладками)
        self.current_equipment: Equipment | None = None

        # Реестр фабрик
        self.registry = FactoryRegistry()
        self.registry.register("bike", BikeFactory())
        self.registry.register("treadmill", TreadmillFactory())
        self.registry.register("rowing", RowingMachineFactory())

        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        ttk.Label(
            root,
            text="Демонстрация паттернов в одной системе: Factory → Builder → Decorator",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_factory = ttk.Frame(self.notebook, padding=10)
        self.tab_builder = ttk.Frame(self.notebook, padding=10)
        self.tab_decorator = ttk.Frame(self.notebook, padding=10)
        self.tab_proxy = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_factory, text="1) Factory")
        self.notebook.add(self.tab_builder, text="2) Builder")
        self.notebook.add(self.tab_decorator, text="3) Decorator")
        self.notebook.add(self.tab_proxy, text="4) Proxy")

        self._build_factory_tab()
        self._build_builder_tab()
        self._build_decorator_tab()
        self._build_proxy_tab()

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
            text="Важно: GUI не создаёт Equipment напрямую — он просит фабрику create().",
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
            text="Добавляй возможности ПО динамически (Decorator):",
        ).pack(anchor="w")

        controls = ttk.Frame(self.tab_decorator)
        controls.pack(anchor="w", pady=10)

        self.var_online = tk.BooleanVar(value=False)
        self.var_analytics = tk.BooleanVar(value=False)

        ttk.Checkbutton(controls, text="Online", variable=self.var_online).pack(side="left", padx=(0, 12))
        ttk.Checkbutton(controls, text="Analytics", variable=self.var_analytics).pack(side="left", padx=(0, 12))

        ttk.Button(controls, text="Применить (Decorator)", command=self.apply_decorators).pack(side="left", padx=4)
        ttk.Button(controls, text="Сбросить ПО к базовому", command=self.reset_software).pack(side="left", padx=4)

        ttk.Separator(self.tab_decorator).pack(fill="x", pady=10)

        self.decorator_output = tk.Text(self.tab_decorator, wrap="word", height=18)
        self.decorator_output.pack(fill="both", expand=True)

        ttk.Label(
            self.tab_decorator,
            text="Важно: расширение делается без наследования — объект ПО оборачивается в декораторы.",
            foreground="#444",
        ).pack(anchor="w", pady=(8, 0))

    def _build_proxy_tab(self) -> None:
        ttk.Label(
            self.tab_proxy,
            text="Proxy: доступ к ПО через проверку лицензии и ленивую загрузку.",
        ).pack(anchor="w")

        controls = ttk.Frame(self.tab_proxy)
        controls.pack(anchor="w", pady=10)

        self.var_use_proxy = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls, text="Использовать Proxy для ПО", variable=self.var_use_proxy).pack(
            side="left", padx=(0, 12)
        )

        ttk.Label(controls, text="License key:").pack(side="left")
        self.license_entry = ttk.Entry(controls, width=20)
        self.license_entry.insert(0, "VALID-KEY")  # для удобства
        self.license_entry.pack(side="left", padx=8)

        ttk.Button(controls, text="Применить Proxy", command=self.apply_proxy).pack(side="left", padx=4)
        ttk.Button(controls, text="Вызвать operation()", command=self.run_software_operation).pack(side="left", padx=4)

        ttk.Separator(self.tab_proxy).pack(fill="x", pady=10)

        self.proxy_output = tk.Text(self.tab_proxy, wrap="word", height=18)
        self.proxy_output.pack(fill="both", expand=True)

        ttk.Label(
            self.tab_proxy,
            text="Идея: GUI/система работает с ISoftware, а Proxy скрывает проверку/загрузку.",
            foreground="#444",
        ).pack(anchor="w", pady=(8, 0))

    # ---------------- Logic ----------------
    def on_create(self) -> None:
        key = self.selected_key.get()
        try:
            factory = self.registry.get(key)
        except KeyError:
            messagebox.showerror("Ошибка", f"Неизвестный ключ фабрики: {key}")
            return

        self.current_equipment = factory.create()  # внутри уже Builder собирает объект
        self.var_online.set(False)
        self.var_analytics.set(False)

        self.factory_output.delete("1.0", "end")
        self.factory_output.insert("1.0", self.current_equipment.summary())

        # сразу обновим остальные вкладки
        self.refresh_builder_tab()
        self.refresh_decorator_tab()

        # сброс proxy-UI
        if hasattr(self, "var_use_proxy"):
            self.var_use_proxy.set(False)
        if hasattr(self, "proxy_output"):
            self.proxy_output.delete("1.0", "end")

    def on_clear(self) -> None:
        self.current_equipment = None
        self.factory_output.delete("1.0", "end")
        self.builder_output.delete("1.0", "end")
        self.decorator_output.delete("1.0", "end")

    def refresh_builder_tab(self) -> None:
        self.builder_output.delete("1.0", "end")
        if not self.current_equipment:
            self.builder_output.insert("1.0", "Сначала создай тренажёр во вкладке Factory.")
            return

        log = self.current_equipment.build_log or ["(лог сборки пуст)"]
        text = "Лог Builder:\n" + "\n".join(f"- {line}" for line in log)
        self.builder_output.insert("1.0", text)

    def refresh_decorator_tab(self) -> None:
        self.decorator_output.delete("1.0", "end")
        if not self.current_equipment:
            self.decorator_output.insert("1.0", "Сначала создай тренажёр во вкладке Factory.")
            return
        self.decorator_output.insert("1.0", self.current_equipment.summary())

    def apply_decorators(self) -> None:
        if not self.current_equipment:
            messagebox.showwarning("Нет объекта", "Сначала создай тренажёр во вкладке Factory.")
            return

        base = self.current_equipment.base_software or self.current_equipment.software
        software = base

        if self.var_online.get():
            software = OnlineSoftwareDecorator(software)
        if self.var_analytics.get():
            software = AnalyticsDecorator(software)

        self.current_equipment.software = software
        self.refresh_decorator_tab()

    def reset_software(self) -> None:
        if not self.current_equipment:
            return
        # Просто пересоздадим объект через фабрику по текущему ключу, чтобы вернуть базовую конфигурацию
        # (так честно: базу задаёт Builder)
        key = self.selected_key.get()
        factory = self.registry.get(key)
        self.current_equipment = factory.create()
        self.var_online.set(False)
        self.var_analytics.set(False)

        self.factory_output.delete("1.0", "end")
        self.factory_output.insert("1.0", self.current_equipment.summary())

        self.refresh_builder_tab()
        self.refresh_decorator_tab()

    def apply_proxy(self) -> None:
        self.proxy_output.delete("1.0", "end")

        if not self.current_equipment:
            self.proxy_output.insert("1.0", "Сначала создай тренажёр во вкладке Factory.")
            return

        if not self.var_use_proxy.get():
            self.proxy_output.insert("1.0", "Proxy выключен (галочка не установлена).")
            return

        # Берём текущее ПО (оно может быть уже с декораторами)
        current_title = self.current_equipment.software.name()
        proxy = SoftwareProxy(title=current_title, required_license="VALID-KEY")

        key = self.license_entry.get().strip()
        proxy.set_license(key)

        # Важно: заменяем ПО на прокси
        self.current_equipment.software = proxy

        self.proxy_output.insert("1.0", f"Proxy применён поверх ПО: {proxy.name()}\nЛицензия установлена: {key}\n")

    def run_software_operation(self) -> None:
        self.proxy_output.delete("1.0", "end")

        if not self.current_equipment:
            self.proxy_output.insert("1.0", "Сначала создай тренажёр во вкладке Factory.")
            return

        software = self.current_equipment.software
        result = software.operation()

        # если это наш прокси — покажем внутренний лог
        if isinstance(software, SoftwareProxy):
            log_text = "\n".join(f"- {x}" for x in software.log) if software.log else "(лог пуст)"
            text = (
                f"software.name(): {software.name()}\n\n"
                f"Результат operation():\n{result}\n\n"
                f"Лог Proxy:\n{log_text}"
            )
        else:
            text = (
                "Текущее ПО НЕ является Proxy.\n"
                "Перейди в Proxy-вкладку, включи галочку и нажми 'Применить Proxy'.\n\n"
                f"software.name(): {software.name()}\n\n"
                f"Результат operation():\n{result}"
            )

        self.proxy_output.insert("1.0", text)

if __name__ == "__main__":
    App().mainloop()
