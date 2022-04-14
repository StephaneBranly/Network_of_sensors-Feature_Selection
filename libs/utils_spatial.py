import matplotlib.pyplot as plt
import geopandas as gpd

def visualise_stations(stations, borough_file):
    borough = gpd.read_file(borough_file)
    fig = plt.figure(figsize=(20,20))
    gdf = gpd.GeoDataFrame(stations, geometry=gpd.points_from_xy(stations.longitude, stations.latitude))
    ax = borough.plot(alpha=0.5, edgecolor='k', color='#DDD')
    gdf.plot(ax=ax, column='nom', markersize=20)
    ax.set_xlabel('Longitude', fontsize=10)
    ax.set_ylabel('Latitude', fontsize='medium')
    ax.set_title(f"Stations")
    for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf.numero_station):
        ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")
