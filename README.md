# Network_of_sensors-Feature_Selection

## Contribute to the module

### Install dev-requirements

```shell
pip3 install -r dev-requirements.txt
```

### Add Feature Selection methods

1. Create a python file in the directory `./src/FeatureSelectionMethods`
2. Create a new class which extends the class `TemplateMethod`
3. Implement your needed feature selection method (the `select` method must be overided)
4. Register an instance of this new class in the main class `FeatureSelection`

### Generate requirements.txt file

Install the package `pipreqs`
```shell
pip3 install pipreqs
```

Generate the file by running the command
```shell
pipreqs ./src
```