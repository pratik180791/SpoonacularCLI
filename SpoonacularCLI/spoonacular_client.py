import ast
import json
from typing import List, Optional
from urllib import parse

import pandas as pd
import requests

from .helpers.file_helper import get_generic_configs
from .settings.authentication_handler import AuthenticationHandler
from .utils.exception import InvalidInputException


class SpoonacularClient:
    def __init__(self):
        self.api_key = AuthenticationHandler().api_key()
        self.base_url = self.configs["spoonacularUrl"]
        self.ingredient_list = set()
        self.shopping_list = []
        print(self.configs["startMessage"])

    @property
    def configs(self):
        return get_generic_configs()

    def get_ingredients_from_user(self) -> set:
        ingredient_list = set()
        while True:
            ingredient_name = ""
            while True:
                ingredient_name = input(self.configs["inputRequest"])
                if not ingredient_name:
                    print(self.configs["invalidIngredient"])
                    continue
                break
            ingredient_list.add(ingredient_name.lower().strip())
            continue_ingredients = input(self.configs["ingredientsContinue"])
            if not continue_ingredients or continue_ingredients.lower().strip() not in (
                "yes",
                "y",
                "no",
                "n",
            ):
                while True:
                    print(self.configs["invalidInput"])
                    continue_ingredients = input(self.configs["ingredientsContinue"])
                    if continue_ingredients.strip() in ("yes", "y", "no", "y"):
                        break
            if continue_ingredients.lower() in ("no", "n"):
                break
        print(self.configs["getRecipes"].format(ingredient_list=ingredient_list))
        self.ingredient_list = ingredient_list
        return self.ingredient_list

    def get_recipes(self, ingredient: str, num_of_results: int = 100) -> List:
        """
        :param ingredient: Name of the ingredient which needs to be searched
        :param num_of_results: Total number of results requested from api
        :return: List of in
        """
        try:
            if not ingredient:
                raise InvalidInputException("Ingredient cannot be empty")
            api_url = parse.urljoin(self.base_url, "recipes/findByIngredients")
            params = {
                "ingredients": ingredient,
                "number": num_of_results,
                "limitLicense": True,
                "ranking": 2,
                "apiKey": self.api_key,
            }
            resp = requests.get(api_url, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as exp:
            print(str(exp))
            pass

    def recommend_recipies(self, ingredient_list: set):
        for ingredient in ingredient_list:
            all_recipes = self.get_recipes(ingredient)
            for recipe in all_recipes:
                print(recipe["title"])
                like_dislike = input(self.configs["recipeLikeDislike"])
                while True:
                    if not like_dislike or like_dislike.lower().strip() not in (
                        "yes",
                        "y",
                        "no",
                        "n",
                    ):
                        print(self.configs["invalidInput"])
                        like_dislike = input(self.configs["recipeLikeDislike"])
                    else:
                        break
                if like_dislike.lower() in ("no", "n"):
                    break
                else:
                    self.shopping_list.extend(recipe["missedIngredients"])

    def process_missing_ingredients(self):
        total_amount = 0
        final_list = []
        cnt = 1
        for i in self.shopping_list:
            total_amount += i["amount"]
            final_list.append(
                {
                    "SrNo": cnt,
                    "Name": i["name"],
                    "Aisle name": i["aisle"],
                    "Unit": i["unit"],
                    "Amount": str(i["amount"]) + "$",
                }
            )
            cnt += 1
        presented_shopping_list = self.format_list_to_dataframe(json.dumps(final_list))
        print(presented_shopping_list)
        print(f"Your total shopping amount will be: {total_amount}$")

    @staticmethod
    def format_list_to_dataframe(shopping_list: str) -> Optional[str]:
        val = ast.literal_eval(shopping_list)
        val1 = json.loads(json.dumps(val))
        pd.set_option("colheader_justify", "right")
        val1 = pd.DataFrame(val1)
        return val1.to_markdown(index=False, tablefmt="grid")
