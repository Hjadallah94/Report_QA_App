import yaml
from typing import Dict

def load_rules(path: str) -> Dict:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)