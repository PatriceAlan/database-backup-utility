import click
from database_backup_utility.utils.context import AppContext

@click.group()
@click.option("-c", "--config", type=click.Path(), help="Path to configuration file.")
@click.option("-v", "verbose", count=True, help="Increase verbosity")
@click.option("-q", "--quiet", is_flag=True, help="Reduce output.")
@click.option("-d", "--dry-run", is_flag=True, help="Show actions without executing")
@click.pass_context
def cli(ctx, config, verbose, quiet, dry_run):
    """
    Database Backup Utility CLI.
    """
    ctx.obj = AppContext(
        config_path=config,
        verbose=verbose,
        quiet=quiet,
        dry_run=dry_run
    )

cli.add_command(backup)

if __name__ == "__main__":
    cli()
