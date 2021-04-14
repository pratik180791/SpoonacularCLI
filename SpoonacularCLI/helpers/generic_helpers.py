import os
import json
from typing import Optional
import ast
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_generic_configs() -> json:
    """
    :return: Returns a config json which has standard messages, api references and other details
    """
    try:
        with open(os.path.join(BASE_DIR, "settings/configs.json")) as config_file:
            return json.load(config_file)
    except OSError as ose:
        print("File not found error %s", str(ose))
        return {}


def format_list_to_dataframe(json_string: str) -> Optional[str]:
    """
    :param json_string: Takes in input json in form of a string value
    :return: Formatted tabular output of the json sent
    """
    val = ast.literal_eval(json_string)
    val1 = json.loads(json.dumps(val))
    pd.set_option("colheader_justify", "right")
    val1 = pd.DataFrame(val1)
    return val1.to_markdown(index=False, tablefmt="grid")


def validate_input(input_message: str, invalid_message: str, acceptable_values: list = None
) -> str:
    while True:
        try:
            input_value = input(input_message)
            if not input_value:
                raise ValueError
            if acceptable_values:
                if input_value.lower().strip() in acceptable_values:
                    return input_value
                raise ValueError
            return input_value
        except ValueError:
            print(invalid_message)
