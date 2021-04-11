import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_generic_configs() -> json:
    """
    :return: Returns a config json which has standard messages, api references and other details
    """
    with open(os.path.join(BASE_DIR, "settings/configs.json")) as config_file:
        return json.load(config_file)
