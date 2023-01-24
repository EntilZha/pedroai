import typer

from pedroai import download, notifications, bibtex, snapshot

cli = typer.Typer()
cli.add_typer(bibtex.app, name='bibtex')
cli.command(name='pushcuts')(notifications.pushcuts_main)
cli.command(name='download')(download.main)
cli.command(name='snapshot')(snapshot.main)


@cli.command()
def nop():
    pass


if __name__ == "__main__":
    cli()
