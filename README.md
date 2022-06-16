# Network_of_sensors-Feature_Selection

## Motivation

This repository shows the work done in a project at the University Of Technology Of Compiègne. Done by Stéphane BRANLY and Ismail KADIRI (Artificial Intelligence and Data Science Students). Project under the supervision of Gilles MOREL (Research and development in neuro-symbolic AI for the smart city).

The goal of this project is to find solutions to operate feature selection on large network of sensors (temporal and spatial aspects) in order to improve machine learning results and reduce the complexity of calculations.

## Use the module

The module is not yet published as a `pip` or `conda` module but you can use it.
Copy the directory `src` and check the [documentation](https://stephanebranly.github.io/Network_of_sensors-Feature_Selection/) or the dedicated section in the [notebook](./TX_notebook.ipynb) to use the module.
Don't forget to install module requirements to use it.
```shell
pip3 install -r requirements.txt
```

## Contribute to the module

You can open `issues`, create `pull requests`.

### Install dev-requirements

```shell
pip3 install -r dev-requirements.txt
```

### Add Feature Selection method

1. Create a python file in the directory `./src/FeatureSelectionMethods`
2. Create a new class which extends the class `TemplateMethod`
3. Implement your needed feature selection method (the `select` method must be overided). You can check the simple example of [PearsonCorrelation](./src/FeatureSelectionMethods/PearsonCorrelation.py) to see how to properly implement your method.
```python
def select(self, dataframe, target_columns, number_of_target_to_keep=1):
    target_correlation = dataframe.corr()[target_columns]
    self._score = abs(target_correlation)

    self._selected_features = dict()
    for target_column in target_columns:
        self._selected_features[target_column] = list(
            self._score.sort_values(by=target_column, ascending=False)[
                :number_of_target_to_keep
            ].index
        )
```
4. Register an instance of this new class in the main class `FeatureSelection`
```python
from src.FeatureSelectionMethods.PearsonCorrelation import PearsonCorrelation
# ...
def __init__(self):
    self._feature_selection_method_objects = [
        PearsonCorrelation(),
        GrangerCausality(),
    ]
```

### Generate requirements.txt file

The requirements file need to be generated manually. For this, follow the steps :

1. Install the package `pipreqs`
```shell
pip3 install pipreqs
```
2. Generate the file by running the command
```shell
pipreqs ./src --force
```

### Contribute in the repository

If you want to contribute and add your module in this repository.
1. Create and work on a dedicated branch (you can `fork` the project or ask for permissions)
2. Commit your changes (a `pre-commit` command will be runned to format the code with `black`)
3. Create a pull request to merge on the main branch (a test will be runned to check if the code is properly formatted)
4. The documentation will be automatically updated when the branch will be merged in the main (check [documentation action](./.github/workflows/documentation.yml))