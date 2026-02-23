"""Coordinate command - task splitting for multi-CLI teams."""

import typer


def coordinate(
    task: str,
    dana_intent: bool = typer.Option(
        False, "--dana-intent", help="Output ready-to-use Dana intent block"
    ),
):
    """Simple coordinator: prints Dana-style intent + suggested CLI prompts"""
    typer.echo(f"Coordinating task: {task}")

    if dana_intent:
        typer.echo("\nDana intent block (paste into .na file):")
        print(
            f'''intent "{task}":
    # Agent implementation goes here
    # Runtime will plan & execute
    
    def handle_{task.replace(" ", "_").lower()}():
        # Your implementation
        return reason("Process {task}")
'''
        )
        return

    typer.echo("\nDana intent block suggestion:")
    print(f'intent "{task}":\n    // paste implementation here\n')

    typer.echo("Suggested splits for your CLIs:")
    print("- Claude Pro: Lead architecture & complex reasoning")
    print(f"  claude 'Design agent for: {task}'")
    print("- Gemini Pro: Fast code gen & tests")
    print(f"  gemini 'Implement Dana agent for: {task}'")
    print("- OpenCode MiniMax: Bulk / repetitive parts")
    print(f"  opencode --model=minimax 'Generate tests for: {task}'")
    print("- Grok: Creative / edge cases")
    print(f"  grok 'Explore alternatives for: {task}'")
