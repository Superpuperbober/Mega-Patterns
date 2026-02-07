import tkinter as tk
from tkinter import ttk, messagebox

from patterns.factory import FactoryRegistry, BikeFactory, TreadmillFactory, RowingMachineFactory
from patterns.decorator import OnlineSoftwareDecorator, AnalyticsDecorator
from patterns.Proxy import SoftwareProxy
from patterns.memento import EquipmentMemento, Caretaker

from domain.equipment import Equipment,BaseSoftware


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
        self.caretaker = Caretaker()
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

    def _build_memento_tab(self) -> None:
        ttk.Label(
            self.tab_memento,
            text="Memento: сохраняем снимки конфигурации и делаем Undo/Redo.",
        ).pack(anchor="w")

        controls = ttk.Frame(self.tab_memento)
        controls.pack(anchor="w", pady=10)

        ttk.Button(controls, text="Сохранить снимок", command=self.save_snapshot).pack(side="left", padx=4)
        ttk.Button(controls, text="Undo", command=self.undo_snapshot).pack(side="left", padx=4)
        ttk.Button(controls, text="Redo", command=self.redo_snapshot).pack(side="left", padx=4)

        ttk.Separator(self.tab_memento).pack(fill="x", pady=10)

        self.memento_output = tk.Text(self.tab_memento, wrap="word", height=18)
        self.memento_output.pack(fill="both", expand=True)

        self.refresh_memento_tab()

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

        eq = self.current_equipment
        eq.base_software_title = eq.software.name()  # базовое ПО от Builder
        eq.use_online = False
        eq.use_analytics = False
        eq.use_proxy = False
        eq.license_key = ""
        self.rebuild_software_from_state()

        # сбрасываем историю и сохраняем первый снимок
        self.caretaker = Caretaker()
        self.caretaker.backup(self.create_memento_from_current())
        if hasattr(self, "refresh_memento_tab"):
            self.refresh_memento_tab()


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

        eq = self.current_equipment
        eq.use_online = bool(self.var_online.get())
        eq.use_analytics = bool(self.var_analytics.get())

        self.rebuild_software_from_state()
        self.refresh_decorator_tab()
        if hasattr(self, "refresh_memento_tab"):
            self.refresh_memento_tab()

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

        eq = self.current_equipment

        # если галочка не стоит — выключаем прокси в состоянии и пересобираем ПО
        if not self.var_use_proxy.get():
            eq.use_proxy = False
            eq.license_key = ""
            self.rebuild_software_from_state()
            self.proxy_output.insert("1.0", "Proxy выключен. ПО восстановлено без Proxy.")
            self.refresh_decorator_tab()
            if hasattr(self, "refresh_memento_tab"):
                self.refresh_memento_tab()
            return

        # если галочка стоит — включаем прокси и сохраняем ключ
        eq.use_proxy = True
        eq.license_key = self.license_entry.get().strip()

        self.rebuild_software_from_state()

        self.proxy_output.insert(
            "1.0",
            f"Proxy включён.\n"
            f"License key: {eq.license_key}\n\n"
            f"Текущее ПО: {eq.software.name()}\n"
            f"Подсказка: нажми 'Вызвать operation()' чтобы увидеть проверку/ленивую загрузку.\n",
        )

        self.refresh_decorator_tab()
        if hasattr(self, "refresh_memento_tab"):
            self.refresh_memento_tab()

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

    def create_memento_from_current(self) -> EquipmentMemento:
        eq = self.current_equipment
        assert eq is not None

        # Важно: specs и functions копируем, чтобы снимок не менялся при дальнейших правках
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

        # синхронизируем GUI-флажки тоже
        self.var_online.set(eq.use_online)
        self.var_analytics.set(eq.use_analytics)
        if hasattr(self, "var_use_proxy"):
            self.var_use_proxy.set(eq.use_proxy)
        if hasattr(self, "license_entry"):
            self.license_entry.delete(0, "end")
            self.license_entry.insert(0, eq.license_key)

        # обновим вывод
        self.factory_output.delete("1.0", "end")
        self.factory_output.insert("1.0", eq.summary())
        self.refresh_builder_tab()
        self.refresh_decorator_tab()
        if hasattr(self, "refresh_memento_tab"):
            self.refresh_memento_tab()

    def refresh_memento_tab(self) -> None:
        if not hasattr(self, "memento_output"):
            return
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

    def save_snapshot(self) -> None:
        if not self.current_equipment:
            messagebox.showwarning("Нет объекта", "Сначала создай тренажёр.")
            return
        m = self.create_memento_from_current()
        self.caretaker.backup(m)
        self.refresh_memento_tab()

    def undo_snapshot(self) -> None:
        if not self.current_equipment:
            return
        m = self.caretaker.undo()
        if m is None:
            messagebox.showinfo("Undo", "Больше некуда откатываться.")
            return
        self.restore_from_memento(m)

    def redo_snapshot(self) -> None:
        if not self.current_equipment:
            return
        m = self.caretaker.redo()
        if m is None:
            messagebox.showinfo("Redo", "Больше некуда возвращаться.")
            return
        self.restore_from_memento(m)


if __name__ == "__main__":
    App().mainloop()
