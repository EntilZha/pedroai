import typer

from pedroai import download, notifications

cli = typer.Typer()
cli.command(name="download")(download.main)
cli.command(name="pushcuts")(notifications.pushcuts_main)


@cli.command()
def nop():
    pass


if __name__ == "__main__":
    cli()
