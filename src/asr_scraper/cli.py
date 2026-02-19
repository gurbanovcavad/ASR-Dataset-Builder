import typer 
from rich.console import Console
from .orchestrator import Orchestrator
from pathlib import Path
from typing import Optional, List
from .config import Config
from asr_scraper.adapters.base import registry

app = typer.Typer(help="ASR Dataset Builder")
console = Console()

# since the only supported platform is youtube I've set default value of platform to youtube to change it to interactive change the first value of typer.Option to ... in both commands
@app.command()
def build(
    platform: str = typer.Option(
        "youtube", "--platform", "-p", help="Platform name"
    ),
    channels: List[str] = typer.Option(
        ..., "--channels", "-c", help="Channel file paths"
    ),
    output_dir: Path = typer.Option(
        Path("./data"), "--output", "-o", help="Output directory"
    ),
    sample_rate: int = typer.Option(
        16000, "--sr", help="Sample rate"
    ),
    mono: bool = typer.Option(
        True, "--mono/--stereo", help="Convert to mono"
    ),
    pcm_bit_depth: int = typer.Option(
        16, "--codec", help="PCM bit depth"
    ),
    concurrency: int = typer.Option(
        2, "--jobs", "-j", help="Parallel jobs"
    ),
    max_videos_per_channel: Optional[int] = typer.Option(
        None, "--max", "-m", help="Max videos per channel"
    ),
    since_date: Optional[str] = typer.Option(
        None, "--since-date", help="Download since date"
    ),
    skip_existing: bool = typer.Option(
        True, "--skip/--no-skip", help="Skip existing files"
    ),
    write_manifest: Path = typer.Option(
        Path("./manifest.jsonl"), "--manifest", help="Manifest path"
    ),
):
    console.print("[white]Building dataset[/white]")
    
    # build config file based on user input 
    config = Config(
        channels=channels,
        output_dir=output_dir,
        sample_rate=sample_rate,
        mono=mono,
        pcm_bit_depth=pcm_bit_depth,
        concurrency=concurrency,
        max_videos_per_channel=max_videos_per_channel,
        since_date=since_date,
        skip_existing=skip_existing,
        write_manifest=write_manifest
        )

    # get platformAdapter or stop the execution (the only available platform is youtube)
    platformAdapter = registry.get(platform)
    if platformAdapter == None: 
        console.print("[red]Invalid platform[/red]")
        return
    
    # create orchestrator with the channel adapter and config 
    orchestrator = Orchestrator(config, platformAdapter)
   
    # build a dataset
    for channel in channels:
        videos = orchestrator.discover(channel)
        
        for video in videos:
            print(video)
    
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
   
    # build config file based on user input 
    config = Config(
        channels=channels,
        )

    # get platformAdapter or stop the execution (the only available platform is youtube)
    platformAdapter = registry.get(platform)
    if platformAdapter == None: 
        console.print("[red]Invalid platform[/red]")
        return
    
    # create orchestrator with the channel adapter and config 
    orchestrator = Orchestrator(config, platformAdapter)
   
    # discover the videos of the provided channel
    for channel in channels:
        videos = orchestrator.discover(channel)
        
        for video in videos:
            console.print(f"[blue]{video}[/blue]")
        
    console.print("[green]Discovery completed[/green]")

if __name__ == "__main__":
    app()   