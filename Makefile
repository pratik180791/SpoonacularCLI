.PHONY: virtual install build-requirements black isort flake8

virtual: .venv/bin/pip

default:
	python3 main.py

.venv/bin/pip:
	virtualenv -p /usr/bin/python3 .venv

install:
	.venv/bin/pip install -Ur requirements.txt

setup: setup.py install isort black flake8

run: setup default

test:
	python3 -m pytest --cov=SpoonacularCLI tests/

update-requirements: install
	.venv/bin/pip freeze > requirements.txt

.venv/bin/black: # Installs black code formatter
	.venv/bin/pip install -U black

.venv/bin/isort: # Installs isort to sort imports
	.venv/bin/pip install -U isort

.venv/bin/flake8: # Installs flake8 code linter
	.venv/bin/pip install -U flake8

black: .venv/bin/black # Formats code with black
	.venv/bin/black SpoonacularCLI/*.py

isort: .venv/bin/isort # Sorts imports using isort
	.venv/bin/isort SpoonacularCLI/*.py

flake8: .venv/bin/flake8 # Lints code using flake8
	.venv/bin/flake8 --max-line-length=120 SpoonacularCLI/*.py
