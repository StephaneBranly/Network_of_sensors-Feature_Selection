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
#      Update: 2022/05/14 15:14:34 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns
import re 
import contextily as ctx

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

def display_feature_importance(features_importance, target_name, stations):
    stations_importance = get_stations_importances(features_importance[target_name], stations)
    stations_importance = stations_importance.to_crs(epsg=3857) # change to Spherical Mercator to add ctx base map properly
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(30, 10), gridspec_kw={'width_ratios':[3,1], 'height_ratios':[1]})
    fig.suptitle(f"Feature importance visualization for the target {target_name}", fontsize=36)
    stations_importance.plot(ax=ax1, column='max_importance_value', legend=True, markersize=(stations_importance['nb_important_sensors'] * 40 + 5), cmap=plt.cm.get_cmap('plasma'), vmin=0, vmax=1)
    ax1.set_xlabel('Longitude', fontsize=10)
    ax1.set_ylabel('Latitude', fontsize='medium')
    ax1.set_title(f"Stations")
    ctx.add_basemap(ax1, source=ctx.providers.CartoDB.Positron)
    for x, y, label, offsetY in zip(stations_importance.geometry.x, stations_importance.geometry.y, stations_importance.numero_station, stations_importance['nb_important_sensors'] + 5):
        ax1.annotate(label, xy=(x, y), xytext=(0, offsetY), textcoords="offset points")

    features_importance = features_importance.dropna().sort_values(by=[target_name], ascending=False)
    sns.heatmap(features_importance, ax=ax2, annot=True, linewidths=.5, cmap=plt.cm.get_cmap('plasma'), cbar=False, vmin=0, vmax=1)