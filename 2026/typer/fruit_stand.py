#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "typer>=0.16,<1",
# ]
# ///

from typing import Annotated

import typer

app = typer.Typer(
    no_args_is_help=True,
    help="Trade produce at the Interplanetary Fruit Stand.",
)


@app.command()
def buy(
    fruit: Annotated[str, typer.Argument(help="Fruit to buy.")],
    quantity: Annotated[
        int,
        typer.Option("--quantity", "-q", min=1, help="Number of pieces to buy."),
    ] = 1,
    origin: Annotated[
        str,
        typer.Option("--from", help="Planet or moon the fruit came from."),
    ] = "Earth",
    organic: Annotated[
        bool,
        typer.Option(
            "--organic/--conventional",
            help="Choose organic or conventional fruit.",
        ),
    ] = False,
) -> None:
    """Buy fruit from a planetary market."""
    kind = "organic" if organic else "conventional"
    typer.echo(f"Buying {quantity} {kind} {fruit} from {origin}.")


@app.command()
def sell(
    fruit: Annotated[str, typer.Argument(help="Fruit to sell.")],
    price: Annotated[
        float,
        typer.Option("--price", "-p", min=0.01, help="Price per piece."),
    ] = 1.0,
    all_inventory: Annotated[
        bool,
        typer.Option("--all", help="Sell every piece of this fruit."),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Preview the sale without completing it."),
    ] = False,
) -> None:
    """Sell fruit back to the market."""
    amount = "all available" if all_inventory else "one"
    action = "Would sell" if dry_run else "Selling"
    typer.echo(f"{action} {amount} {fruit} at ${price:.2f} each.")


if __name__ == "__main__":
    app()
