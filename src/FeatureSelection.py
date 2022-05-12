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
#      Update: 2022/05/12 19:15:14 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

import geopandas
from matplotlib import pyplot as plt
import plotly.express as px
import seaborn as sns
import re

from src.FeatureSelectionMethods.PearsonCorrelation import PearsonCorrelation

class FeatureSelection:
    _stations_dataframe = None
    _stations_geometry_column = 'geometry'
    _stations_name_column = None

    _background_shape = None

    _feature_selection_method_objects = None
    _last_used_methods = None
    _last_used_targets = None
    
    def __init__(self):
        self._feature_selection_method_objects = [PearsonCorrelation()]

    def register_stations(self, stations_dataframe, lon_column='lon', lat_column='lat', geometry_column=None, name_column=None):
        self._stations_dataframe = stations_dataframe
        self._stations_name_column = name_column

        if geometry_column:
            self._stations_geometry_column = geometry_column
        else:
            self._stations_dataframe['geometry'] = geopandas.points_from_xy(self._stations_dataframe[lon_column], self._stations_dataframe[lat_column])
            self._stations_geometry_column = 'geometry'
            self._stations_dataframe = self._stations_dataframe.drop(columns=[lon_column, lat_column])

        self._stations_dataframe =  geopandas.GeoDataFrame(self._stations_dataframe, geometry=self._stations_dataframe[self._stations_geometry_column])
    
    def register_background_shape_file(self, shape_file_path):
        self._background_shape = geopandas.read_file(shape_file_path)

    def plot_stations(self):
        fig = px.scatter_geo(self._stations_dataframe, 
                lat=self._stations_dataframe[self._stations_geometry_column].y, 
                lon=self._stations_dataframe[self._stations_geometry_column].x,     
                size_max=15,
                hover_name=self._stations_name_column,
                fitbounds='locations',
                title = 'Registered stations',
                basemap_visible=True,
        )
    
        fig.show()

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

    def plot(self):
        stations_importances = self.get_stations_importance(self._last_used_targets[0], 'PearsonCorrelation')
        gdf = geopandas.GeoDataFrame(stations_importances, geometry=self._stations_dataframe[self._stations_geometry_column], crs='EPSG:4326')
        map = gdf.explore(
            column='max_importance_value',
            # cmap=plt.cm.get_cmap('turbo'),
            legend=True,
            marker_kwds=dict(radius=10, fill=True),
            vmin=0,
            vmax=1,
            tiles='CartoDB dark_matter',
            tooltip=self._stations_name_column,
            tooltip_kwds=dict(labels=False),
        )
        # gdf.plot(ax=ax1, column='max_importance_value', legend=True, markersize=(stations_importances['nb_important_sensors'] * 40 + 5), cmap=plt.cm.get_cmap('turbo'), vmin=0, vmax=1)
        return map
      
        
    def get_features_importance(self):
        method_names = self._last_used_methods

        methods = self._feature_selection_method_objects if not method_names else [method for method in self._feature_selection_method_objects if method.get_method_name() in method_names]
        return dict(zip([method.get_method_name() for method in methods], [method.get_features_importance() for method in methods]))
    
    def get_stations_importance(self, target, method):
        stations_importance = self._stations_dataframe.copy()
        stations_importance['nb_important_sensors'] = 0
        stations_importance['max_importance_value'] = 0
        score = self.get_features_importance()[method]
        for index in score.index:
            x = re.search("station_([0-9]+)", index)
            if x:
                station_id = int(x.group(1))
                importance_value = score[target][index]
                stations_importance.loc[stations_importance['numero_station'] == station_id, 'nb_important_sensors'] += 1
                stations_importance.loc[(stations_importance['numero_station'] == station_id) & (stations_importance['max_importance_value'] < importance_value), 'max_importance_value'] = importance_value 

        return stations_importance

    def get_available_methods(self):
        return [method.get_method_name for method in self._feature_selection_method_objects]