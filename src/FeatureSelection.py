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
#      Update: 2022/05/14 15:19:54 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

import geopandas
from matplotlib import pyplot as plt
import plotly.express as px
import seaborn as sns
import re
import folium
import wrapt
import contextily as ctx

from src.FeatureSelectionMethods.PearsonCorrelation import PearsonCorrelation

class FeatureSelection:
    _stations_dataframe = None
    _stations_geometry_column = 'geometry'
    _stations_name_column = None
    _stations_id_column = None
    _stations_get_id_from_sensor_regex = None
    _stations_crs = None

    _background_shape = None

    _feature_selection_method_objects = None
    _last_used_methods = None
    _last_used_targets = None
    
    def __init__(self):
        self._feature_selection_method_objects = [PearsonCorrelation()]

    def register_stations(self, stations_dataframe, id_column, get_id_from_sensor_regex, lon_column='lon', lat_column='lat', geometry_column=None, name_column=None, crs='EPSG:4326'):
        self._stations_dataframe = stations_dataframe
        self._stations_name_column = name_column
        self._stations_id_column = id_column
        self._stations_get_id_from_sensor_regex = get_id_from_sensor_regex
        self._stations_crs = crs

        if geometry_column:
            self._stations_geometry_column = geometry_column
        else:
            self._stations_dataframe.loc[:, 'geometry'] = geopandas.points_from_xy(self._stations_dataframe.loc[:, lon_column], self._stations_dataframe.loc[:, lat_column])
            self._stations_geometry_column = 'geometry'
            self._stations_dataframe = self._stations_dataframe.drop(columns=[lon_column, lat_column])

        self._stations_dataframe =  geopandas.GeoDataFrame(self._stations_dataframe, geometry=self._stations_dataframe[self._stations_geometry_column], crs=crs)
    
    def register_background_shape_file(self, shape_file_path):
        self._background_shape = geopandas.read_file(shape_file_path)

    def explore_stations(self):
        map = self._stations_dataframe.explore(
            column=self._stations_id_column,
            categorical=True,
            legend=True,
            popup=True,
            marker_kwds=dict(radius=5, fill=True),
            tiles='CartoDB dark_matter',
            tooltip_kwds=dict(labels=True)
        )
        return map

    def _get_feature_selection_object_by_name(self, name):
        for method in self._feature_selection_method_objects:
            if method.get_method_name() == name:
                return method
        return None
        
    def select(self, dataframe, target_columns, method_names=None):
        methods = self._feature_selection_method_objects if not method_names else [method for method in self._feature_selection_method_objects if method.get_method_name() in method_names]

        for method in methods:
            method.select(dataframe, target_columns)
        
        self._last_used_methods = [method.get_method_name() for method in methods]
        self._last_used_targets = target_columns

    def explore(self, used_target, used_method):
        # overide of the stylefunction, should be added soon as a Geopandas feature.
        @wrapt.patch_function_wrapper(folium, "GeoJson")
        def new_style(wrapped, instance, args, kwargs):
            def style_fn(x):
                return {
                    "fillColor": x["properties"]["__folium_color"],
                    "color": x["properties"]["__folium_color"],
                    "radius": x["properties"]["nb_important_sensors"] + 1,
                    "fillOpacity":.8
                }

            if "_style_column" in str(kwargs["style_function"]):
                kwargs["style_function"] = style_fn
            return wrapped(*args, **kwargs)

        stations_importance = self.get_stations_importance(used_target, used_method)
        map = stations_importance.explore(
            column='max_importance_value',
            legend=True,
            marker_kwds=dict(radius=10, fill=True),
            vmin=0,
            vmax=1,
            tiles='CartoDB dark_matter',
            tooltip=[self._stations_name_column, self._stations_id_column, 'sensors'],
            popup=[self._stations_name_column, self._stations_id_column, 'sensors'],
            tooltip_kwds=dict(labels=True)
        )
        return map
      
    def plot(self, used_targets=None, used_methods=None):
        if not used_targets:
            used_targets = self._last_used_targets
        if not used_methods:
            used_methods = self._last_used_methods
        if len(used_methods) > 1 and len(used_targets) > 1:
            raise NotImplementedError('Cannot plot results for multiple methods and multiple targets at once yet...')

        if len(used_methods) > 1:
            fig, axs = plt.subplots(len(used_methods), 2, figsize=(30, 10 * len(used_methods)), gridspec_kw={'width_ratios':[3,1]})
            fig.suptitle(f"Feature importance visualization for the target {used_targets[0]}", fontsize=36)
            for i, method in enumerate(used_methods):
                self._plot(used_targets[0], method, axs[i, 0], axs[i, 1], title=f"Stations importance for the method {method}")
        elif len(used_targets) > 1:   
            fig, axs = plt.subplots(len(used_targets), 2, figsize=(30, 10 * len(used_targets)), gridspec_kw={'width_ratios':[3,1]})
            fig.suptitle(f"Feature importance visualization for the method {used_methods[0]}", fontsize=36)
            for i, target in enumerate(used_targets):
                self._plot(target, used_methods[0], axs[i, 0], axs[i, 1], title=f"Stations importance for the target {target}")
        else:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(30, 10), gridspec_kw={'width_ratios':[3,1]})
            fig.suptitle(f"Feature importance visualization for the method {used_methods[0]} and the target {used_targets[0]}", fontsize=36)
            self._plot(used_targets[0], used_methods[0], ax1, ax2)

       

    def _plot(self, target, method, ax1, ax2, title="Stations importance"):
        stations_importance = self.get_stations_importance(target, method)
        stations_importance = stations_importance.to_crs(epsg=3857) # change to Spherical Mercator to add ctx base map properly
        features_importance = self.get_features_importance()
        stations_importance.plot(ax=ax1, column='max_importance_value', legend=True, markersize=(stations_importance['nb_important_sensors'] * 40 + 5), cmap=plt.cm.get_cmap('plasma'), vmin=0, vmax=1)
        ax1.set_xlabel('Longitude', fontsize=10)
        ax1.set_ylabel('Latitude', fontsize='medium')
        ax1.set_title(title)
        ctx.add_basemap(ax1, source=ctx.providers.CartoDB.Positron)
        for x, y, label, offsetY in zip(stations_importance.geometry.x, stations_importance.geometry.y, stations_importance[self._stations_id_column], stations_importance['nb_important_sensors'] + 5):
            ax1.annotate(label, xy=(x, y), xytext=(0, offsetY), textcoords="offset points")

        features_importance = features_importance[method].dropna().sort_values(by=[target], ascending=False)
        sns.heatmap(features_importance[[target]], ax=ax2, annot=True, linewidths=.5, cmap=plt.cm.get_cmap('plasma'), cbar=False, vmin=0, vmax=1)

    def get_features_importance(self):
        method_names = self._last_used_methods

        methods = self._feature_selection_method_objects if not method_names else [method for method in self._feature_selection_method_objects if method.get_method_name() in method_names]
        return dict(zip([method.get_method_name() for method in methods], [method.get_features_importance() for method in methods]))
    
    def get_stations_importance(self, target, method):
        stations_importance = self._stations_dataframe.copy()
        stations_importance['nb_important_sensors'] = 0
        stations_importance['max_importance_value'] = 0
        stations_importance['sensors'] = ''
        score = self.get_features_importance()[method]
        for index in score.index:
            x = re.search(self._stations_get_id_from_sensor_regex, index)
            if x:
                station_id = int(x.group(1))
                importance_value = score[target][index]
                stations_importance.loc[stations_importance[self._stations_id_column] == station_id, 'nb_important_sensors'] += 1
                stations_importance.loc[stations_importance[self._stations_id_column] == station_id, 'sensors'] += f"{index} : {'{:.2f}'.format(importance_value)}\n</br>"
                stations_importance.loc[(stations_importance[self._stations_id_column] == station_id) & (stations_importance['max_importance_value'] < importance_value), 'max_importance_value'] = importance_value 

        return stations_importance

    def get_available_methods(self):
        return [method.get_method_name for method in self._feature_selection_method_objects]