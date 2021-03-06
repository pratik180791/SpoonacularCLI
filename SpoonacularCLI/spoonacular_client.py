import json
from enum import Enum
from typing import Dict, List
from urllib import parse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from SpoonacularCLI.utils.authentication_handler import AuthenticationHandler

from .helpers.generic_helpers import (
    format_list_to_dataframe,
    get_generic_configs,
    validate_input,
)
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
        self.user_stats = {}
        self.shopping_list = []

    @staticmethod
    def requests_retry_session(
        retries=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504, 599]
    ):
        """

        :param retries: Number of retries
        :param backoff_factor: Backoff factor for retries
        :param status_forcelist: HTTP Status forcelist to perform retries
        :return: session Object
        """
        session = requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    @property
    def configs(self):
        return get_generic_configs()

    def get_ingredients_from_user(self) -> set:
        ingredient_list = set()
        while True:
            ingredient_name = validate_input(
                input_message=self.configs["inputRequest"],
                invalid_message=self.configs["invalidIngredient"],
            )
            ingredient_list.add(ingredient_name.lower().strip())
            continue_ingredients = validate_input(
                invalid_message=self.configs["invalidInput"],
                input_message=self.configs["ingredientsContinue"],
                acceptable_values=SpoonacularEnums.YES.value
                + SpoonacularEnums.NO.value,
            )

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
            resp = SpoonacularClient.requests_retry_session().get(
                api_url, params=params
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exp:
            print(str(exp))
            pass

    @staticmethod
    def filter_recipe_output(recipe: Dict) -> List:
        if not recipe:
            return []

        all_ingredients = []
        for ingredients in recipe["usedIngredients"] + recipe["missedIngredients"]:
            all_ingredients.append(
                {
                    "Ingredient Name": ingredients["name"],
                    "Usage Description": ingredients["original"],
                }
            )
        return [
            {
                "Recipe Name": recipe["title"],
                "Total Number Of Ingredients": recipe.get("usedIngredientCount", 0)
                + recipe.get("missedIngredientCount", 0),
                "Recipe Details": json.dumps(all_ingredients),
            }
        ]

    def recommend_recipies(self, ingredient_list: set) -> List:
        """
        This method does an GET request call to spoonacular API to present user
        with a set of recipes in a formatted way.
        It applies a descending order sorting based on fetched recipes with key as number of likes in api.
        That way user views most popular recipes first
        :param ingredient_list: List of ingredients chosen by a user
        :return: List of missing ingredients of the recipes user liked
        """
        all_recipes = []
        liked_count, total_count = 0, 0

        for ingredient in ingredient_list:
            all_recipes.extend(self.get_recipes(ingredient))

        all_recipes = sorted(all_recipes, key=lambda i: i.get("likes", 0), reverse=True)

        for recipe in all_recipes:
            print("\n")
            recipe_list = self.filter_recipe_output(recipe)
            if recipe_list:
                recipe_list[0]["Recipe Details"] = format_list_to_dataframe(
                    recipe_list[0]["Recipe Details"]
                )
            print(format_list_to_dataframe(json.dumps(recipe_list)))
            print("\n")

            acceptable_values = (
                SpoonacularEnums.YES.value
                + SpoonacularEnums.NO.value
                + [SpoonacularEnums.EXIT.value]
            )
            like_dislike = validate_input(
                input_message=self.configs["recipeLikeDislike"],
                invalid_message=self.configs["invalidInput"],
                acceptable_values=acceptable_values,
            )
            total_count += 1
            if like_dislike.lower().strip() in SpoonacularEnums.YES.value:
                self.shopping_list.extend(recipe["missedIngredients"])
                liked_count += 1

            elif like_dislike.lower().strip() == SpoonacularEnums.EXIT.value:
                break
        self.user_stats = {"liked": liked_count, "total_count": total_count}
        return self.shopping_list

    def process_missing_ingredients(self, shopping_list: List) -> None:
        """

        :param shopping_list: List of missing ingredients added in the shopping list based on user's liked recipes
        :return: Doesn't return anything but prints the formatted output of the missing ingredients added
        to shopping list based on user's selections
        """
        total_amount, cnt, final_list = 0, 1, []

        for i in shopping_list:
            total_amount += i["amount"]
            final_list.append(
                {
                    "SrNo": cnt,
                    "Name": i["name"],
                    "Aisle name": i["aisle"],
                    "Unit": i["unit"],
                    "Amount": str(round(i["amount"], 2)) + "$",
                }
            )
            cnt += 1
        presented_shopping_list = format_list_to_dataframe(json.dumps(final_list))
        print(presented_shopping_list)
        print("\nYour total shopping amount will be: %.2f$" % total_amount)
        print(
            self.configs["thankYouShopping"].format(
                liked_count=self.user_stats["liked"],
                total_count=self.user_stats["total_count"],
            )
        )
