
from SpoonacularCLI.spoonacular_client import SpoonacularClient

if __name__ == "__main__":
    spoonacular_client = SpoonacularClient()
    ingredient_list = spoonacular_client.get_ingredients_from_user()
    spoonacular_client.recommend_recipies(ingredient_list=ingredient_list)
    spoonacular_client.process_missing_ingredients()

