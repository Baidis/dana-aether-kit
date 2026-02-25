"""Main CLI entry point for Aether."""

import typer

from aether.commands import init, coordinate, config, run, agent, lock

app = typer.Typer(
    name="aether",
    help="Dana agent scaffolding & coordination toolkit",
    add_completion=False,
)

app.command()(init.init)
app.command()(coordinate.coordinate)
app.command()(config.config)
app.command()(run.run)
app.command()(agent.agent)
app.command(name="lock")(lock.lock)
app.command(name="unlock")(lock.unlock)
app.command(name="locks")(lock.locks)


if __name__ == "__main__":
    app()
