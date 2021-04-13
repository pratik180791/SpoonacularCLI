from SpoonacularCLI.spoonacular_client import SpoonacularClient, SpoonacularEnums
from unittest import TestCase
from unittest.mock import patch
import pytest
import json
import os

BASE_DIR = os.path.dirname((os.path.abspath(__file__)))


class TestSpoonacularClient(TestCase):
    def setUp(self) -> None:
        self.SpoonacularClient = SpoonacularClient()
        self.configs = self.SpoonacularClient.configs

        with open(os.path.join(BASE_DIR, "data/api_response.json")) as api_resp:
            self.api_resp = json.load(api_resp)

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_configs(self):
        test_string = "\nGreat! You entered these ingredients {ingredient_list}, sit back and relax while we get our best recipes just for you!"
        self.assertEqual(self.configs["getRecipes"].format(ingredient_list="sample"),
                         test_string.format(ingredient_list="sample"))
        self.assertIsNotNone(self.configs)

    @patch('builtins.input', return_value="Sample Input")
    def test_validate_input(self, mocked_input):
        output = self.SpoonacularClient.validate_input(input_message="Enter input of your choice",
                                                       invalid_message="Invalid input, please try again")
        self.assertEqual(output, "Sample Input")

    def test_process_missing_ingredients(self):
        missing_ingreds, liked, total_count = [],  0, 5
        for i in range(5):
            missing_ingreds.extend(self.api_resp[i]["missedIngredients"])
        self.SpoonacularClient.user_stats["liked"] = liked
        self.SpoonacularClient.user_stats["total_count"] = total_count
        self.SpoonacularClient.process_missing_ingredients(missing_ingreds)
        out, err = self.capsys.readouterr()
        assert "Your total shopping amount will be: 11.00$" in out
        assert self.configs["thankYouShopping"].format(liked_count=liked, total_count=total_count) in out

    def test_filter_recipe_output(self):
        filtered_output = self.SpoonacularClient.filter_recipe_output({})
        self.assertEqual(filtered_output, [])

        filtered_output = self.SpoonacularClient.filter_recipe_output(self.api_resp[0])
        self.assertIsNotNone(filtered_output)
        expected_output = [{'Recipe Details': '[{"Ingredient Name": "apple", "Usage Description": "apple '
                            'slicer (*optional)"}, {"Ingredient Name": "green apples", '
                            '"Usage Description": "2 green apples"}, {"Ingredient '
                            'Name": "beef broth", "Usage Description": "2 cups beef '
                            'broth"}, {"Ingredient Name": "pork tenderloin", "Usage '
                            'Description": "Pork Tenderloin"}]',
                            'Recipe Name': 'Slow Cooker Apple Pork Tenderloin',
                            'Total Number Of Ingredients': 4}]

        self.assertEqual(filtered_output, expected_output)

    @patch('SpoonacularCLI.spoonacular_client.SpoonacularClient.validate_input')
    @patch('SpoonacularCLI.spoonacular_client.SpoonacularClient.get_recipes')
    def test_recommend_recipies(self, mock1, mock2):
        mock1.return_value = [self.api_resp[0]]
        mock2.return_value = "YES"
        op = self.SpoonacularClient.recommend_recipies({"apple"})
        expected_op = [{'id': 6008, 'amount': 2.0, 'unit': 'cups', 'unitLong': 'cups',
                        'unitShort': 'cup', 'aisle': 'Canned and Jarred', 'name': 'beef broth',
                        'original': '2 cups beef broth', 'originalString': '2 cups beef broth',
                        'originalName': 'beef broth', 'metaInformation': [], 'meta': [],
                        'image': 'https://spoonacular.com/cdn/ingredients_100x100/beef-broth.png'},
                       {'id': 10218, 'amount': 1.0, 'unit': 'serving', 'unitLong': 'serving', 'unitShort':
                           'serving', 'aisle': 'Meat', 'name': 'pork tenderloin', 'original':
                           'Pork Tenderloin', 'originalString': 'Pork Tenderloin', 'originalName':
                           'Pork Tenderloin', 'metaInformation': [], 'meta': [],
                        'image': 'https://spoonacular.com/cdn/ingredients_100x100/pork-tenderloin-raw.png'}]

        self.assertEqual(op, expected_op)
