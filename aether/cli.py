"""Main CLI entry point for Aether."""

import typer

from aether.commands import init, coordinate, config, run

app = typer.Typer(
    name="aether",
    help="Dana agent scaffolding & coordination toolkit",
    add_completion=False,
)

app.command()(init.init)
app.command()(coordinate.coordinate)
app.command()(config.config)
app.command()(run.run)


if __name__ == "__main__":
    app()
