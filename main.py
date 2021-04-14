
from SpoonacularCLI.spoonacular_client import SpoonacularClient

if __name__ == "__main__":
    try:
        spoonacular_client = SpoonacularClient()
        ingredient_list = spoonacular_client.get_ingredients_from_user()
        shopping_list = spoonacular_client.recommend_recipies(ingredient_list=ingredient_list)
        spoonacular_client.process_missing_ingredients(shopping_list=shopping_list)
    except Exception as exp:
        print("Something went wrong on our side. Please restart our app")
