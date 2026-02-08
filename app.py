import tkinter as tk
from tkinter import ttk, messagebox

from patterns.factory import FactoryRegistry, BikeFactory, TreadmillFactory, RowingMachineFactory
from patterns.decorator import OnlineSoftwareDecorator, AnalyticsDecorator
from patterns.proxy import SoftwareProxy

from patterns.memento import EquipmentMemento, Caretaker

from patterns.state import SystemState, EditState, ViewState

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
        self.title("Trainer Software — Patterns Demo (Factory+Builder+Decorator+Proxy+State+Memento+Command)")
        self.geometry("980x680")

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

        # State: режим системы (по документу)
        self._editing_enabled: bool = True
        self.system_state: SystemState = EditState(self)

        # UI
        self._editable_widgets: list[tk.Widget] = []
        self._build_ui()

        # применяем состояние сразу
        self.system_state.show_funcs()

    # ---------------- UI ----------------
    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        # верхняя панель: переключение режимов (State)
        topbar = ttk.Frame(root)
        topbar.pack(fill="x", pady=(0, 8))

        ttk.Label(
            topbar,
            text="Factory → Builder → Decorator → Proxy → State(Edit/View) → Memento (+ Command)",
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")

        ttk.Button(topbar, text="EDIT", command=lambda: self.set_state(EditState)).pack(side="right", padx=4)
        ttk.Button(topbar, text="VIEW", command=lambda: self.set_state(ViewState)).pack(side="right", padx=4)

        self.status_label = ttk.Label(root, text="", foreground="#444")
        self.status_label.pack(anchor="w", pady=(0, 10))

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
        self.notebook.add(self.tab_memento, text="5) Memento + Command")

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
        self.type_combo = ttk.Combobox(
            row,
            textvariable=self.selected_key,
            values=self.registry.keys(),
            state="readonly",
            width=20,
        )
        self.type_combo.pack(side="left", padx=8)

        btn_create = ttk.Button(row, text="Создать (Factory)", command=self.on_create)
        btn_create.pack(side="left", padx=4)
        self._editable_widgets.append(btn_create)
        self._editable_widgets.append(self.type_combo)

        btn_clear = ttk.Button(row, text="Очистить", command=self.on_clear)
        btn_clear.pack(side="left", padx=4)
        # очистку оставим доступной всегда

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

        self.cb_online = ttk.Checkbutton(controls, text="Online", variable=self.var_online)
        self.cb_online.pack(side="left", padx=(0, 12))
        self._editable_widgets.append(self.cb_online)

        self.cb_analytics = ttk.Checkbutton(controls, text="Analytics", variable=self.var_analytics)
        self.cb_analytics.pack(side="left", padx=(0, 12))
        self._editable_widgets.append(self.cb_analytics)

        btn_apply = ttk.Button(controls, text="Применить (Command)", command=self.on_apply_decorators_click)
        btn_apply.pack(side="left", padx=4)
        self._editable_widgets.append(btn_apply)

        btn_reset = ttk.Button(controls, text="Сбросить к базе", command=self.reset_software)
        btn_reset.pack(side="left", padx=4)
        self._editable_widgets.append(btn_reset)

        ttk.Separator(self.tab_decorator).pack(fill="x", pady=10)

        self.decorator_output = tk.Text(self.tab_decorator, wrap="word", height=18)
        self.decorator_output.pack(fill="both", expand=True)

    def _build_proxy_tab(self) -> None:
        ttk.Label(self.tab_proxy, text="Proxy: лицензия + ленивый доступ к ПО.").pack(anchor="w")

        top = ttk.Frame(self.tab_proxy)
        top.pack(anchor="w", pady=10)

        self.var_use_proxy = tk.BooleanVar(value=False)
        self.cb_proxy = ttk.Checkbutton(top, text="Использовать Proxy", variable=self.var_use_proxy)
        self.cb_proxy.pack(side="left", padx=(0, 12))
        self._editable_widgets.append(self.cb_proxy)

        ttk.Label(top, text="License key:").pack(side="left")
        self.license_entry = ttk.Entry(top, width=20)
        self.license_entry.insert(0, "VALID-KEY")
        self.license_entry.pack(side="left", padx=8)
        self._editable_widgets.append(self.license_entry)

        btn_apply_proxy = ttk.Button(top, text="Применить Proxy (Command)", command=self.on_apply_proxy_click)
        btn_apply_proxy.pack(side="left", padx=4)
        self._editable_widgets.append(btn_apply_proxy)

        # operation разрешим даже в VIEW (просмотр)
        ttk.Button(top, text="Вызвать operation()", command=self.run_software_operation).pack(side="left", padx=4)

        ttk.Separator(self.tab_proxy).pack(fill="x", pady=10)

        self.proxy_output = tk.Text(self.tab_proxy, wrap="word", height=18)
        self.proxy_output.pack(fill="both", expand=True)

    def _build_memento_tab(self) -> None:
        ttk.Label(self.tab_memento, text="Memento + Command: снимки, Undo/Redo.").pack(anchor="w")

        controls = ttk.Frame(self.tab_memento)
        controls.pack(anchor="w", pady=10)

        self.btn_save_snapshot = ttk.Button(
            controls, text="Сохранить снимок", command=lambda: self.invoker.execute("save_snapshot")
        )
        self.btn_save_snapshot.pack(side="left", padx=4)
        self._editable_widgets.append(self.btn_save_snapshot)

        self.btn_undo = ttk.Button(controls, text="Undo", command=lambda: self.invoker.execute("undo"))
        self.btn_undo.pack(side="left", padx=4)
        self._editable_widgets.append(self.btn_undo)

        self.btn_redo = ttk.Button(controls, text="Redo", command=lambda: self.invoker.execute("redo"))
        self.btn_redo.pack(side="left", padx=4)
        self._editable_widgets.append(self.btn_redo)

        ttk.Separator(self.tab_memento).pack(fill="x", pady=10)

        self.memento_output = tk.Text(self.tab_memento, wrap="word", height=18)
        self.memento_output.pack(fill="both", expand=True)

        self.refresh_memento_tab()

    # ---------------- State (как в документе) ----------------
    def set_state(self, state_cls: type[SystemState]) -> None:
        self.system_state = state_cls(self)
        self.system_state.show_funcs()

    def enable_editing(self, enabled: bool) -> None:
        self._editing_enabled = enabled
        state = "normal" if enabled else "disabled"
        for w in self._editable_widgets:
            try:
                w.configure(state=state)
            except tk.TclError:
                pass

    def set_status(self, text: str) -> None:
        self.status_label.configure(text=text)

    # ---------------- Build software chain (без StatefulSoftware!) ----------------
    def rebuild_software_from_flags(self) -> None:
        """
        Собираем цепочку (как раньше):
        BaseSoftware -> Decorators -> Proxy
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
        if not self._editing_enabled:
            messagebox.showinfo("VIEW режим", "В режиме VIEW создание/изменения запрещены.")
            return

        key = self.selected_key.get()
        try:
            factory = self.registry.get(key)
        except KeyError:
            messagebox.showerror("Ошибка", f"Неизвестный ключ фабрики: {key}")
            return

        self.current_equipment = factory.create()

        eq = self.current_equipment
        # флаги расширений
        self.var_online.set(False)
        self.var_analytics.set(False)
        self.var_use_proxy.set(False)
        self.license_entry.delete(0, "end")
        self.license_entry.insert(0, "VALID-KEY")

        eq.use_online = False
        eq.use_analytics = False
        eq.use_proxy = False
        eq.license_key = ""

        # база от builder
        eq.base_software_title = eq.software.name()

        self.rebuild_software_from_flags()
        self.refresh_all()

        # новый caretaker + первый снимок
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
        if not self._editing_enabled:
            messagebox.showinfo("VIEW режим", "В режиме VIEW изменения запрещены.")
            return
        if not self.current_equipment:
            messagebox.showwarning("Нет объекта", "Сначала создай тренажёр.")
            return
        cmd = ApplyDecoratorsCommand(self, online=bool(self.var_online.get()), analytics=bool(self.var_analytics.get()))
        cmd.execute()

    def on_apply_proxy_click(self) -> None:
        if not self._editing_enabled:
            messagebox.showinfo("VIEW режим", "В режиме VIEW изменения запрещены.")
            return
        if not self.current_equipment:
            messagebox.showwarning("Нет объекта", "Сначала создай тренажёр.")
            return
        enabled = bool(self.var_use_proxy.get())
        key = self.license_entry.get().strip()
        cmd = ApplyProxyCommand(self, enabled=enabled, license_key=key)
        cmd.execute()

        self.proxy_output.delete("1.0", "end")
        self.proxy_output.insert("1.0", f"Proxy applied: enabled={enabled}, key='{key}'\n")

    def reset_software(self) -> None:
        if not self._editing_enabled:
            messagebox.showinfo("VIEW режим", "В режиме VIEW изменения запрещены.")
            return
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

        self.rebuild_software_from_flags()
        self.refresh_all()

        self.caretaker = Caretaker()
        self.caretaker.backup(self.create_memento_from_current())
        self.refresh_memento_tab()

    # ---------------- Proxy demo ----------------
    def run_software_operation(self) -> None:
        self.proxy_output.delete("1.0", "end")
        if not self.current_equipment:
            self.proxy_output.insert("1.0", "Сначала создай тренажёр.")
            return

        software = self.current_equipment.software
        result = software.operation()

        proxy_log = ""
        if isinstance(software, SoftwareProxy):
            log_text = "\n".join(f"- {x}" for x in getattr(software, "log", [])) or "(лог пуст)"
            proxy_log = f"\n\nЛог Proxy:\n{log_text}"

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

        # sync ui
        self.var_online.set(eq.use_online)
        self.var_analytics.set(eq.use_analytics)
        self.var_use_proxy.set(eq.use_proxy)
        self.license_entry.delete(0, "end")
        self.license_entry.insert(0, eq.license_key or "VALID-KEY")

        self.rebuild_software_from_flags()

    def refresh_memento_tab(self) -> None:
        self.memento_output.delete("1.0", "end")
        if not self.current_equipment:
            self.memento_output.insert("1.0", "Сначала создай тренажёр.")
            return

        eq = self.current_equipment
        self.memento_output.insert(
            "1.0",
            f"{self.caretaker.info()}\n\n"
            f"Текущее состояние:\n"
            f"- base_software_title: {eq.base_software_title}\n"
            f"- online: {eq.use_online}\n"
            f"- analytics: {eq.use_analytics}\n"
            f"- proxy: {eq.use_proxy}\n"
            f"- license_key: {eq.license_key}\n\n"
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
        if not self._editing_enabled:
            messagebox.showinfo("VIEW режим", "В режиме VIEW изменения запрещены.")
            return
        self.caretaker.backup(snapshot)
        self.refresh_memento_tab()

    def undo_snapshot(self):
        if not self._editing_enabled:
            messagebox.showinfo("VIEW режим", "В режиме VIEW изменения запрещены.")
            return None
        return self.caretaker.undo()

    def redo_snapshot(self):
        if not self._editing_enabled:
            messagebox.showinfo("VIEW режим", "В режиме VIEW изменения запрещены.")
            return None
        return self.caretaker.redo()

    def refresh_all(self) -> None:
        if self.current_equipment:
            self.factory_output.delete("1.0", "end")
            self.factory_output.insert("1.0", self.current_equipment.summary())
        self.refresh_builder_tab()
        self.refresh_decorator_tab()
        self.refresh_memento_tab()

    def set_decorators_state(self, online: bool, analytics: bool) -> None:
        if not self._editing_enabled:
            return
        eq = self.current_equipment
        if not eq:
            return
        eq.use_online = online
        eq.use_analytics = analytics
        self.var_online.set(online)
        self.var_analytics.set(analytics)
        self.rebuild_software_from_flags()
        self.refresh_all()

    def set_proxy_state(self, enabled: bool, license_key: str) -> None:
        if not self._editing_enabled:
            return
        eq = self.current_equipment
        if not eq:
            return
        eq.use_proxy = enabled
        eq.license_key = license_key
        self.var_use_proxy.set(enabled)
        self.license_entry.delete(0, "end")
        self.license_entry.insert(0, license_key or "VALID-KEY")
        self.rebuild_software_from_flags()
        self.refresh_all()


if __name__ == "__main__":
    App().mainloop()
