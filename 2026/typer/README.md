# Typer

Documentation: https://typer.tiangolo.com/

GitHub: https://github.com/fastapi/typer

Tech Radar: https://www.thoughtworks.com/en-us/radar/languages-and-frameworks/typer

**Assessment:** Adopt (April 2026, Volume 34)

Typer is a Python library for building command-line applications from ordinary type-annotated functions. It uses the function name, parameters, type hints, defaults, and docstrings to generate commands, arguments, options, validation, and `--help` output.

## Minimal multi-command setup

A multi-command application starts with `typer.Typer()`. Each function decorated with `@app.command()` becomes a subcommand, and each subcommand can have its own arguments and flags.

```python
from typing import Annotated

import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def buy(
    fruit: Annotated[str, typer.Argument(help="Fruit to buy.")],
    quantity: Annotated[
        int,
        typer.Option("--quantity", "-q", min=1),
    ] = 1,
    organic: Annotated[
        bool,
        typer.Option("--organic/--conventional"),
    ] = False,
) -> None:
    """Buy fruit from the stand."""
    kind = "organic" if organic else "conventional"
    typer.echo(f"Buying {quantity} {kind} {fruit}.")


@app.command()
def sell(
    fruit: Annotated[str, typer.Argument(help="Fruit to sell.")],
    price: Annotated[
        float,
        typer.Option("--price", "-p", min=0.01),
    ] = 1.0,
    all_inventory: Annotated[
        bool,
        typer.Option("--all"),
    ] = False,
) -> None:
    """Sell fruit back to the stand."""
    amount = "all available" if all_inventory else "one"
    typer.echo(f"Selling {amount} {fruit} at ${price:.2f} each.")


if __name__ == "__main__":
    app()
```

Typer automatically exposes `buy` and `sell`, converts `--quantity` to an integer and `--price` to a float, validates their minimum values, and generates help for the application and each command.

## Demo script

The complete executable example is [`fruit_stand.py`](./fruit_stand.py), a small, deterministic fruit stand. It does not require an API key or network connection, so the presentation can focus entirely on how Typer generates and validates the CLI.

Show the generated top-level help:

```bash
./fruit_stand.py --help
```

Show help for one subcommand:

```bash
./fruit_stand.py buy --help
```

Buy several organic mangoes from a named orchard:

```bash
./fruit_stand.py buy mango --quantity 4 --from "Hill Orchard" --organic
```

Preview selling all available blueberries:

```bash
./fruit_stand.py sell blueberries --price 3.50 --all --dry-run
```

The script can also be run explicitly through `uv`:

```bash
uv run 2026/typer/fruit_stand.py --help
```

The more substantial Typer example will live in the Agent Skills presentation, where Typer will provide the command-line interface around the skill-related workflow.

<!-- Additional notes will be added from the presenter's follow-up instructions. -->
