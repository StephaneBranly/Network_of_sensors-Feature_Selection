# ************************************************************************************************************************* #
#   UTC Header                                                                                                              #
#                                                         ::::::::::::::::::::       :::    ::: :::::::::::  ::::::::       #
#      utils_spatial.py                                   ::::::::::::::::::::       :+:    :+:     :+:     :+:    :+:      #
#                                                         ::::::::::::::+++#####+++  +:+    +:+     +:+     +:+             #
#      By: branlyst and ismailkad < >                     ::+++##############+++     +:+    +:+     +:+     +:+             #
#                                                     +++##############+++::::       +#+    +:+     +#+     +#+             #
#                                                       +++##+++::::::::::::::       +#+    +:+     +#+     +#+             #
#                                                         ::::::::::::::::::::       +#+    +#+     +#+     +#+             #
#                                                         ::::::::::::::::::::       #+#    #+#     #+#     #+#    #+#      #
#      Update: 2022/05/14 17:48:56 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx

def visualise_stations(stations):
    """
        Generates a figure with geospatial data
        Shows the stations position with their ID
        Boroughs are used as a background layer
    """
    gdf = gpd.GeoDataFrame(stations, geometry=gpd.points_from_xy(stations.longitude, stations.latitude), crs='EPSG:4326').to_crs(epsg=3857)
    ax = gdf.plot(column='nom', markersize=20)
    ax.set_xlabel('Longitude', fontsize=10)
    ax.set_ylabel('Latitude', fontsize=10)
    ax.set_title(f"Visualisation of the stations")
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
    for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf.numero_station):
        ax.annotate(label, xy=(x, y), xytext=(1, 4), textcoords="offset points")
