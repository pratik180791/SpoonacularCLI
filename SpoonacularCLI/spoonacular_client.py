import ast
import json
from enum import Enum
from typing import List, Optional, Dict
from urllib import parse

import pandas as pd
import requests

from .helpers.file_helper import get_generic_configs
from .settings.authentication_handler import AuthenticationHandler
from .utils.exception import InvalidInputException


class SpoonacularEnums(Enum):
    YES = ["yes", "y"]
    NO = ["no", "n"]
    EXIT = "exit"


class SpoonacularClient:
    def __init__(self):
        print(self.configs["startMessage"])
        self.api_key = AuthenticationHandler().api_key()
        self.base_url = self.configs["spoonacularUrl"]
        self.shopping_list = []
        self.user_stats = {}

    @property
    def configs(self):
        return get_generic_configs()

    def validate_input(self, input_message, invalid_message, acceptable_values=None) -> str:
        while True:
            input_value = input(input_message)
            if not input_value:
                print(invalid_message)
                continue
            if acceptable_values:
                if input_value.lower().strip() in acceptable_values:
                    return input_value
                else:
                    print(invalid_message)
                    continue
            break
        return input_value

    def get_ingredients_from_user(self) -> set:
        ingredient_list = set()
        while True:
            ingredient_name = self.validate_input(input_message=self.configs["inputRequest"],
                                                  invalid_message=self.configs["invalidIngredient"])
            ingredient_list.add(ingredient_name.lower().strip())
            continue_ingredients = self.validate_input(invalid_message=self.configs["invalidInput"],
                                                       input_message=self.configs["ingredientsContinue"],
                                                       acceptable_values=SpoonacularEnums.YES.value +
                                                                         SpoonacularEnums.NO.value)

            if continue_ingredients.lower() in SpoonacularEnums.NO.value:
                break
        print(self.configs["getRecipes"].format(ingredient_list=ingredient_list))
        return ingredient_list

    def get_recipes(self, ingredient: str, num_of_results: int = 100) -> List:
        """
        :param ingredient: Name of the ingredient which needs to be searched
        :param num_of_results: Total number of results requested from api
        :return: List of recipes matching the given ingredient
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

    def filter_recipe_output(self, recipe: Dict) -> List:
        if not recipe:
            return []

        all_ingredients = []
        for ingredients in recipe["usedIngredients"] + recipe["missedIngredients"]:
            all_ingredients.append({"Ingredient Name": ingredients["name"],
                                    "Usage Description": ingredients["original"]})
        return [{"Recipe Name": recipe["title"],
                 "Total Number Of Ingredients": recipe.get("usedIngredientCount", 0) + recipe.get(
                     "missedIngredientCount", 0),
                "Recipe Details": json.dumps(all_ingredients)}
                ]

    def recommend_recipies(self, ingredient_list: set):
        all_recipes = []
        liked_count = 0
        total_count = 0
        for ingredient in ingredient_list:
            all_recipes.extend(self.get_recipes(ingredient))

        #Sort recipies based on popularity(Number of likes)
        all_recipes = sorted(all_recipes, key=lambda i: i.get('likes', 0), reverse=True)

        for recipe in all_recipes:
            print("\n")
            recipe_list = self.filter_recipe_output(recipe)
            if recipe_list:
                recipe_list[0]["Recipe Details"] = self.format_list_to_dataframe(recipe_list[0]["Recipe Details"])
            print(self.format_list_to_dataframe(json.dumps(recipe_list)))
            print("\n")

            acceptable_values = SpoonacularEnums.YES.value + SpoonacularEnums.NO.value + [SpoonacularEnums.EXIT.value]
            like_dislike = self.validate_input(input_message=self.configs["recipeLikeDislike"],
                                               invalid_message=self.configs["invalidInput"],
                                               acceptable_values=acceptable_values)
            total_count += 1
            if like_dislike.lower().strip() in SpoonacularEnums.YES.value:
                self.shopping_list.extend(recipe["missedIngredients"])
                liked_count += 1

            if like_dislike.lower().strip() == SpoonacularEnums.EXIT.value:
                self.shopping_list.extend(recipe["missedIngredients"])
                break
        self.user_stats = {"liked": liked_count, "total_count": total_count}

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
        print("\nYour total shopping amount will be: %.2f$" % total_amount)
        print(self.configs["thankYouShopping"].format(liked_count=self.user_stats["liked"],
                                                      total_count=self.user_stats["total_count"]))

    @staticmethod
    def format_list_to_dataframe(shopping_list: str) -> Optional[str]:
        val = ast.literal_eval(shopping_list)
        val1 = json.loads(json.dumps(val))
        pd.set_option("colheader_justify", "right")
        val1 = pd.DataFrame(val1)
        return val1.to_markdown(index=False, tablefmt="grid")
