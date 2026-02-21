import re 
from unicodedata import normalize
from pathlib import Path

def slugify(a: str, output_dir: Path, video_id: str) -> Path:
    slug = normalize("NFKC", a).lower()
    slug= re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[-\s]+", "-", slug).strip("-_")

    return unique_slug(slug, output_dir, video_id)

    # slug = normalize("NFKD", a).encode("ascii", "ignore").decode("utf-8").lower()
    # slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    
    # return unique_slug(slug, st, video_id)
    
def unique_slug(slug: str,output_dir: Path, video_id: str) -> Path:
    output_path = output_dir / f"{slug}.wav"
    
    if not output_path.exists():
        return output_path
    
    output_path = output_dir / f"{slug}-{video_id}.wav"
    
    if not output_path.exists():
        return output_path
    
    # just in case
    c = 1
    while (output_dir / f"{slug}-{c}.wav").exists():
        c += 1
        
    return output_dir / f"{slug}-{c}.wav"