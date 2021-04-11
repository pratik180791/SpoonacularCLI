from setuptools import find_packages, setup, Command

setup(
    name='Spoonacular App - Spoonappular',
    version='1.0.0',
    packages=find_packages(exclude=["tests"]),
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': [
            'spoonacular_assessment_script = app:main'
        ]
    }
)
