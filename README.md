***SpoonacularCLI***

SpoonacularCLI is an interactive tool to choose from a wide range of food recipes based on the provided ingredient, on exit, display the chosen recipe’s missing ingredients and stop the shopping experience.

[User documentation](https://github.com/pratik180791/SpoonacularCLI/blob/main/docs/SpoonacularCLI.pdf)


**HOW TO**
1. Open a terminal directly or through any of your favorite IDEs (PyCharm/VSCode)
2. Type in `git clone https://github.com/pratik180791/SpoonacularCLI.git`
3. Step 2 will clone down the repo for you. Once done you can check if the repository root folder `SpoonacularCLI` is created using two ways.
   * Running `ls` command if you are on Mac/Linux or in an IDE terminal
   * By Simply checking the folder structure through windows explorer if on WindowsOS
4. Once confirmed that the project is cloned, please run `cd SpoonacularCLI` on your terminal 
5. If you are reading this, you probably made it to the point of cloning and entering in the project root folder.
6. Stay on the terminal and run `pwd`, it should return something a path ending with `/SpoonacularCLI`
7. Run each command sequentially once its previous command completes its execution.
    *   `make virtual`: This will create a new python3 virtual environment for you
    *   `source .venv/bin/activate`: This will activate the virtual environment we just created above
    *   `make run`: This step will do a below tasks for you. 
        *  First: Install all the dependencies needed for the project. 
        *  Second: Run `isort` for sorting the imports in the project 
        *  Third: Run `flake8` to check for linting issues and does auto code formatting to make the codebase look clean
        *  Finally, it"ll actually run the project entry point script. Once run, you should below message on your terminal 
           `Welcome to Spoonacular - we are excited to serve you with some delicious recipes!!!`
        

**Testing**
   * Run `make test` to run unit tests and see coverage report

   
