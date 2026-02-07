import tkinter as tk
from tkinter import ttk, messagebox

from patterns.factory import FactoryRegistry, BikeFactory, TreadmillFactory, RowingMachineFactory
from patterns.decorator import OnlineSoftwareDecorator, AnalyticsDecorator
from patterns.proxy import SoftwareProxy

from patterns.memento import EquipmentMemento, Caretaker
from patterns.state import StatefulSoftware, SetupState, IdleState, TrainingState, LockedState

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
        self.title("Trainer Software — Patterns Demo (Factory+Builder+Decorator+proxy+State+Memento+Command)")
        self.geometry("980x650")

        self.current_equipment: EquipmentModel | None = None

        # factory registry
        self.registry = FactoryRegistry()
        self.registry.register("bike", BikeFactory())
        self.registry.register("treadmill", TreadmillFactory())
        self.registry.register("rowing", RowingMachineFactory())

        # memento caretaker
        self.caretaker = Caretaker()

        # invoker
        self.invoker = Invoker()
        self.invoker.register("save_snapshot", SaveSnapshotCommand(self))
        self.invoker.register("undo", UndoCommand(self))
        self.invoker.register("redo", RedoCommand(self))

        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        ttk.Label(
            root,
            text="Factory → Builder → Decorator → proxy → State → Memento (+ Command)",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_factory = ttk.Frame(self.notebook, padding=10)
        self.tab_builder = ttk.Frame(self.notebook, padding=10)
        self.tab_decorator = ttk.Frame(self.notebook, padding=10)
        self.tab_proxy_state = ttk.Frame(self.notebook, padding=10)
        self.tab_memento = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_factory, text="1) Factory")
        self.notebook.add(self.tab_builder, text="2) Builder")
        self.notebook.add(self.tab_decorator, text="3) Decorator")
        self.notebook.add(self.tab_proxy_state, text="4) proxy + State")
        self.notebook.add(self.tab_memento, text="5) Memento + Command")

        self._build_factory_tab()
        self._build_builder_tab()
        self._build_decorator_tab()
        self._build_proxy_state_tab()
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

    def _build_builder_tab(self) -> None:
        ttk.Label(self.tab_builder, text="Лог Builder (шаги сборки):").pack(anchor="w")
        ttk.Button(self.tab_builder, text="Показать лог", command=self.refresh_builder_tab).pack(anchor="w", pady=10)

        self.builder_output = tk.Text(self.tab_builder, wrap="word", height=22)
        self.builder_output.pack(fill="both", expand=True)

    def _build_decorator_tab(self) -> None:
        ttk.Label(self.tab_decorator, text="Decorator: включай модули ПО (через Command):").pack(anchor="w")

        controls = ttk.Frame(self.tab_decorator)
        controls.pack(anchor="w", pady=10)

        self.var_online = tk.BooleanVar(value=False)
        self.var_analytics = tk.BooleanVar(value=False)

        ttk.Checkbutton(controls, text="Online", variable=self.var_online).pack(side="left", padx=(0, 12))
        ttk.Checkbutton(controls, text="Analytics", variable=self.var_analytics).pack(side="left", padx=(0, 12))

        ttk.Button(controls, text="Применить (Command)", command=self.on_apply_decorators_click).pack(side="left", padx=4)
        ttk.Button(controls, text="Сбросить к базе", command=self.reset_software).pack(side="left", padx=4)

        ttk.Separator(self.tab_decorator).pack(fill="x", pady=10)

        self.decorator_output = tk.Text(self.tab_decorator, wrap="word", height=18)
        self.decorator_output.pack(fill="both", expand=True)

    def _build_proxy_state_tab(self) -> None:
        ttk.Label(self.tab_proxy_state, text="proxy + State: лицензия + режимы ПО.").pack(anchor="w")

        top = ttk.Frame(self.tab_proxy_state)
        top.pack(anchor="w", pady=10)

        # proxy controls
        self.var_use_proxy = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="Использовать proxy", variable=self.var_use_proxy).pack(side="left", padx=(0, 12))

        ttk.Label(top, text="License key:").pack(side="left")
        self.license_entry = ttk.Entry(top, width=20)
        self.license_entry.insert(0, "VALID-KEY")
        self.license_entry.pack(side="left", padx=8)

        ttk.Button(top, text="Применить proxy (Command)", command=self.on_apply_proxy_click).pack(side="left", padx=4)
        ttk.Button(top, text="Вызвать operation()", command=self.run_software_operation).pack(side="left", padx=4)

        # state controls
        state_row = ttk.Frame(self.tab_proxy_state)
        state_row.pack(anchor="w", pady=(10, 0))

        ttk.Label(state_row, text="State режим:").pack(side="left", padx=(0, 8))
        ttk.Button(state_row, text="SETUP", command=lambda: self.set_software_state("SETUP")).pack(side="left", padx=4)
        ttk.Button(state_row, text="IDLE", command=lambda: self.set_software_state("IDLE")).pack(side="left", padx=4)
        ttk.Button(state_row, text="TRAINING", command=lambda: self.set_software_state("TRAINING")).pack(side="left", padx=4)

        ttk.Separator(self.tab_proxy_state).pack(fill="x", pady=10)

        self.proxy_output = tk.Text(self.tab_proxy_state, wrap="word", height=18)
        self.proxy_output.pack(fill="both", expand=True)

    def _build_memento_tab(self) -> None:
        ttk.Label(self.tab_memento, text="Memento + Command: снимки, Undo/Redo.").pack(anchor="w")

        controls = ttk.Frame(self.tab_memento)
        controls.pack(anchor="w", pady=10)

        ttk.Button(controls, text="Сохранить снимок", command=lambda: self.invoker.execute("save_snapshot")).pack(side="left", padx=4)
        ttk.Button(controls, text="Undo", command=lambda: self.invoker.execute("undo")).pack(side="left", padx=4)
        ttk.Button(controls, text="Redo", command=lambda: self.invoker.execute("redo")).pack(side="left", padx=4)

        ttk.Separator(self.tab_memento).pack(fill="x", pady=10)

        self.memento_output = tk.Text(self.tab_memento, wrap="word", height=18)
        self.memento_output.pack(fill="both", expand=True)

        self.refresh_memento_tab()

    # ---------------- Software chain builder ----------------
    def _state_obj_from_name(self, name: str):
        name = (name or "").upper()
        if name == "SETUP":
            return SetupState()
        if name == "TRAINING":
            return TrainingState()
        if name == "LOCKED":
            return LockedState()
        return IdleState()

    def rebuild_software_from_state(self) -> None:
        """
        Собираем цепочку:
        BaseSoftware -> Decorators -> proxy -> StatefulSoftware
        """
        eq = self.current_equipment
        if not eq:
            return

        # 1) base
        software = BaseSoftware(eq.base_software_title)

        # 2) decorators
        if eq.use_online:
            software = OnlineSoftwareDecorator(software)
        if eq.use_analytics:
            software = AnalyticsDecorator(software)

        # 3) proxy
        if eq.use_proxy:
            proxy = SoftwareProxy(title=software.name(), required_license="VALID-KEY")
            proxy.set_license(eq.license_key)
            software = proxy

        # 4) state wrapper on top
        stateful = StatefulSoftware(software)

        # auto-lock if proxy enabled and key empty
        if eq.use_proxy and not eq.license_key:
            eq.software_state_name = "LOCKED"
        stateful.set_state(self._state_obj_from_name(getattr(eq, "software_state_name", "IDLE")))

        eq.software = stateful

    # ---------------- Logic ----------------
    def on_create(self) -> None:
        key = self.selected_key.get()
        try:
            factory = self.registry.get(key)
        except KeyError:
            messagebox.showerror("Ошибка", f"Неизвестный ключ фабрики: {key}")
            return

        self.current_equipment = factory.create()

        # init flags
        eq = self.current_equipment
        self.var_online.set(False)
        self.var_analytics.set(False)
        self.var_use_proxy.set(False)
        self.license_entry.delete(0, "end")
        self.license_entry.insert(0, "VALID-KEY")

        eq.use_online = False
        eq.use_analytics = False
        eq.use_proxy = False
        eq.license_key = ""
        eq.software_state_name = "IDLE"

        # base_software_title comes from builder-created software name
        eq.base_software_title = eq.software.name()

        self.rebuild_software_from_state()
        self.refresh_all()

        # reset caretaker + first snapshot
        self.caretaker = Caretaker()
        self.caretaker.backup(self.create_memento_from_current())
        self.refresh_memento_tab()

        self.proxy_output.delete("1.0", "end")

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
            self.builder_output.insert("1.0", "Сначала создай тренажёр.")
            return
        log = getattr(self.current_equipment, "build_log", None) or ["(лог сборки пуст)"]
        self.builder_output.insert("1.0", "Лог Builder:\n" + "\n".join(f"- {x}" for x in log))

    def refresh_decorator_tab(self) -> None:
        self.decorator_output.delete("1.0", "end")
        if not self.current_equipment:
            self.decorator_output.insert("1.0", "Сначала создай тренажёр.")
            return
        self.decorator_output.insert("1.0", self.current_equipment.summary())

    # ---------------- Command handlers ----------------
    def on_apply_decorators_click(self) -> None:
        if not self.current_equipment:
            messagebox.showwarning("Нет объекта", "Сначала создай тренажёр.")
            return
        cmd = ApplyDecoratorsCommand(self, online=bool(self.var_online.get()), analytics=bool(self.var_analytics.get()))
        cmd.execute()

    def on_apply_proxy_click(self) -> None:
        if not self.current_equipment:
            messagebox.showwarning("Нет объекта", "Сначала создай тренажёр.")
            return
        enabled = bool(self.var_use_proxy.get())
        key = self.license_entry.get().strip()
        cmd = ApplyProxyCommand(self, enabled=enabled, license_key=key)
        cmd.execute()
        self.proxy_output.delete("1.0", "end")
        self.proxy_output.insert("1.0", f"proxy applied: enabled={enabled}, key='{key}'\n")

    # ---------------- State UI ----------------
    def set_software_state(self, state_name: str) -> None:
        if not self.current_equipment:
            messagebox.showwarning("Нет объекта", "Сначала создай тренажёр.")
            return
        eq = self.current_equipment
        # если LOCKED — ручное переключение запрещаем (можно разрешить, но так логичнее)
        if eq.use_proxy and not eq.license_key:
            eq.software_state_name = "LOCKED"
        else:
            eq.software_state_name = state_name.upper()

        self.rebuild_software_from_state()
        self.refresh_all()

    def reset_software(self) -> None:
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
        eq.software_state_name = "IDLE"

        self.var_online.set(False)
        self.var_analytics.set(False)
        self.var_use_proxy.set(False)
        self.license_entry.delete(0, "end")
        self.license_entry.insert(0, "VALID-KEY")

        self.rebuild_software_from_state()
        self.refresh_all()

        self.caretaker = Caretaker()
        self.caretaker.backup(self.create_memento_from_current())
        self.refresh_memento_tab()

    def run_software_operation(self) -> None:
        self.proxy_output.delete("1.0", "end")
        if not self.current_equipment:
            self.proxy_output.insert("1.0", "Сначала создай тренажёр.")
            return

        software = self.current_equipment.software
        result = software.operation()

        # показать лог proxy если он внутри (может быть wrapped)
        proxy_log = ""
        # попробуем достать прокси изнутри (если StatefulSoftware хранит wrapped в поле _wrapped)
        wrapped = getattr(software, "_wrapped", None)
        if isinstance(wrapped, SoftwareProxy):
            log_text = "\n".join(f"- {x}" for x in getattr(wrapped, "log", [])) or "(лог пуст)"
            proxy_log = f"\n\nЛог proxy:\n{log_text}"

        self.proxy_output.insert(
            "1.0",
            f"software.name(): {software.name()}\n\n"
            f"operation():\n{result}"
            f"{proxy_log}",
        )

    # ---------------- Memento ----------------
    def create_memento_from_current(self) -> EquipmentMemento:
        eq = self.current_equipment
        assert eq is not None
        # добавляем software_state_name как поле в specs? лучше прямо в memento если можно.
        # Если твой EquipmentMemento пока без этого поля — добавь туда software_state_name.
        return EquipmentMemento(
            equipment_type=eq.equipment_type,
            specs=dict(eq.specs),
            functions=list(eq.functions),
            base_software_title=eq.base_software_title,
            use_online=eq.use_online,
            use_analytics=eq.use_analytics,
            use_proxy=eq.use_proxy,
            license_key=eq.license_key,
            software_state_name=getattr(eq, "software_state_name", "IDLE"),
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
        eq.software_state_name = getattr(m, "software_state_name", "IDLE")

        self.var_online.set(eq.use_online)
        self.var_analytics.set(eq.use_analytics)
        self.var_use_proxy.set(eq.use_proxy)
        self.license_entry.delete(0, "end")
        self.license_entry.insert(0, eq.license_key or "VALID-KEY")

        self.rebuild_software_from_state()

    def refresh_memento_tab(self) -> None:
        self.memento_output.delete("1.0", "end")
        if not self.current_equipment:
            self.memento_output.insert("1.0", "Сначала создай тренажёр.")
            return

        eq = self.current_equipment
        self.memento_output.insert(
            "1.0",
            f"{self.caretaker.info()}\n\n"
            f"State:\n"
            f"- base_software_title: {eq.base_software_title}\n"
            f"- online: {eq.use_online}\n"
            f"- analytics: {eq.use_analytics}\n"
            f"- proxy: {eq.use_proxy}\n"
            f"- license_key: {eq.license_key}\n"
            f"- software_state_name: {getattr(eq, 'software_state_name', 'IDLE')}\n\n"
            f"Summary:\n{eq.summary()}",
        )

    # ---------------- AppContext API for Commands ----------------
    def has_equipment(self) -> bool:
        return self.current_equipment is not None

    def get_snapshot(self):
        return self.create_memento_from_current()

    def restore_snapshot(self, snapshot):
        if not self.current_equipment:
            return
        self.restore_from_memento(snapshot)
        self.refresh_all()

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
