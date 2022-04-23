# ************************************************************************************************************************* #
#   UTC Header                                                                                                              #
#                                                         ::::::::::::::::::::       :::    ::: :::::::::::  ::::::::       #
#      sts_featureselection.py                            ::::::::::::::::::::       :+:    :+:     :+:     :+:    :+:      #
#                                                         ::::::::::::::+++#####+++  +:+    +:+     +:+     +:+             #
#      By: branlyst and ismailkad < >                     ::+++##############+++     +:+    +:+     +:+     +:+             #
#                                                     +++##############+++::::       +#+    +:+     +#+     +#+             #
#                                                       +++##+++::::::::::::::       +#+    +:+     +#+     +#+             #
#                                                         ::::::::::::::::::::       +#+    +#+     +#+     +#+             #
#                                                         ::::::::::::::::::::       #+#    #+#     #+#     #+#    #+#      #
#      Update: 2022/04/23 17:05:11 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns
import re 

def get_stations_importances(feature_importance, stations):
    stations_importance = stations.copy()
    stations_importance['nb_important_sensors'] = 0
    stations_importance['max_importance_value'] = 0
    for index in feature_importance.index:
        x = re.search("station_([0-9]+)", index)
        if x:
            station_id = int(x.group(1))
            importance_value = feature_importance[index]
            stations_importance.loc[stations_importance['numero_station'] == station_id, 'nb_important_sensors'] += 1
            stations_importance.loc[(stations_importance['numero_station'] == station_id) & (stations_importance['max_importance_value'] < importance_value), 'max_importance_value'] = importance_value 

    return stations_importance

def display_feature_importance(feature_importance, target_name, stations, borough_file):
    borough = gpd.read_file(borough_file)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(30, 10), gridspec_kw={'width_ratios':[3,1], 'height_ratios':[1]})
    fig.suptitle(f"Feature importance visualization for the target {target_name}", fontsize=36)
    stations_importances = get_stations_importances(feature_importance[target_name], stations)
    gdf = gpd.GeoDataFrame(stations_importances, geometry=gpd.points_from_xy(stations_importances.longitude, stations_importances.latitude))
    borough.plot(ax=ax1, alpha=0.5, edgecolor='k', color='#CCC')
    gdf.plot(ax=ax1, column='max_importance_value', legend=True, markersize=(stations_importances['nb_important_sensors'] * 40 + 5), cmap=plt.cm.get_cmap('plasma_r'), vmin=0, vmax=1)
    ax1.set_xlabel('Longitude', fontsize=10)
    ax1.set_ylabel('Latitude', fontsize='medium')
    ax1.set_title(f"Stations")
    for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf.numero_station):
        ax1.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")
    
    sns.heatmap(feature_importance, ax=ax2, annot=True, linewidths=.5, cmap=plt.cm.get_cmap('plasma_r'), cbar=False, vmin=0, vmax=1)
