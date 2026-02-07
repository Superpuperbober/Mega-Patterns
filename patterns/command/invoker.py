from __future__ import annotations
from typing import Optional
from patterns.command.commands import Command


class Invoker:
    """
    Invoker хранит команды и выполняет их по имени.
    (Можно расширить: очереди, макросы, хоткеи.)
    """
    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}

    def register(self, name: str, cmd: Command) -> None:
        self._commands[name] = cmd

    def execute(self, name: str) -> None:
        cmd = self._commands.get(name)
        if cmd:
            cmd.execute()

    def get(self, name: str) -> Optional[Command]:
        return self._commands.get(name)
