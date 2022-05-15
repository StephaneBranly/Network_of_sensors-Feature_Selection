# ************************************************************************************************************************* #
#   UTC Header                                                                                                              #
#                                                         ::::::::::::::::::::       :::    ::: :::::::::::  ::::::::       #
#      utils_pollution.py                                 ::::::::::::::::::::       :+:    :+:     :+:     :+:    :+:      #
#                                                         ::::::::::::::+++#####+++  +:+    +:+     +:+     +:+             #
#      By: branlyst and ismailkad < >                     ::+++##############+++     +:+    +:+     +:+     +:+             #
#                                                     +++##############+++::::       +#+    +:+     +#+     +#+             #
#                                                       +++##+++::::::::::::::       +#+    +:+     +#+     +#+             #
#                                                         ::::::::::::::::::::       +#+    +#+     +#+     +#+             #
#                                                         ::::::::::::::::::::       #+#    #+#     #+#     #+#    #+#      #
#      Update: 2022/05/14 19:50:11 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

import pandas as pd
import numpy as np
import re
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

def concatenate_new_station(data, station_data, station_id):
  """
    Concatenates a new station data to the current data
    Sets date_heure as index and rename columns by adding the station id into it
  """
  station_data = station_data.drop(columns=['numero_station'])
  station_data[['date','heure']] = station_data['date_heure'].str.split(expand=True)
  station_data['date_heure'] = (pd.to_datetime(station_data.pop('date'), format='%d-%m-%Y') + pd.to_timedelta(station_data.pop('heure') + ':00'))
  station_data = station_data.set_index('date_heure')

  # add station_id to pollutant column name
  station_data.columns = [feature + "_station_" + str(station_id) for feature in station_data.columns]
  data = pd.concat([data, station_data], axis=1, join='outer')
  return data

def transform_all_pollutants_data(data):
  """
    Transforms the pollutant data to have one column for each sensor of each station
  """
  fr = pd.DataFrame()
  for station_id in data['numero_station'].unique():
    fr = concatenate_new_station(fr, data[data['numero_station'] == station_id], station_id)
  return fr

def convert_unknown_values_to_na(data):
  """
    Converts string values as np.nan to considere them as unknown
    Sets columns as float type
  """
  considered_as_unknown = ['<Samp', 'InVld', 'NoData', 'Down', 'Calib', 'Zero', 'Span', 'Purge', 'Alarm', 'FailPwr', 'N/M']
  for column in data.columns:
    for to_replace in considered_as_unknown:
      data[column] = np.where((data[column] == to_replace), np.nan ,data[column])
    data[column] = data[column].astype(float)

  return data


def plot_pollution_data(dataframe):
  """
    Plots the pollution data
  """
  stations_color = {
      3: '#FF4949',
      6: '#764AF1',
      17: '#F66B0E',
      28: '#001D6E',
      31: '#614124',
      50: '#00FFC6',
      55: '#2F296D',
      66: '#4D96FF',
      80: '#019267',
      99: '#524A4E',
      103: '#06FF00'
  }
  
  pollutants = ['co','no','no2','pm2_5','pst','pm10','o3','so2','bc1_370nm','bc6_880nm','Benzene','Toluene','Ethylbenzene','M P-Xylene','O-Xylene']
  fig, axs = plt.subplots(3, 5, figsize=(30, 15))
  fig.tight_layout()
  for i, pollutant in enumerate(pollutants):
      ax = axs[i // 5][i % 5]
      ax.title.set_text(pollutant)
      y_columns = [c for c in dataframe.columns if f"{pollutant}_" in c]
      for y_column in y_columns:
          x = re.search('station_([0-9]+)', y_column)
          station = x.group(1)
          pal = [stations_color[int(station)]]*sum(dataframe[y_column].isna())
          if (len(pal) == 0):
            pal = [stations_color[int(station)]]
          g = sns.lineplot(ax=ax, 
                  data=dataframe, 
                  x=dataframe.index, 
                  y=y_column,
                  hue=dataframe[y_column].isna().cumsum(),
                  palette=pal,
                  legend=False,
                  markers=True,
                  alpha=.9
              )

      plt.legend(handles=[mlines.Line2D([], [], color=f"{stations_color[id]}", label=f"Station {id}") for id in stations_color])
      ax.set(ylabel=None)
