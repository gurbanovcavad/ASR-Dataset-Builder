import typer 
from typing import Optional
from pathlib import Path
from rich.console import Console
from .config import ScraperConfig
from .orchestrator import Orchestrator

app = typer.Typer(help="ASR Dataset Builder")
console = Console()

@app.command()
def discover(
    
):  
    console.print("Discovering videos")
    # TODO - implement discover function
    Orchestrator.discover()

    console.print("Discovery complete")
    
@app_command()
def build():
    console.print("Building dataset")
    # TODO - add building dataset in orchestrator
    
    console.print("Dataset successfully built")
    
    
if __main__ == "__main__":
    app()   