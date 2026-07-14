from __future__ import annotations

import asyncio
from collections.abc import Callable
from concurrent.futures import Future

import numpy as np

from .evaluator import DiceRolls, KeepChoiceHandler, TraceCallback
from .evaluator import Evaluator
from .simulation import evaluate

try:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical
    from textual.screen import ModalScreen
    from textual.widgets import (
        Button,
        Footer,
        Header,
        Input,
        RichLog,
        SelectionList,
        Static,
    )
except ImportError as error:
    raise SystemExit(
        "The dice-roller TUI requires the optional 'tui' extra. "
        "Install it with: uv sync --extra tui"
    ) from error


class KeepChoiceScreen(ModalScreen[list[int] | None]):
    CSS = """
    KeepChoiceScreen {
        align: center middle;
    }

    #keep-choice-dialog {
        width: 48;
        max-width: 90%;
        height: auto;
        padding: 1 2;
        border: thick $primary;
        background: $surface;
    }

    #keep-choice-title {
        text-style: bold;
        margin-bottom: 1;
    }

    #keep-choice-list {
        height: auto;
        max-height: 14;
        margin-bottom: 1;
    }

    #keep-choice-error {
        height: 1;
        color: $error;
        margin-bottom: 1;
    }

    #keep-choice-buttons {
        height: auto;
        align-horizontal: right;
    }

    Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("enter", "confirm", "Keep selected"),
    ]

    def __init__(self, rolls: DiceRolls, amount: int) -> None:
        super().__init__()
        self._rolls = [int(roll) for roll in rolls]
        self._amount = amount

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(
                f"Choose {self._amount} dice to keep from {self._rolls}",
                id="keep-choice-title",
            ),
            SelectionList(
                *[
                    (f"Die {index + 1}: {value}", (index, value))
                    for index, value in enumerate(self._rolls)
                ],
                id="keep-choice-list",
            ),
            Static("", id="keep-choice-error"),
            Horizontal(
                Button("Cancel", id="cancel"),
                Button("Keep", variant="primary", id="keep"),
                id="keep-choice-buttons",
            ),
            id="keep-choice-dialog",
        )

    def on_mount(self) -> None:
        self.query_one("#keep-choice-list", SelectionList).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
            return
        if event.button.id == "keep":
            self.action_confirm()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_confirm(self) -> None:
        selection_list = self.query_one("#keep-choice-list", SelectionList)
        selected = selection_list.selected
        if len(selected) != self._amount:
            self.query_one("#keep-choice-error", Static).update(
                f"Select exactly {self._amount} dice."
            )
            return

        self.dismiss([value for (_index, value) in selected])


class DiceRollerTui(App[None]):
    CSS = """
    Screen {
        layout: vertical;
    }

    #main {
        height: 1fr;
    }

    #workspace {
        height: 1fr;
    }

    #left-pane {
        width: 2fr;
        min-width: 40;
        padding: 1;
        border: solid $primary;
    }

    #right-pane {
        width: 1fr;
        min-width: 32;
        padding: 1;
        border: solid $secondary;
    }

    #notation {
        margin-bottom: 1;
    }

    #result {
        height: 3;
        content-align: left middle;
        padding: 0 1;
        margin-bottom: 1;
        border: round $accent;
    }

    .label {
        text-style: bold;
        margin-bottom: 1;
    }

    RichLog {
        height: 1fr;
        border: round $surface;
    }
    """

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+l", "clear", "Clear"),
        ("up", "history_previous", "Previous roll"),
        ("down", "history_next", "Next roll"),
    ]

    TITLE = "Dice Roller"
    SUB_TITLE = "Parser, evaluator, and simulation TUI"

    def __init__(
        self,
        *,
        evaluator_factory: Callable[
            [TraceCallback, KeepChoiceHandler], Evaluator
        ]
        | None = None,
    ) -> None:
        super().__init__()
        self._evaluator_factory = evaluator_factory or self._default_evaluator_factory
        self._evaluator: Evaluator | None = None
        self._history: list[str] = []
        self._history_index: int | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="workspace"):
            with Vertical(id="left-pane"):
                yield Static("Dice notation", classes="label")
                yield Input(
                    placeholder="Try 2d6 + 3, 4d6kh3, or x = 1d20",
                    id="notation",
                )
                yield Static("Result appears here", id="result")
                yield Static("History", classes="label")
                yield RichLog(id="history", wrap=True, markup=True)
            with Vertical(id="right-pane"):
                yield Static("Trace", classes="label")
                yield RichLog(id="trace", wrap=True, markup=True)
        yield Footer()

    def on_mount(self) -> None:
        self._evaluator = self._evaluator_factory(
            self._write_trace,
            self._choose_keep_dice,
        )
        self.query_one("#notation", Input).focus()
        self.query_one("#trace", RichLog).write("Roll details will appear here.")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        notation = event.value.strip()
        if not notation:
            return

        self._history.append(notation)
        self._history_index = None

        event.input.disabled = True
        asyncio.create_task(self._submit_notation(notation, event.input))

    async def _submit_notation(self, notation: str, input_widget: Input) -> None:
        result_widget = self.query_one("#result", Static)
        history = self.query_one("#history", RichLog)
        trace = self.query_one("#trace", RichLog)
        trace.clear()

        try:
            result = await asyncio.to_thread(self._evaluate_notation, notation)
        except Exception as error:
            message = f"[red]Error:[/red] {error}"
            result_widget.update(message)
            history.write(f"[red]✗[/red] {notation} -> {error}")
            trace.write(message)
            input_widget.disabled = False
            input_widget.focus()
            return

        result_widget.update(f"[bold green]{result}[/bold green]")
        history.write(f"[green]✓[/green] {notation} -> [bold]{result}[/bold]")
        input_widget.value = ""
        input_widget.disabled = False
        input_widget.focus()

    def action_clear(self) -> None:
        self.query_one("#result", Static).update("Result appears here")
        self.query_one("#history", RichLog).clear()
        self.query_one("#trace", RichLog).clear()
        self._history.clear()
        self._history_index = None

    def action_history_previous(self) -> None:
        if not self._history:
            return

        if self._history_index is None:
            self._history_index = len(self._history) - 1
        else:
            self._history_index = max(0, self._history_index - 1)

        self._load_history_item()

    def action_history_next(self) -> None:
        if self._history_index is None:
            return

        if self._history_index >= len(self._history) - 1:
            self._history_index = None
            self._set_notation("")
            return

        self._history_index += 1
        self._load_history_item()

    def _write_trace(self, message: str) -> None:
        self.call_from_thread(self._write_trace_on_app_thread, message)

    def _write_trace_on_app_thread(self, message: str) -> None:
        self.query_one("#trace", RichLog).write(message)

    def _choose_keep_dice(self, sorted_rolls_left: DiceRolls, amount: int) -> DiceRolls:
        selection: Future[list[int] | None] = Future()

        def show_picker() -> None:
            self.push_screen(
                KeepChoiceScreen(sorted_rolls_left, amount),
                selection.set_result,
            )

        self.call_from_thread(show_picker)
        choices = selection.result()
        if choices is None:
            raise ValueError("keep choice selection was cancelled")
        return np.array(choices)

    def _evaluate_notation(self, notation: str) -> float:
        return evaluate(notation, evaluator=self._require_evaluator())

    def _load_history_item(self) -> None:
        if self._history_index is None:
            return
        self._set_notation(self._history[self._history_index])

    def _set_notation(self, notation: str) -> None:
        input_widget = self.query_one("#notation", Input)
        input_widget.value = notation
        input_widget.cursor_position = len(notation)
        input_widget.focus()

    def _require_evaluator(self) -> Evaluator:
        if self._evaluator is None:
            self._evaluator = self._evaluator_factory(
                self._write_trace,
                self._choose_keep_dice,
            )
        return self._evaluator

    @staticmethod
    def _default_evaluator_factory(
        trace: TraceCallback,
        keep_choice_handler: KeepChoiceHandler,
    ) -> Evaluator:
        return Evaluator(trace=trace, keep_choice_handler=keep_choice_handler)


def main() -> None:
    DiceRollerTui().run()
