import re 
from unicodedata import normalize

def slugify(a: str, st: set, video_id: str) -> str:
    slug = normalize("NFKD", a).encode("ascii", "ignore").decode("utf-8").lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    
    return unique_slug(slug, st, video_id)

def unique_slug(slug: str, slugs: set, video_id: str) -> str:
    if slug not in slugs:
        return slug
   
    res = f"{slug}-{video_id}"
    
    if res not in slugs:
        return res
    
    c = 1
    while f"{slug}-{c}" in slugs:
        c += 1
        
    return f"{slug}-{c}"