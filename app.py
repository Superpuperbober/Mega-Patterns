import tkinter as tk
from tkinter import ttk, messagebox

from patterns.factory import FactoryRegistry, BikeFactory, TreadmillFactory, RowingMachineFactory


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Trainer Software Demo — Factory Method")
        self.geometry("720x520")

        self.registry = FactoryRegistry()
        self.registry.register("bike", BikeFactory())
        self.registry.register("treadmill", TreadmillFactory())
        self.registry.register("rowing", RowingMachineFactory())

        self._build_ui()

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text="Создание тренажёра через Фабрику", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", pady=(0, 10)
        )

        row = ttk.Frame(root)
        row.pack(fill="x", pady=(0, 10))

        ttk.Label(row, text="Тип тренажёра:").pack(side="left")

        self.selected_key = tk.StringVar(value=self.registry.keys()[0])
        ttk.Combobox(
            row,
            textvariable=self.selected_key,
            values=self.registry.keys(),
            state="readonly",
            width=20,
        ).pack(side="left", padx=8)

        ttk.Button(row, text="Создать", command=self.on_create).pack(side="left")
        ttk.Button(row, text="Очистить", command=self.on_clear).pack(side="left", padx=8)

        ttk.Separator(root).pack(fill="x", pady=8)

        self.output = tk.Text(root, wrap="word", height=22)
        self.output.pack(fill="both", expand=True)

        ttk.Label(
            root,
            text="GUI не создаёт объекты напрямую — он обращается к фабрике через общий интерфейс.",
            foreground="#444",
        ).pack(anchor="w", pady=(8, 0))

    def on_create(self) -> None:
        key = self.selected_key.get()
        try:
            factory = self.registry.get(key)
        except KeyError:
            messagebox.showerror("Ошибка", f"Неизвестный ключ фабрики: {key}")
            return

        equipment = factory.create()
        self.output.delete("1.0", "end")
        self.output.insert("1.0", equipment.summary())

    def on_clear(self) -> None:
        self.output.delete("1.0", "end")


if __name__ == "__main__":
    App().mainloop()
