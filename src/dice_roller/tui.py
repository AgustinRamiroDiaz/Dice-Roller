from __future__ import annotations

from collections.abc import Callable

from .evaluator import Evaluator
from .simulation import evaluate

try:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical
    from textual.widgets import Footer, Header, Input, RichLog, Static
except ImportError as error:
    raise SystemExit(
        "The dice-roller TUI requires the optional 'tui' extra. "
        "Install it with: uv sync --extra tui"
    ) from error


class DiceRollerTui(App):
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
        evaluator_factory: Callable[[Callable[[str], None]], Evaluator] | None = None,
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
        self._evaluator = self._evaluator_factory(self._write_trace)
        self.query_one("#notation", Input).focus()
        self.query_one("#trace", RichLog).write("Roll details will appear here.")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        notation = event.value.strip()
        if not notation:
            return

        self._history.append(notation)
        self._history_index = None

        result_widget = self.query_one("#result", Static)
        history = self.query_one("#history", RichLog)
        trace = self.query_one("#trace", RichLog)
        trace.clear()

        try:
            result = evaluate(notation, evaluator=self._require_evaluator())
        except Exception as error:
            message = f"[red]Error:[/red] {error}"
            result_widget.update(message)
            history.write(f"[red]✗[/red] {notation} -> {error}")
            trace.write(message)
            return

        result_widget.update(f"[bold green]{result}[/bold green]")
        history.write(f"[green]✓[/green] {notation} -> [bold]{result}[/bold]")
        event.input.value = ""

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
        self.query_one("#trace", RichLog).write(message)

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
            self._evaluator = self._evaluator_factory(self._write_trace)
        return self._evaluator

    @staticmethod
    def _default_evaluator_factory(trace: Callable[[str], None]) -> Evaluator:
        return Evaluator(trace=trace)


def main() -> None:
    DiceRollerTui().run()
