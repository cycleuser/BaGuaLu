"""Console UI utility."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class ConsoleUI:
    """Console UI wrapper."""

    @staticmethod
    def print(message: str) -> None:
        """Print message."""
        console.print(message)

    @staticmethod
    def print_panel(title: str, content: str) -> None:
        """Print panel."""
        console.print(Panel.fit(content, title=title, border_style="cyan"))

    @staticmethod
    def print_table(title: str, rows: list) -> None:
        """Print table."""
        table = Table(title=title)

        if rows:
            for col in range(len(rows[0])):
                table.add_column(f"Col {col}")

            for row in rows:
                table.add_row(*[str(cell) for cell in row])

        console.print(table)
