from pathlib import Path
from rich.console import Console
import sys

from asr_scraper.orchestrator import Orchestrator
from asr_scraper.config import config
from asr_scraper.adapters.base import registry
from asr_scraper.utils.read_config import create_config
from asr_scraper.utils.logger_config import setup_logging
from asr_scraper.config import config
from asr_scraper.utils.system_check import check_ffmpeg

def main():
    console = Console()
    try: 
        check_ffmpeg()
    except Exception as e:
        console.print(f"[red]{str(e)}[/red]")
        return
        
    platform = sys.argv[1] if len(sys.argv) > 1 else "youtube"
    
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
