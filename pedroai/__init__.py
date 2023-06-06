import logging
from rich.logging import RichHandler


__version__ = "0.5.0"

logging.basicConfig(
    format='%(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[RichHandler(rich_tracebacks=True)],
    # TODO: this would get completely jacked by distribution
    # logging.FileHandler(f'/checkpoint/{os.getlogin()}/logs/retro-z/retro_z_data.log')
    force=True)