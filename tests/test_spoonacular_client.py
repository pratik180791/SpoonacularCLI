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
            self.mocked_api_response = json.load(api_resp)

        self.mock_recommended_output = [{'id': 6008, 'amount': 2.0, 'unit': 'cups', 'unitLong': 'cups', 'unitShort': 'cup', 'aisle': 'Canned and Jarred', 'name': 'beef broth', 'original': '2 cups beef broth', 'originalString': '2 cups beef broth', 'originalName': 'beef broth', 'metaInformation': [], 'meta': [], 'image': 'https://spoonacular.com/cdn/ingredients_100x100/beef-broth.png'}, {'id': 10218, 'amount': 1.0, 'unit': 'serving', 'unitLong': 'serving', 'unitShort': 'serving', 'aisle': 'Meat', 'name': 'pork tenderloin', 'original': 'Pork Tenderloin', 'originalString': 'Pork Tenderloin', 'originalName': 'Pork Tenderloin', 'metaInformation': [], 'meta': [], 'image': 'https://spoonacular.com/cdn/ingredients_100x100/pork-tenderloin-raw.png'}]

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_configs(self):
        test_string = "\nGreat! You entered these ingredients {ingredient_list}, sit back and relax while we get our best recipes just for you!"
        self.assertEqual(self.configs["getRecipes"].format(ingredient_list="sample"),
                         test_string.format(ingredient_list="sample"))
        self.assertIsNotNone(self.configs)

    def test_process_missing_ingredients(self):
        missing_ingredients, liked, total_count = [],  0, 5
        for i in range(5):
            missing_ingredients.extend(self.mocked_api_response[i]["missedIngredients"])
        self.SpoonacularClient.user_stats["liked"] = liked
        self.SpoonacularClient.user_stats["total_count"] = total_count
        self.SpoonacularClient.process_missing_ingredients(missing_ingredients)
        out, err = self.capsys.readouterr()
        assert "Your total shopping amount will be: 11.00$" in out
        assert self.configs["thankYouShopping"].format(liked_count=liked, total_count=total_count) in out

    def test_filter_recipe_output(self):
        filtered_output = self.SpoonacularClient.filter_recipe_output({})
        self.assertEqual(filtered_output, [])
        filtered_output = self.SpoonacularClient.filter_recipe_output(self.mocked_api_response[0])
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

    def test_filter_recipe_output_no_input(self):
        filtered_output = self.SpoonacularClient.filter_recipe_output({})
        self.assertEqual(filtered_output, [])
        filtered_output = self.SpoonacularClient.filter_recipe_output({})
        self.assertIsNotNone(filtered_output)
        self.assertEqual(filtered_output, [])

    @patch('SpoonacularCLI.spoonacular_client.validate_input')
    @patch('SpoonacularCLI.spoonacular_client.SpoonacularClient.get_recipes')
    def test_recommend_recipies(self, mocked_recipe, mocked_input):
        mocked_recipe.return_value = [self.mocked_api_response[0]]
        mocked_input.return_value = "YES"
        actual_output = self.SpoonacularClient.recommend_recipies({"apple"})
        self.assertEqual(actual_output, self.mock_recommended_output)

    @patch('SpoonacularCLI.spoonacular_client.validate_input', side_effect=['NO', 'NO', 'YES', 'exit'])
    @patch('SpoonacularCLI.spoonacular_client.SpoonacularClient.get_recipes')
    def test_recommend_recipies_range_inputs(self, mocked_recipe, mocked_input):
        mocked_recipe.return_value = self.mocked_api_response[:3]
        actual_output = self.SpoonacularClient.recommend_recipies({"apple"})
        self.assertEqual(actual_output, self.mock_recommended_output)

    @patch('SpoonacularCLI.spoonacular_client.validate_input')
    @patch('SpoonacularCLI.spoonacular_client.SpoonacularClient.get_recipes')
    def test_recommend_recipies_invalid_inputs(self, mocked_recipes, mocked_input):
        mocked_recipes.return_value = []
        mocked_input.return_value = "YES"
        op = self.SpoonacularClient.recommend_recipies(set())
        self.assertListEqual(op, [])
