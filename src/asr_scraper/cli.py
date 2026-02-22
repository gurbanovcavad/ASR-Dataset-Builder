import typer 
from rich.console import Console
from pathlib import Path
from typing import Optional, List
from datetime import date

from .orchestrator import Orchestrator
from .config import config
from asr_scraper.adapters.base import registry
from asr_scraper.utils.read_config import create_config
from asr_scraper.utils.logger_config import setup_logging

# create config based on config.yaml file
create_config()

setup_logging(Path("logs"))

app = typer.Typer(help="ASR Dataset Builder")
console = Console()

# since the only supported platform is youtube, I've set the default value of platform to youtube. To make it interactive, change the first argument of typer.Option to ... in all of the commands
@app.command()
def build(
    platform: str = typer.Option(
        "youtube", "--platform", "-p", help="Platform name"
    ),
    channels: List[str] = typer.Option(
        ..., "--channels", "-c", help="Channel file paths"
    ),
    output_dir: Path = typer.Option(
        config.output_dir, "--output", "-o", help="Output directory"
    ),
    sample_rate: int = typer.Option(
        config.sample_rate, "--sr", help="Sample rate"
    ),
    mono: bool = typer.Option(
        config.mono, "--mono/--stereo", help="Convert to mono"
    ),
    pcm_bit_depth: int = typer.Option(
        config.pcm_bit_depth, "--codec", help="PCM bit depth"
    ),
    concurrency: int = typer.Option(
        config.concurrency, "--jobs", "-j", help="Parallel jobs"
    ),
    max_videos_per_channel: Optional[int] = typer.Option(
        config.max_videos_per_channel, "--max", "-m", help="Max videos per channel"
    ),
    since_date: Optional[str] = typer.Option(
        config.since_date, "--since-date", help="Download since date"
    ),
    skip_existing: bool = typer.Option(
        config.skip_existing, "--skip/--no-skip", help="Skip existing files"
    ),
    write_manifest: Path = typer.Option(
        config.write_manifest, "--manifest", help="Manifest path"
    ),
):
    console.print("[navy_blue]Building dataset[/navy_blue]")
    # update config object based on user input 
    setattr(config, "channels", channels)
    setattr(config, "output_dir", output_dir)
    setattr(config, "sample_rate", sample_rate)
    setattr(config, "mono", mono)
    setattr(config, "pcm_bit_depth", pcm_bit_depth)
    setattr(config, "concurrency", concurrency)
    setattr(config, "max_videos_per_channel", max_videos_per_channel)
    setattr(config, "since_date", since_date)
    setattr(config, "skip_existing", skip_existing)
    setattr(config, "write_manifest", write_manifest)

    # get platformAdapter or stop the execution (the only available platform is youtube)
    platformAdapter = registry.get(platform)
    if platformAdapter == None: 
        console.print("[red]Invalid platform[/red]")
        return
    
    # create orchestrator with the channel adapter and config 
    orchestrator = Orchestrator(console, platformAdapter, platform)
   
    # build a dataset
    orchestrator.build(channels)
    console.print("[green]Dataset successfully built[/green]")

@app.command()
def discover(
    platform: str = typer.Option(
        "youtube", "--platform", "-p", help="Platform name"
    ),
    channels: List[str] = typer.Option(
        ..., "--channels", "-c", help="Channel file paths"
    ),
):
    console.print("[navy_blue]Discovering videos[/navy_blue]")
   
    # update config object based on user input 
    setattr(config, "channels", channels)
    
    # get platformAdapter or stop the execution (the only available platform is youtube)
    platform_adapter = registry.get(platform)
    if platform_adapter == None: 
        console.print("[red]Invalid platform[/red]")
        return
    
    # create orchestrator with the channel adapter and config 
    orchestrator = Orchestrator(console, platform_adapter, platform)
   
    # discover the videos of the provided channel
    orchestrator.discover(channels)
        
    console.print("[green]Discovery completed[/green]")
    