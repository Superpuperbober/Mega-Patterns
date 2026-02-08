import tkinter as tk
from tkinter import ttk, messagebox

from patterns.factory import FactoryRegistry, BikeFactory, TreadmillFactory, RowingMachineFactory
from patterns.decorator import OnlineSoftwareDecorator, AnalyticsDecorator
from patterns.proxy import SoftwareProxy
from patterns.memento import EquipmentMemento, Caretaker

# State (как в документе)
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
        self.title("Mega-Patterns — Trainer Software Control Panel")
        self.geometry("1200x740")
        self.minsize(1500, 1000)


        self.COL = {
            "bg": "#0f172a",          # slate-900
            "panel": "#111827",       # gray-900
            "card": "#0b1220",
            "text": "#e5e7eb",        # gray-200
            "muted": "#9ca3af",       # gray-400
            "border": "#1f2937",      # gray-800
            "factory": "#60a5fa",     # blue-400
            "builder": "#c084fc",     # purple-400
            "decorator": "#34d399",   # green-400
            "proxy": "#fb923c",       # orange-400
            "memento": "#22d3ee",     # cyan-400
            "state": "#a3a3a3",       # neutral-400
            "error": "#f87171",       # red-400
            "success": "#4ade80",     # green-300
            "warn": "#fbbf24",        # amber-400
        }


        self.current_equipment: EquipmentModel | None = None

        # Composite catalog (тип -> список моделей)
        self._catalog: dict[str, list[EquipmentModel]] = {}
        self._tree_type_nodes: dict[str, str] = {}
        self._tree_model_nodes: dict[int, str] = {}


        self._snapshot_list: list[EquipmentMemento] = []


        self.registry = FactoryRegistry()
        self.registry.register("bike", BikeFactory())
        self.registry.register("treadmill", TreadmillFactory())
        self.registry.register("rowing", RowingMachineFactory())

        self.caretaker = Caretaker()


        self.invoker = Invoker()
        self.invoker.register("save_snapshot", SaveSnapshotCommand(self))
        self.invoker.register("undo", UndoCommand(self))
        self.invoker.register("redo", RedoCommand(self))


        self._editing_enabled: bool = True
        self.system_state: SystemState = EditState(self)



        self._editable_widgets: list[tk.Widget] = []


        self._apply_ttk_theme()

        # Build UI
        self._build_ui()
        self.system_state.show_funcs()
        self.refresh_all()


    def _apply_ttk_theme(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=self.COL["bg"])
        style.configure("TLabelframe", background=self.COL["bg"], foreground=self.COL["text"])
        style.configure("TLabelframe.Label", background=self.COL["bg"], foreground=self.COL["text"])
        style.configure("TLabel", background=self.COL["bg"], foreground=self.COL["text"])
        style.configure("TButton", padding=7)
        style.configure("TCheckbutton", background=self.COL["bg"], foreground=self.COL["text"])
        style.map("TCheckbutton", foreground=[("disabled", self.COL["muted"])])
        style.configure("TCombobox", padding=4)


    def _build_ui(self) -> None:
        self.configure(bg=self.COL["bg"])

        # Header
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill="x")

        title = ttk.Label(
            header,
            text="Trainer Software — Patterns Demo Dashboard",
            font=("Segoe UI", 15, "bold"),
        )
        title.pack(side="left")

        ttk.Button(header, text="EDIT", command=lambda: self.set_state(EditState)).pack(side="right", padx=4)
        ttk.Button(header, text="VIEW", command=lambda: self.set_state(ViewState)).pack(side="right", padx=4)


        self.status_label = tk.Label(
            self,
            text="",
            bg=self.COL["bg"],
            fg=self.COL["muted"],
            anchor="w",
            padx=12,
        )
        self.status_label.pack(fill="x")


        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        body.columnconfigure(0, weight=0)
        body.columnconfigure(1, weight=1)
        body.columnconfigure(2, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_left_controls(body)
        self._build_center_info(body)
        self._build_right_panel(body)

        # Bottom bar
        self.bottom_bar = tk.Label(
            self,
            text="",
            bg=self.COL["bg"],
            fg=self.COL["muted"],
            anchor="w",
            padx=12,
            pady=6,
        )
        self.bottom_bar.pack(fill="x")

    def _card(self, parent: ttk.Frame, title: str) -> ttk.Labelframe:
        lf = ttk.Labelframe(parent, text=title, padding=10)
        lf.pack(fill="x", pady=8)
        return lf


    def _build_left_controls(self, parent: ttk.Frame) -> None:
        left = ttk.Frame(parent)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        # FACTORY
        c1 = self._card(left, "1) Factory")
        ttk.Label(c1, text="Тип тренажёра:").pack(anchor="w")

        self.selected_key = tk.StringVar(value=self.registry.keys()[0])
        self.combo_type = ttk.Combobox(
            c1, textvariable=self.selected_key, values=self.registry.keys(), state="readonly", width=18
        )
        self.combo_type.pack(anchor="w", pady=(4, 8))
        self._editable_widgets.append(self.combo_type)

        btn_create = ttk.Button(c1, text="Create Equipment", command=self.on_create)
        btn_create.pack(fill="x")
        self._editable_widgets.append(btn_create)

        ttk.Button(c1, text="Clear current", command=self.on_clear).pack(fill="x", pady=(6, 0))


        c2 = self._card(left, "2) Builder")
        ttk.Label(c2, text="Лог шагов сборки:").pack(anchor="w")
        ttk.Button(c2, text="Show Builder Log", command=self.show_builder_log).pack(fill="x", pady=(6, 0))


        c3 = self._card(left, "3) Decorator")
        self.var_online = tk.BooleanVar(value=False)
        self.var_analytics = tk.BooleanVar(value=False)

        cb1 = ttk.Checkbutton(c3, text="Online module", variable=self.var_online)
        cb1.pack(anchor="w")
        cb2 = ttk.Checkbutton(c3, text="Analytics module", variable=self.var_analytics)
        cb2.pack(anchor="w")

        self._editable_widgets.extend([cb1, cb2])

        btn_apply_dec = ttk.Button(c3, text="Apply Decorators (Command)", command=self.on_apply_decorators_click)
        btn_apply_dec.pack(fill="x", pady=(8, 0))
        self._editable_widgets.append(btn_apply_dec)

        btn_reset = ttk.Button(c3, text="Reset to Base", command=self.reset_software)
        btn_reset.pack(fill="x", pady=(6, 0))
        self._editable_widgets.append(btn_reset)


        c4 = self._card(left, "4) Proxy")
        self.var_use_proxy = tk.BooleanVar(value=False)
        cbp = ttk.Checkbutton(c4, text="Enable Proxy", variable=self.var_use_proxy)
        cbp.pack(anchor="w")
        self._editable_widgets.append(cbp)

        ttk.Label(c4, text="License key:").pack(anchor="w", pady=(6, 0))
        self.license_entry = ttk.Entry(c4)
        self.license_entry.insert(0, "VALID-KEY")
        self.license_entry.pack(fill="x", pady=(2, 6))
        self._editable_widgets.append(self.license_entry)

        btn_apply_proxy = ttk.Button(c4, text="Apply Proxy (Command)", command=self.on_apply_proxy_click)
        btn_apply_proxy.pack(fill="x")
        self._editable_widgets.append(btn_apply_proxy)

        ttk.Button(c4, text="Run operation()", command=self.run_software_operation).pack(fill="x", pady=(6, 0))


        c5 = self._card(left, "5) Memento")
        btn_save = ttk.Button(c5, text="Save Snapshot", command=lambda: self.invoker.execute("save_snapshot"))
        btn_undo = ttk.Button(c5, text="Undo", command=lambda: self.invoker.execute("undo"))
        btn_redo = ttk.Button(c5, text="Redo", command=lambda: self.invoker.execute("redo"))

        btn_save.pack(fill="x")
        btn_undo.pack(fill="x", pady=(6, 0))
        btn_redo.pack(fill="x", pady=(6, 0))

        self._editable_widgets.extend([btn_save, btn_undo, btn_redo])


    def _build_center_info(self, parent: ttk.Frame) -> None:
        center = ttk.Frame(parent)
        center.grid(row=0, column=1, sticky="nsew", padx=(0, 10))
        center.rowconfigure(0, weight=1)
        center.rowconfigure(1, weight=1)
        center.rowconfigure(2, weight=1)
        center.columnconfigure(0, weight=1)


        eq_card = ttk.Labelframe(center, text="Current Equipment (Product)", padding=10)
        eq_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        eq_card.rowconfigure(0, weight=1)
        eq_card.columnconfigure(0, weight=1)

        self.txt_equipment = tk.Text(eq_card, wrap="word", bg=self.COL["panel"], fg=self.COL["text"], insertbackground=self.COL["text"])
        self.txt_equipment.grid(row=0, column=0, sticky="nsew")


        sw_card = ttk.Labelframe(center, text="Software chain (Decorator/Proxy)", padding=10)
        sw_card.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        sw_card.rowconfigure(0, weight=1)
        sw_card.columnconfigure(0, weight=1)

        self.txt_software = tk.Text(sw_card, wrap="word", bg=self.COL["panel"], fg=self.COL["text"], insertbackground=self.COL["text"])
        self.txt_software.grid(row=0, column=0, sticky="nsew")


        mem_card = ttk.Labelframe(center, text="Memento (Snapshots)", padding=10)
        mem_card.grid(row=2, column=0, sticky="nsew")
        mem_card.rowconfigure(0, weight=1)
        mem_card.columnconfigure(0, weight=1)

        top = ttk.Frame(mem_card)
        top.grid(row=0, column=0, sticky="nsew")
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=1)
        top.rowconfigure(0, weight=1)


        left_box = ttk.Frame(top)
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_box.rowconfigure(1, weight=1)
        left_box.columnconfigure(0, weight=1)

        ttk.Label(left_box, text="Snapshots list:").grid(row=0, column=0, sticky="w")

        self.lst_snapshots = tk.Listbox(
            left_box,
            height=6,
            bg=self.COL["panel"],
            fg=self.COL["text"],
            selectbackground=self.COL["memento"],
            selectforeground="#000000",
            highlightthickness=1,
            highlightbackground=self.COL["border"],
        )
        self.lst_snapshots.grid(row=1, column=0, sticky="nsew")
        self.lst_snapshots.bind("<<ListboxSelect>>", self._on_snapshot_select)

        btn_restore = ttk.Button(left_box, text="Restore selected", command=self.restore_selected_snapshot)
        btn_restore.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        self._editable_widgets.append(btn_restore)


        right_box = ttk.Frame(top)
        right_box.grid(row=0, column=1, sticky="nsew")
        right_box.rowconfigure(1, weight=1)
        right_box.columnconfigure(0, weight=1)

        ttk.Label(right_box, text="Selected snapshot details:").grid(row=0, column=0, sticky="w")

        self.txt_memento = tk.Text(
            right_box,
            wrap="word",
            height=6,
            bg=self.COL["panel"],
            fg=self.COL["text"],
            insertbackground=self.COL["text"],
        )
        self.txt_memento.grid(row=1, column=0, sticky="nsew")

        self.lbl_memento_info = tk.Label(mem_card, text="", bg=self.COL["bg"], fg=self.COL["muted"], anchor="w")
        self.lbl_memento_info.grid(row=1, column=0, sticky="w", pady=(8, 0))


    def _build_right_panel(self, parent: ttk.Frame) -> None:
        right = ttk.Frame(parent)
        right.grid(row=0, column=2, sticky="nsew")
        right.rowconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)


        comp_card = ttk.Labelframe(right, text="Composite Catalog (Type → Models)", padding=10)
        comp_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        comp_card.rowconfigure(0, weight=1)
        comp_card.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(comp_card, columns=("kind",), show="tree headings")
        self.tree.heading("#0", text="Hierarchy")
        self.tree.heading("kind", text="Node type")
        self.tree.column("kind", width=90, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", self._on_tree_double_click)


        self.tree.tag_configure("TYPE", foreground=self.COL["factory"])
        self.tree.tag_configure("MODEL", foreground=self.COL["text"])


        log_card = ttk.Labelframe(right, text="Action Log (colored)", padding=10)
        log_card.grid(row=1, column=0, sticky="nsew")
        log_card.rowconfigure(0, weight=1)
        log_card.columnconfigure(0, weight=1)

        self.txt_log = tk.Text(log_card, wrap="word", bg=self.COL["panel"], fg=self.COL["text"], insertbackground=self.COL["text"])
        self.txt_log.grid(row=0, column=0, sticky="nsew")


        self.txt_log.tag_config("FACTORY", foreground=self.COL["factory"])
        self.txt_log.tag_config("BUILDER", foreground=self.COL["builder"])
        self.txt_log.tag_config("DECORATOR", foreground=self.COL["decorator"])
        self.txt_log.tag_config("PROXY", foreground=self.COL["proxy"])
        self.txt_log.tag_config("MEMENTO", foreground=self.COL["memento"])
        self.txt_log.tag_config("STATE", foreground=self.COL["state"])
        self.txt_log.tag_config("WARN", foreground=self.COL["warn"])
        self.txt_log.tag_config("ERROR", foreground=self.COL["error"])
        self.txt_log.tag_config("OK", foreground=self.COL["success"])


    def log(self, text: str, tag: str = "STATE") -> None:
        self.txt_log.insert("end", text + "\n", (tag,))
        self.txt_log.see("end")


    def set_state(self, state_cls: type[SystemState]) -> None:
        self.system_state = state_cls(self)
        self.system_state.show_funcs()
        self.log(f"[STATE] -> {self.system_state.name()}", "STATE")
        self.refresh_bottom_bar()

    def edit(self):
        self.state.edit(self)

    def view(self):
        self.state.view(self)

    def enable_editing(self, enabled: bool) -> None:
        self._editing_enabled = enabled
        state = "normal" if enabled else "disabled"
        for w in self._editable_widgets:
            try:
                w.configure(state=state)
            except tk.TclError:
                pass

    def set_status(self, text: str) -> None:
        # color status line based on mode
        mode = self.system_state.name() if self.system_state else "?"
        if mode.upper() == "EDIT":
            fg = self.COL["success"]
        else:
            fg = self.COL["warn"]
        self.status_label.configure(text=text, fg=fg)


    def rebuild_software_from_flags(self) -> None:
        """BaseSoftware -> Decorators -> Proxy"""
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

    def software_chain_text(self) -> str:
        eq = self.current_equipment
        if not eq:
            return "Нет созданного тренажёра."

        chain = [f"BaseSoftware('{eq.base_software_title}')"]
        if eq.use_online:
            chain.append("OnlineDecorator")
        if eq.use_analytics:
            chain.append("AnalyticsDecorator")
        if eq.use_proxy:
            chain.append(f"Proxy(license='{eq.license_key}')")

        return (
            "Цепочка обёрток:\n"
            + "  -> ".join(chain)
            + "\n\n"
            + f"software.name(): {eq.software.name()}\n"
            + "Подсказка: нажми 'Run operation()' чтобы увидеть поведение."
        )

    def _add_to_catalog(self, model: EquipmentModel) -> None:
        eq_type = getattr(model, "equipment_type", "") or "UnknownType"
        self._catalog.setdefault(eq_type, [])
        if all(id(x) != id(model) for x in self._catalog[eq_type]):
            self._catalog[eq_type].append(model)
        self._rebuild_tree()

    def _rebuild_tree(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        self._tree_type_nodes.clear()
        self._tree_model_nodes.clear()

        for eq_type in sorted(self._catalog.keys()):
            type_id = self.tree.insert("", "end", text=eq_type, values=("TYPE",), tags=("TYPE",))
            self._tree_type_nodes[eq_type] = type_id

            for m in self._catalog[eq_type]:
                label = f"{getattr(m, 'name', 'Model')}  (software: {m.software.name()})"
                mid = self.tree.insert(type_id, "end", text=label, values=("MODEL",), tags=("MODEL",))
                self._tree_model_nodes[id(m)] = mid

        for t in self._tree_type_nodes.values():
            self.tree.item(t, open=True)

    def _on_tree_double_click(self, _event) -> None:
        item_id = self.tree.focus()
        if not item_id:
            return
        values = self.tree.item(item_id, "values")
        if not values or values[0] != "MODEL":
            return

        for eq_type, models in self._catalog.items():
            for m in models:
                if self._tree_model_nodes.get(id(m)) == item_id:
                    self.current_equipment = m

                    self.var_online.set(bool(getattr(m, "use_online", False)))
                    self.var_analytics.set(bool(getattr(m, "use_analytics", False)))
                    self.var_use_proxy.set(bool(getattr(m, "use_proxy", False)))
                    self.license_entry.delete(0, "end")
                    self.license_entry.insert(0, getattr(m, "license_key", "") or "VALID-KEY")

                    self.log(f"[COMPOSITE] selected model: {eq_type} / {m.name}", "FACTORY")
                    self.refresh_all()
                    return


    def _caretaker_history(self) -> list[EquipmentMemento]:
        # Try common names
        for name in ("_history", "history", "snapshots", "_snapshots"):
            if hasattr(self.caretaker, name):
                val = getattr(self.caretaker, name)
                if isinstance(val, list):
                    return val
        # Try methods
        for m in ("get_history", "history_list", "all"):
            if hasattr(self.caretaker, m) and callable(getattr(self.caretaker, m)):
                try:
                    val = getattr(self.caretaker, m)()
                    if isinstance(val, list):
                        return val
                except Exception:
                    pass
        return []

    def _caretaker_index(self) -> int:
        for name in ("_index", "index", "pos", "_pos"):
            if hasattr(self.caretaker, name):
                try:
                    return int(getattr(self.caretaker, name))
                except Exception:
                    pass
        # if caretaker has method current_index()
        if hasattr(self.caretaker, "current_index") and callable(getattr(self.caretaker, "current_index")):
            try:
                return int(self.caretaker.current_index())
            except Exception:
                pass
        return -1


    def _sync_snapshot_list_from_caretaker(self) -> None:
        history = list(self._caretaker_history())
        idx = self._caretaker_index()

        self._snapshot_list = history

        self.lst_snapshots.delete(0, "end")
        for i, m in enumerate(history):
            label = f"{i:02d} | {m.equipment_type} | online={m.use_online} analytics={m.use_analytics} proxy={m.use_proxy}"
            self.lst_snapshots.insert("end", label)

        if 0 <= idx < len(history):
            self.lst_snapshots.selection_clear(0, "end")
            self.lst_snapshots.selection_set(idx)
            self.lst_snapshots.see(idx)
            self._show_snapshot_details(history[idx])
        else:
            self.txt_memento.delete("1.0", "end")
            self.txt_memento.insert("1.0", "Нет активного snapshot.")

        info = self.caretaker.info() if hasattr(self.caretaker, "info") else ""
        self.lbl_memento_info.config(text=info)

    def _on_snapshot_select(self, _event) -> None:
        sel = self.lst_snapshots.curselection()
        if not sel:
            return
        i = int(sel[0])
        if 0 <= i < len(self._snapshot_list):
            self._show_snapshot_details(self._snapshot_list[i])

    def _show_snapshot_details(self, m: EquipmentMemento) -> None:
        self.txt_memento.delete("1.0", "end")
        self.txt_memento.insert(
            "1.0",
            f"equipment_type: {m.equipment_type}\n"
            f"specs: {m.specs}\n"
            f"functions: {m.functions}\n\n"
            f"base_software_title: {m.base_software_title}\n"
            f"use_online: {m.use_online}\n"
            f"use_analytics: {m.use_analytics}\n"
            f"use_proxy: {m.use_proxy}\n"
            f"license_key: {m.license_key}\n"
        )

    def restore_selected_snapshot(self) -> None:
        if not self._editing_enabled:
            messagebox.showinfo("VIEW режим", "В режиме VIEW изменения запрещены.")
            return
        if not self.current_equipment:
            messagebox.showwarning("Нет объекта", "Сначала создай тренажёр.")
            return
        sel = self.lst_snapshots.curselection()
        if not sel:
            messagebox.showinfo("Memento", "Выбери snapshot в списке.")
            return
        i = int(sel[0])
        if not (0 <= i < len(self._snapshot_list)):
            return

        self.restore_snapshot(self._snapshot_list[i])
        self.log(f"[MEMENTO] restored selected snapshot index={i}", "MEMENTO")
        self._sync_snapshot_list_from_caretaker()


    def on_create(self) -> None:
        if not self._editing_enabled:
            messagebox.showinfo("VIEW режим", "В режиме VIEW изменения запрещены.")
            return

        key = self.selected_key.get()
        try:
            factory = self.registry.get(key)
        except KeyError:
            messagebox.showerror("Ошибка", f"Неизвестный ключ фабрики: {key}")
            self.log(f"[ERROR] unknown factory key: {key}", "ERROR")
            return

        self.current_equipment = factory.create()
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

        eq.base_software_title = eq.software.name()
        self.rebuild_software_from_flags()


        self._add_to_catalog(eq)


        self.caretaker = Caretaker()
        self.caretaker.backup(self.create_memento_from_current())

        self.log(f"[FACTORY] created: {eq.equipment_type} / {eq.name}", "FACTORY")
        self.refresh_all()

    def on_clear(self) -> None:
        self.current_equipment = None
        self.txt_equipment.delete("1.0", "end")
        self.txt_software.delete("1.0", "end")
        self.txt_memento.delete("1.0", "end")
        self.log("[SYSTEM] cleared current equipment", "STATE")
        self.refresh_bottom_bar()

    def show_builder_log(self) -> None:
        if not self.current_equipment:
            messagebox.showinfo("Builder", "Сначала создай тренажёр.")
            self.log("[BUILDER] requested log but no equipment", "WARN")
            return
        log_lines = getattr(self.current_equipment, "build_log", None) or ["(лог сборки пуст)"]
        self.log("[BUILDER] log opened", "BUILDER")
        messagebox.showinfo("Builder Log", "\n".join(log_lines))

    def on_apply_decorators_click(self) -> None:
        if not self._editing_enabled:
            messagebox.showinfo("VIEW режим", "В режиме VIEW изменения запрещены.")
            return
        if not self.current_equipment:
            messagebox.showwarning("Нет объекта", "Сначала создай тренажёр.")
            self.log("[DECORATOR] apply failed (no equipment)", "WARN")
            return

        cmd = ApplyDecoratorsCommand(self, online=bool(self.var_online.get()), analytics=bool(self.var_analytics.get()))
        cmd.execute()
        self.log(
            f"[DECORATOR] applied: online={self.var_online.get()} analytics={self.var_analytics.get()}",
            "DECORATOR",
        )
        self.refresh_all()

    def on_apply_proxy_click(self) -> None:
        if not self._editing_enabled:
            messagebox.showinfo("VIEW режим", "В режиме VIEW изменения запрещены.")
            return
        if not self.current_equipment:
            messagebox.showwarning("Нет объекта", "Сначала создай тренажёр.")
            self.log("[PROXY] apply failed (no equipment)", "WARN")
            return

        enabled = bool(self.var_use_proxy.get())
        key = self.license_entry.get().strip()

        cmd = ApplyProxyCommand(self, enabled=enabled, license_key=key)
        cmd.execute()
        self.log(f"[PROXY] applied: enabled={enabled}, key='{key}'", "PROXY")
        self.refresh_all()

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

        self._add_to_catalog(eq)

        self.caretaker = Caretaker()
        self.caretaker.backup(self.create_memento_from_current())

        self.log("[SYSTEM] reset to base (Factory+Builder)", "FACTORY")
        self.refresh_all()

    def run_software_operation(self) -> None:
        if not self.current_equipment:
            self.log("[OPERATION] no equipment", "WARN")
            messagebox.showinfo("operation()", "Сначала создай тренажёр.")
            return

        software = self.current_equipment.software
        try:
            result = software.operation()
        except Exception as e:
            self.log(f"[ERROR] operation failed: {e}", "ERROR")
            messagebox.showerror("operation()", str(e))
            return

        proxy_log = ""
        if isinstance(software, SoftwareProxy):
            log_text = "\n".join(f"- {x}" for x in getattr(software, "log", [])) or "(лог пуст)"
            proxy_log = "\n\nЛог Proxy:\n" + log_text
            self.log(f"[PROXY] operation via proxy, name={software.name()}", "PROXY")
        else:
            self.log(f"[STATE] operation direct, name={software.name()}", "STATE")

        messagebox.showinfo("operation()", f"{result}{proxy_log}")
        self.refresh_all()

    # =========================================================
    # AppContext API for Commands (Command expects these)
    # =========================================================
    def set_decorators_state(self, online: bool, analytics: bool) -> None:
        if not self.current_equipment:
            return
        eq = self.current_equipment
        eq.use_online = bool(online)
        eq.use_analytics = bool(analytics)

        self.var_online.set(eq.use_online)
        self.var_analytics.set(eq.use_analytics)

        self.rebuild_software_from_flags()
        self._rebuild_tree()
        self.refresh_all()

    def set_proxy_state(self, enabled: bool, license_key: str) -> None:
        if not self.current_equipment:
            return
        eq = self.current_equipment
        eq.use_proxy = bool(enabled)
        eq.license_key = (license_key or "").strip()

        self.var_use_proxy.set(eq.use_proxy)
        self.license_entry.delete(0, "end")
        self.license_entry.insert(0, eq.license_key or "VALID-KEY")

        self.rebuild_software_from_flags()
        self._rebuild_tree()
        self.refresh_all()

    def has_equipment(self) -> bool:
        return self.current_equipment is not None

    def get_snapshot(self):
        return self.create_memento_from_current()

    def push_snapshot(self, snapshot):
        if not self._editing_enabled:
            messagebox.showinfo("VIEW режим", "В режиме VIEW изменения запрещены.")
            return
        self.caretaker.backup(snapshot)
        self.log("[MEMENTO] snapshot saved", "MEMENTO")
        self.refresh_all()

    def undo_snapshot(self):
        if not self._editing_enabled:
            messagebox.showinfo("VIEW режим", "В режиме VIEW изменения запрещены.")
            return None
        m = self.caretaker.undo()
        if m is None:
            messagebox.showinfo("Undo", "Больше некуда откатываться.")
            self.log("[MEMENTO] undo failed (no history)", "WARN")
        else:
            self.log("[MEMENTO] undo", "MEMENTO")
        return m

    def redo_snapshot(self):
        if not self._editing_enabled:
            messagebox.showinfo("VIEW режим", "В режиме VIEW изменения запрещены.")
            return None
        m = self.caretaker.redo()
        if m is None:
            messagebox.showinfo("Redo", "Больше некуда возвращаться.")
            self.log("[MEMENTO] redo failed (no future)", "WARN")
        else:
            self.log("[MEMENTO] redo", "MEMENTO")
        return m

    def restore_snapshot(self, snapshot):
        if not self.current_equipment:
            return
        self.restore_from_memento(snapshot)
        self.log("[MEMENTO] snapshot restored", "MEMENTO")
        self.refresh_all()

    # =========================================================
    # Memento create/restore
    # =========================================================
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

        self.var_online.set(eq.use_online)
        self.var_analytics.set(eq.use_analytics)
        self.var_use_proxy.set(eq.use_proxy)
        self.license_entry.delete(0, "end")
        self.license_entry.insert(0, eq.license_key or "VALID-KEY")

        self.rebuild_software_from_flags()

    # =========================================================
    # Refresh
    # =========================================================
    def refresh_all(self) -> None:
        if not self.current_equipment:
            self.txt_equipment.delete("1.0", "end")
            self.txt_equipment.insert("1.0", "Нет созданного тренажёра.\nСоздай его через Factory слева.")

            self.txt_software.delete("1.0", "end")
            self.txt_software.insert("1.0", "Цепочка ПО будет показана после создания тренажёра.")

            self.txt_memento.delete("1.0", "end")
            self.txt_memento.insert("1.0", "Нет snapshot (создай тренажёр и нажми Save Snapshot).")

            self._sync_snapshot_list_from_caretaker()
            self.refresh_bottom_bar()
            return

        eq = self.current_equipment

        self.txt_equipment.delete("1.0", "end")
        self.txt_equipment.insert("1.0", eq.summary())

        self.txt_software.delete("1.0", "end")
        self.txt_software.insert("1.0", self.software_chain_text())

        self._sync_snapshot_list_from_caretaker()
        self.refresh_bottom_bar()

    def refresh_bottom_bar(self) -> None:
        state_name = self.system_state.name() if self.system_state else "?"
        eq_name = f"{self.current_equipment.equipment_type}/{self.current_equipment.name}" if self.current_equipment else "—"
        hist = self.caretaker.info() if hasattr(self.caretaker, "info") else ""
        self.bottom_bar.configure(text=f"Mode: {state_name} | Current: {eq_name} | {hist}")


if __name__ == "__main__":
    App().mainloop()
