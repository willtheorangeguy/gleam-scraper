"""
Interactive TUI for browsing and opening giveaways.
"""

import logging
import webbrowser
from typing import List, Tuple

from prompt_toolkit.shortcuts import message_dialog, radiolist_dialog
from rich.console import Console
from rich.panel import Panel

from .scraper import Giveaway

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


class SimpleTUI:
    """Arrow-key-driven giveaway browser."""

    def __init__(self, giveaways: List[Giveaway]):
        self.giveaways = giveaways

    def _build_choices(self) -> List[Tuple[str, str]]:
        choices: List[Tuple[str, str]] = []
        for index, giveaway in enumerate(self.giveaways):
            description = giveaway.description or ""
            compact_description = (
                f" - {description[:70]}..."
                if len(description) > 70
                else f" - {description}"
            )
            label = f"{index + 1:>3}. {giveaway.title}{compact_description}"
            choices.append((str(index), label))
        return choices

    def _show_details(self, giveaway: Giveaway) -> None:
        panel = Panel(
            f"[bold cyan]Title:[/bold cyan]\n{giveaway.title}\n\n"
            f"[bold cyan]URL:[/bold cyan]\n{giveaway.url}\n\n"
            f"[bold cyan]Description:[/bold cyan]\n{giveaway.description or 'N/A'}",
            title="[bold magenta]Giveaway Details[/bold magenta]",
        )
        console.print(panel)

    def run(self) -> None:
        if not self.giveaways:
            console.print("[red]No giveaways found! Try --force-refresh[/red]")
            return

        while True:
            selected_index = radiolist_dialog(
                title="Gleam.io Giveaways",
                text=(
                    "Use ↑/↓ to navigate, Enter to choose, Esc to quit.\n"
                    "After selecting, choose whether to open or view details."
                ),
                values=self._build_choices(),
                ok_text="Select",
                cancel_text="Quit",
            ).run()

            if selected_index is None:
                console.print("[cyan]Goodbye![/cyan]")
                return

            giveaway = self.giveaways[int(selected_index)]
            action = radiolist_dialog(
                title=f"Selected: {giveaway.title}",
                text="Choose an action:",
                values=[
                    ("open", "Open giveaway in browser"),
                    ("details", "View giveaway details in terminal"),
                    ("back", "Back to giveaway list"),
                ],
                ok_text="Run",
                cancel_text="Back",
            ).run()

            if action in (None, "back"):
                continue

            if action == "details":
                console.clear()
                self._show_details(giveaway)
                input("Press Enter to return to the list...")
                continue

            try:
                console.print(f"[green]Opening: {giveaway.title}[/green]")
                webbrowser.open(giveaway.url)
                logger.info("Opened: %s", giveaway.url)
                message_dialog(
                    title="Opened",
                    text=f"Opened in browser:\n{giveaway.title}\n{giveaway.url}",
                ).run()
            except Exception as exc:
                logger.error("Error opening browser: %s", exc)
                message_dialog(
                    title="Error",
                    text=f"Failed to open browser:\n{exc}",
                ).run()
