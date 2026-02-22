from pathlib import Path
from rich.console import Console
import sys

from asr_scraper.orchestrator import Orchestrator
from asr_scraper.config import config
from asr_scraper.adapters.base import registry
from asr_scraper.utils.read_config import create_config
from asr_scraper.utils.logger_config import setup_logging
from asr_scraper.config import config

def main():
    platform = sys.argv[1] if len(sys.argv) > 1 else "youtube"
    
    console = Console()
    create_config()

    setup_logging(Path("logs"))

    console.print("[navy_blue]Building dataset[/navy_blue]")

    platform_adapter = registry.get(platform)
    if platform_adapter == None: 
        console.print("[red]Invalid platform[/red]")
        return

    if platform_adapter is None:
        console.print("[red]Invalid platform[/red]")
        return

    orchestrator = Orchestrator(console, platform_adapter, platform)

    orchestrator.build(config.channels)

    console.print("[green]Dataset successfully built[/green]")


if __name__ == "__main__":
    main()
