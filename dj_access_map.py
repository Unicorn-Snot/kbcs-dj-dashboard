# Pseudocode structure
from typing import Dict, List, Optional, Tuple

dj_access_map = {
    ("Auntmama", "2003"): "Sunday Folks",
    ("Levi Sweeney", "2024"): "Retro Radio Theatre",
    ("John Pai", "2000"): "Giant Steps",
    ("Rus Thompson", "2003 and 2023"): ["Road Songs", "Night Train"],
    ("Michael Schell", "2021"): "Flotation Device",
    ("Matt Fish", "2021"): "CrossCurrents",
    ("Tom Voorhees", "2000"): "Bluegrass Ramble",
    ("John Gibaut", "2016"): "Sunday's Hornpipe",
    ("Braddah Gomes", "1991"): "Hawai'i Radio Connection",
    ("Michael Olson", "2023"): "Freedom Sounds",
    ("Oneda Harris", "2004"): ["The Vault", "Living the Blues", "Gospel Highway"],
    ("Mike Biggins", "2016"): "Sunday Folks",
    ("Tom Keeney", "1980s"): "Bluegrass Ramble",
    ("Tracy Yang", "2024"): "K-Wave",
    ("Larry Lewin", "1988"): "Saturday Tradition",
    ("Winona Hollins-Hauge", "20 years"): ["Living the Blues", "Gospel Highway"],
    ("Chairman Moe", "2009"): "Chairman Moe",
    ("Iaan Hughes", "2000"): ["Roots Rock & Soul with Iaan Hughes", "In Studio"],
    ("Greg D'Elia", "ops"): ["Roots Rock & Soul with Greg Delia", "The Dubside"]
}

def authenticate(username: str, password: str) -> Optional[List[str]]:
    """Return list of programs if (username, password) is valid; else None."""
    return dj_access_map.get((username, password))
