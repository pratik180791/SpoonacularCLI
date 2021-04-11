from SpoonacularCLI.helpers import file_helper

if __name__ == "__main__":
    configs = file_helper.get_generic_configs()
    ingredient_list = set()
    print(configs["startMessage"])
    while True:
        ingredient_name = ""
        while True:
            ingredient_name = input(configs["inputRequest"])
            if not ingredient_name:
                print(configs["invalidIngredient"])
                continue
            break
        ingredient_list.add(ingredient_name.lower().strip())
        continue_ingredients = input(configs["ingredientsContinue"])
        if not continue_ingredients or continue_ingredients.lower().strip() not in ("yes", "y", "no", "y"):
            while True:
                print(configs["invalidInput"])
                continue_ingredients = input(configs["ingredientsContinue"])
                if continue_ingredients.strip() in ("yes", "y", "no", "y"):
                    break
        if continue_ingredients.lower() in ("no", "n"):
            break
    print(configs["getRecipes"].format(ingredient_list=ingredient_list))
