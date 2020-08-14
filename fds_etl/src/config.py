import json
import pathlib

config_filepath = pathlib.Path(__file__).parent.parent.parent / 'config.json'


def load_config() -> dict:
    with open(config_filepath) as f:
        return json.load(f)


CONFIG = load_config()
