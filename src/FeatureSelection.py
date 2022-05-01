# ************************************************************************************************************************* #
#   UTC Header                                                                                                              #
#                                                         ::::::::::::::::::::       :::    ::: :::::::::::  ::::::::       #
#      featureselection.py                                ::::::::::::::::::::       :+:    :+:     :+:     :+:    :+:      #
#                                                         ::::::::::::::+++#####+++  +:+    +:+     +:+     +:+             #
#      By: branlyst and ismailkad < >                     ::+++##############+++     +:+    +:+     +:+     +:+             #
#                                                     +++##############+++::::       +#+    +:+     +#+     +#+             #
#                                                       +++##+++::::::::::::::       +#+    +:+     +#+     +#+             #
#                                                         ::::::::::::::::::::       +#+    +#+     +#+     +#+             #
#                                                         ::::::::::::::::::::       #+#    #+#     #+#     #+#    #+#      #
#      Update: 2022/05/01 22:36:17 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

import matplotlib.pyplot as plt
import geopandas as gpd

from src.FeatureSelectionMethods.PearsonCorrelation import PearsonCorrelation

class FeatureSelection:
    _stations_dataframe = None
    _stations_geometry_column = 'geometry'
    _stations_name_column = None

    _background_shape = None

    _feature_selection_objects = None
    
    def __init__(self):
        self._feature_selection_objects = [PearsonCorrelation()]

    def register_stations(self, stations_dataframe, lon_column='lon', lat_column='lat', geometry_column=None, name_column=None):
        self._stations_dataframe = stations_dataframe
        self._stations_name_column = name_column

        if geometry_column:
            self._stations_geometry_column = geometry_column
        else:
            self._stations_dataframe['geometry'] = gpd.points_from_xy(self._stations_dataframe[lon_column], self._stations_dataframe[lat_column])
            self._stations_geometry_column = 'geometry'
            self._stations_dataframe = self._stations_dataframe.drop(columns=[lon_column, lat_column])

    def register_background_shape_file(self, shape_file_path):
        self._background_shape = gpd.read_file(shape_file_path)

    def plot_stations(self):
        fig = plt.figure(figsize=(20,20))
        gdf = gpd.GeoDataFrame(self._stations_dataframe, geometry=self._stations_dataframe[self._stations_geometry_column])

        if type(self._background_shape) != type(None):
            ax = self._background_shape.plot(alpha=0.5, edgecolor='k', color='#DDD')
            gdf.plot(ax=ax, markersize=20)
        else:
            ax = gdf.plot(markersize=20)

        ax.set_xlabel('Longitude', fontsize=10)
        ax.set_ylabel('Latitude', fontsize='medium')
        ax.set_title(f"Stations")

        if self._stations_name_column:
            for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf[self._stations_name_column]):
                ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")

    def _get_feature_selection_object_by_name(self, name):
        for method in self._feature_selection_objects:
            if method.get_method_name() == name:
                return method
        return None

    def select(self, dataframe, target_column, method_name=None):
        if method_name:
            feature_selection_object = self._get_feature_selection_object_by_name(method_name)
            feature_selection_object.select(dataframe, target_column)
        else:
            for method in self._feature_selection_objects:
                method.select(dataframe, target_column)