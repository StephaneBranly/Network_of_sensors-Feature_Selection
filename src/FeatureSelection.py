# ************************************************************************************************************************* #
#   UTC Header                                                                                                              #
#                                                         ::::::::::::::::::::       :::    ::: :::::::::::  ::::::::       #
#      FeatureSelection.py                                ::::::::::::::::::::       :+:    :+:     :+:     :+:    :+:      #
#                                                         ::::::::::::::+++#####+++  +:+    +:+     +:+     +:+             #
#      By: branlyst and ismailkad < >                     ::+++##############+++     +:+    +:+     +:+     +:+             #
#                                                     +++##############+++::::       +#+    +:+     +#+     +#+             #
#                                                       +++##+++::::::::::::::       +#+    +:+     +#+     +#+             #
#                                                         ::::::::::::::::::::       +#+    +#+     +#+     +#+             #
#                                                         ::::::::::::::::::::       #+#    #+#     #+#     #+#    #+#      #
#      Update: 2022/06/16 19:02:58 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

import geopandas
from matplotlib import pyplot as plt
import seaborn as sns
import re
import folium
import wrapt
import contextily as ctx

from src.FeatureSelectionMethods.PearsonCorrelation import PearsonCorrelation
from src.FeatureSelectionMethods.GrangerCausality import GrangerCausality


class FeatureSelection:
    """
    Feature Selection is a module which permits to apply feature selection methods to a dataframe. It is specialised into geospatial timeseries and provides visualisation functions.

    Attributes:
        _stations_dataframe (GeoDataFrame) : contains the registered stations
        _stations_geometry_column (str) : indicates the column name of _stations_dataframe which contains the geometry of the station
        _stations_name_column (str | None) : indicates the column name of _stations_dataframe which contains the name of the station
        _stations_id_column (str) : indicates the column name of _stations_dataframe which contains the id of the station
        _stations_get_id_from_sensor_regex (str) : regex used to find the station id in the dataframe containing all records used for feature selection
        _stations_crs (str) : current crs of the _stations_dataframe

        _feature_selection_method_objects (TemplateMethod[]) : Array of TemplateMethod implemented objects
        _last_used_methods (str[]) : last used method names
        _last_used_targets (str[]) : last used targets names

    Example:
    ```python
    # Import module
    from src.FeatureSelection import FeatureSelection
    import pandas as pd

    # Import data sample
    data = pd.read_csv('./data/sample.csv', index_col=0)

    # Import stations references
    stations_references = pd.read_csv("./data/liste-des-stations-rsqa.csv")

    # Instanciation of FeatureSelection
    fs = FeatureSelection()

    # Registering the stations
    fs.register_stations(
        stations_references[stations_references['statut'] == 'ouvert'], # Select open stations
        id_column="numero_station", # Indicate the unique id column name
        get_id_from_sensor_regex="station_([0-9]+)", # Indicate how to get this unique id from the data column's names
        lon_column='longitude', # Indicate longitude column
        lat_column='latitude', # Indicate latitude column
        name_column='nom' # Indicate name column
    )
    ```
    """

    _stations_dataframe = None
    _stations_geometry_column = "geometry"
    _stations_name_column = None
    _stations_id_column = None
    _stations_get_id_from_sensor_regex = None
    _stations_crs = None

    _feature_selection_method_objects = None
    _last_used_methods = None
    _last_used_targets = None

    def __init__(self):
        self._feature_selection_method_objects = [
            PearsonCorrelation(),
            GrangerCausality(),
        ]

    def register_stations(
        self,
        stations_dataframe,
        id_column,
        get_id_from_sensor_regex,
        lon_column="lon",
        lat_column="lat",
        geometry_column=None,
        name_column=None,
        crs="EPSG:4326",
    ):
        """
        Register the stations in order to have a visualisation

        Args:
            stations_dataframe (DataFrame | GeoDataFrame) : DataFrame containing the stations
            id_column (str) : column name of the stations_dataframe which contains the unique id of the station
            get_id_from_sensor_regex (str) : regex used to find the station id in the dataframe containing all records used for feature selection
            lon_column (str) : column name of the stations_dataframe which contains the longitude of the station
            lat_column (str) : column name of the stations_dataframe which contains the latitude of the station
            geometry_column (str | None) : if provided and dataframe is a GeoDataFrame, column name of the stations_dataframe which contains the geometry
            name_column (str | None) : if provided, column name of the stations_dataframe which contains the name of the station
            crs (str) : crs used for the location

        Example:
        ```python
        # Import stations references
        stations_references = pd.read_csv("./data/liste-des-stations-rsqa.csv")

        # Registering the stations
        fs.register_stations(
            stations_references[stations_references['statut'] == 'ouvert'], # Select open stations
            id_column="numero_station", # Indicate the unique id column name
            get_id_from_sensor_regex="station_([0-9]+)", # Indicate how to get this unique id from the data column's names
            lon_column='longitude', # Indicate longitude column
            lat_column='latitude', # Indicate latitude column
            name_column='nom' # Indicate name column
        )
        ```
        """

        self._stations_dataframe = stations_dataframe
        self._stations_name_column = name_column
        self._stations_id_column = id_column
        self._stations_get_id_from_sensor_regex = get_id_from_sensor_regex
        self._stations_crs = crs

        if geometry_column:
            self._stations_geometry_column = geometry_column
        else:
            self._stations_dataframe.loc[:, "geometry"] = geopandas.points_from_xy(
                self._stations_dataframe.loc[:, lon_column],
                self._stations_dataframe.loc[:, lat_column],
            )
            self._stations_geometry_column = "geometry"
            self._stations_dataframe = self._stations_dataframe.drop(
                columns=[lon_column, lat_column]
            )

        self._stations_dataframe = geopandas.GeoDataFrame(
            self._stations_dataframe,
            geometry=self._stations_dataframe[self._stations_geometry_column],
            crs=crs,
        )

    def explore_stations(self, **explore_kwargs):
        """
        Explore the different registered stations on an interactive map

        Example:
        ```python
        # Explore the stations
        fs.explore_stations()
        ```
        """
        map = self._stations_dataframe.explore(
            column=self._stations_id_column,
            categorical=True,
            legend=True,
            popup=True,
            marker_kwds=dict(radius=5, fill=True),
            tiles="CartoDB dark_matter",
            tooltip_kwds=dict(labels=True),
            **explore_kwargs,
        )
        return map

    def _get_feature_selection_object_by_name(self, name):
        """
        Private method, get the feature selection method object by is name

        Args:
            name (str) : Feature selection method registered name
        """

        for method in self._feature_selection_method_objects:
            if method.get_method_name() == name:
                return method
        return None

    def select(
        self, dataframe, target_columns, method_names=None, number_of_target_to_keep=1
    ):
        """
        Apply feature selection methods on target_columns for a given dataframe

        Args:
            dataframe (DataFrame) : dataframe which contains the data used to apply the feature selection. 1 column by feature and 1 line by entry
            target_columns (str[]) : array of the target column names used to apply the feature selection
            method_names (str[] | None) : array of the method names to use for feature selection, if None, all registered methods will be applied

        Example:
        ```python
        # Apply a feature selection method (PearsonCorrelation) to the data for the targets pm2_5_station_3 and no_station_3
        fs.select(data, target_columns=['pm2_5_station_3', 'no_station_3'], method_names=['PearsonCorrelation'], number_of_target_to_keep=15)
        ```
        """
        methods = (
            self._feature_selection_method_objects
            if not method_names
            else [
                method
                for method in self._feature_selection_method_objects
                if method.get_method_name() in method_names
            ]
        )

        for method in methods:
            method.select(dataframe, target_columns, number_of_target_to_keep)

        self._last_used_methods = [method.get_method_name() for method in methods]
        self._last_used_targets = target_columns

    def explore(self, used_target, used_method, **explore_kwargs):
        """
        Explore the results of the feature selection on an interactive map for a method and a target. Feature selection (`select()`) must be done before

        Args:
            used_target (str) : the name of the target that we wan't to see (must be referenced in `target_columns` when `select()`)
            used_method (str) : the name of the method that we wan't to see (must be referenced in `method_names` when `select()`, or None used)

        Example:
        ```python
        # Explore the results for the method PearsonCorrelation and the target pm2_5_station_3
        fs.explore(used_target='pm2_5_station_3', used_method='PearsonCorrelation')
        ```
        """

        # overide of the stylefunction, should be added soon as a Geopandas feature.
        @wrapt.patch_function_wrapper(folium, "GeoJson")
        def new_style(wrapped, instance, args, kwargs):
            def style_fn(x):
                return {
                    "fillColor": x["properties"]["__folium_color"],
                    "color": x["properties"]["__folium_color"],
                    "radius": x["properties"]["nb_important_sensors"] + 1,
                    "fillOpacity": 0.8,
                }

            if "_style_column" in str(kwargs["style_function"]):
                kwargs["style_function"] = style_fn
            return wrapped(*args, **kwargs)

        stations_importance = self.get_station_importances(used_target, used_method)
        map = stations_importance.explore(
            column="max_importance_value",
            legend=True,
            marker_kwds=dict(radius=10, fill=True),
            vmin=0,
            vmax=1,
            tiles="CartoDB dark_matter",
            tooltip=[self._stations_name_column, self._stations_id_column, "sensors"],
            popup=[self._stations_name_column, self._stations_id_column, "sensors"],
            tooltip_kwds=dict(labels=True),
            **explore_kwargs,
        )
        return map

    def plot(self, used_targets=None, used_methods=None):
        """
        Plot the results of the feature selection. Feature selection (`select()`) must be done before.
        (Cannot plot results for multiple methods and multiple targets at once)

        Args:
            used_targets (str[] | None) : the name of the targets that we wan't to see (must be referenced in `target_columns` when `select()`). If None, all last used_targets will be used
            used_methods (str[] | None) : the name of the methods that we wan't to see (must be referenced in `method_names` when `select()`, or None used). If None, all last used_methods will be used

        Example:
        ```python
        # Plot the results
        fs.plot()

        # Plot the results only for the target no_station_3
        fs.plot(used_targets=['no_station_3'])
        ```
        """

        if not used_targets:
            used_targets = self._last_used_targets
        if not used_methods:
            used_methods = self._last_used_methods
        if len(used_methods) > 1 and len(used_targets) > 1:
            raise NotImplementedError(
                "Cannot plot results for multiple methods and multiple targets at once yet..."
            )

        if len(used_methods) > 1:
            fig, axs = plt.subplots(
                len(used_methods),
                2,
                figsize=(30, 10 * len(used_methods)),
                gridspec_kw={"width_ratios": [3, 1]},
            )
            fig.suptitle(
                f"Feature importance visualization for the target {used_targets[0]}",
                fontsize=36,
            )
            for i, method in enumerate(used_methods):
                self._plot(
                    used_targets[0],
                    method,
                    axs[i, 0],
                    axs[i, 1],
                    title=f"Stations importance for the method {method}",
                )
        elif len(used_targets) > 1:
            fig, axs = plt.subplots(
                len(used_targets),
                2,
                figsize=(30, 10 * len(used_targets)),
                gridspec_kw={"width_ratios": [3, 1]},
            )
            fig.suptitle(
                f"Feature importance visualization for the method {used_methods[0]}",
                fontsize=36,
            )
            for i, target in enumerate(used_targets):
                self._plot(
                    target,
                    used_methods[0],
                    axs[i, 0],
                    axs[i, 1],
                    title=f"Stations importance for the target {target}",
                )
        else:
            fig, (ax1, ax2) = plt.subplots(
                1, 2, figsize=(30, 10), gridspec_kw={"width_ratios": [3, 1]}
            )
            fig.suptitle(
                f"Feature importance visualization for the method {used_methods[0]} and the target {used_targets[0]}",
                fontsize=36,
            )
            self._plot(used_targets[0], used_methods[0], ax1, ax2)

    def _plot(self, target, method, ax1, ax2, title="Stations importance"):
        """
        Private method. Plot the result for a target and a method. Feature selection (`select()`) must be done before

        Args:
            target (str) : target name (must be referenced in `target_columns` when `select()`)
            method (str) : method name (must be referenced in `method_names` when `select()`, or None used)
            ax1 (Axe) : axe which will contains the map
            ax2 (Axe) : axe which will contains the heatmap
            title (str) : title of the figure
        """

        stations_importance = self.get_station_importances(target, method)
        stations_importance = stations_importance.to_crs(
            epsg=3857
        )  # change to Spherical Mercator to add ctx base map properly
        features_importance = self.get_feature_importances()
        stations_importance.plot(
            ax=ax1,
            column="max_importance_value",
            legend=True,
            markersize=(stations_importance["nb_important_sensors"] * 40 + 5),
            cmap=plt.cm.get_cmap("plasma"),
            vmin=0,
            vmax=1,
        )
        ax1.set_xlabel("Longitude", fontsize=10)
        ax1.set_ylabel("Latitude", fontsize="medium")
        ax1.set_title(title)
        ctx.add_basemap(ax1, source=ctx.providers.CartoDB.Positron)
        for x, y, label, offsetY in zip(
            stations_importance.geometry.x,
            stations_importance.geometry.y,
            stations_importance[self._stations_id_column],
            stations_importance["nb_important_sensors"] + 5,
        ):
            ax1.annotate(
                label, xy=(x, y), xytext=(0, offsetY), textcoords="offset points"
            )

        features_importance = (
            features_importance[method]
            .dropna()
            .sort_values(by=[target], ascending=False)
        )
        sns.heatmap(
            features_importance[[target]],
            ax=ax2,
            annot=True,
            linewidths=0.5,
            cmap=plt.cm.get_cmap("plasma"),
            cbar=False,
            vmin=0,
            vmax=1,
        )

    def get_feature_importances(self):
        """
        Get the features importance. Feature selection (`select()`) must be done before
        """
        method_names = self._last_used_methods

        methods = (
            self._feature_selection_method_objects
            if not method_names
            else [
                method
                for method in self._feature_selection_method_objects
                if method.get_method_name() in method_names
            ]
        )
        return dict(
            zip(
                [method.get_method_name() for method in methods],
                [method.get_feature_importances() for method in methods],
            )
        )

    def get_selected_features(self):
        """
        Get the selected features. Feature selection (`select()`) must be done before

        Example:
        ```python
        # Get access to the selected features for Pearson Correlation method and the target pm2_5_station_3
        fs.get_selected_features()['PearsonCorrelation']['pm2_5_station_3']
        ```
        """
        method_names = self._last_used_methods

        methods = (
            self._feature_selection_method_objects
            if not method_names
            else [
                method
                for method in self._feature_selection_method_objects
                if method.get_method_name() in method_names
            ]
        )
        return dict(
            zip(
                [method.get_method_name() for method in methods],
                [method.get_selected_features() for method in methods],
            )
        )

    def get_station_importances(self, target, method):
        """
        Generates a Stations importance for a target and a method. Feature selection (`select()`) must be done before

        Args:
            target (str) : target name (must be referenced in `target_columns` when `select()`)
            method (str) : method name (must be referenced in `method_names` when `select()`, or None used)
        """
        stations_importance = self._stations_dataframe.copy()
        stations_importance["nb_important_sensors"] = 0
        stations_importance["max_importance_value"] = 0
        stations_importance["sensors"] = ""
        score = self.get_feature_importances()[method]
        for index in score.index:
            x = re.search(self._stations_get_id_from_sensor_regex, index)
            if x:
                station_id = int(x.group(1))
                importance_value = score[target][index]
                stations_importance.loc[
                    stations_importance[self._stations_id_column] == station_id,
                    "nb_important_sensors",
                ] += 1
                stations_importance.loc[
                    stations_importance[self._stations_id_column] == station_id,
                    "sensors",
                ] += f"{index} : {'{:.2f}'.format(importance_value)}\n</br>"
                stations_importance.loc[
                    (stations_importance[self._stations_id_column] == station_id)
                    & (stations_importance["max_importance_value"] < importance_value),
                    "max_importance_value",
                ] = importance_value

        return stations_importance

    def get_available_methods(self):
        """
        Get the name of all registered Feature Selection Methods
        """

        return [
            method.get_method_name()
            for method in self._feature_selection_method_objects
        ]
