import typer

from pedroai import download

cli = typer.Typer()
cli.command(name="download")(download.main)


@cli.command()
def nop():
    pass


if __name__ == "__main__":
    cli()
