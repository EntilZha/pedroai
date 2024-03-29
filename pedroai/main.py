import typer

from pedroai import download, notifications, bibtex, snapshot, files, slurm_logs, slurm_tui

def stui():
    app = slurm_tui.SlurmDashboardApp()
    app.run()

cli = typer.Typer()
cli.add_typer(bibtex.app, name='bibtex')
cli.add_typer(files.app, name='files')
cli.command(name='pushcuts')(notifications.pushcuts_main)
cli.command(name='download')(download.main)
cli.command(name='snapshot')(snapshot.main)
cli.command(name='slogs')(slurm_logs.main)
cli.command(name='stui')(stui)


@cli.command()
def nop():
    pass


if __name__ == "__main__":
    cli()
