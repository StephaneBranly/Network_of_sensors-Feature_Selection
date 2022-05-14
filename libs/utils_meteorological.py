# ************************************************************************************************************************* #
#   UTC Header                                                                                                              #
#                                                         ::::::::::::::::::::       :::    ::: :::::::::::  ::::::::       #
#      utils_meteorological.py                            ::::::::::::::::::::       :+:    :+:     :+:     :+:    :+:      #
#                                                         ::::::::::::::+++#####+++  +:+    +:+     +:+     +:+             #
#      By: branlyst and ismailkad < >                     ::+++##############+++     +:+    +:+     +:+     +:+             #
#                                                     +++##############+++::::       +#+    +:+     +#+     +#+             #
#                                                       +++##+++::::::::::::::       +#+    +:+     +#+     +#+             #
#                                                         ::::::::::::::::::::       +#+    +#+     +#+     +#+             #
#                                                         ::::::::::::::::::::       #+#    #+#     #+#     #+#    #+#      #
#      Update: 2022/05/14 19:50:26 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

import pandas as pd
import re
import seaborn as sns
import matplotlib.pyplot as plt

def replace_from_dic(string, dic):
  """
    Replaces in a string the keys of a dictionnary by their value
  """
  for key in dic.keys():
    string = string.replace(key, str(dic[key]))
  return string

def index_to_reference(dt):
  """
    Generates a dictionnay with {DAY}, {MONTH} and {YEAR} as keys from a datetime variable
  """
  return {
      '{DAY}': dt.day,
      '{MONTH}': dt.month,
      '{YEAR}': dt.year,
  }

def reference_to_string(reference):
  """
    Generates an unique string index from a dictionnary reference (with {DAY}, {MONTH} and {YEAR} as keys)
  """
  return f"{reference['{DAY}']}-{reference['{MONTH}']}-{reference['{YEAR}']}"

def load_day_meteorological_data(meteorological_data, day_url):
  """
    Loads meteorological data for one day and add it to the meteorological_data dataframe given. Sets datetime as index. 
  """
  data = pd.read_csv(day_url)
  data['Date/Heure (UTC)'] = pd.to_datetime(data['Date/Heure (UTC)'], format='%Y-%m-%d %H:%M')
  data = data.set_index('Date/Heure (UTC)')
  meteorological_data = pd.concat([meteorological_data, data], axis=0)
  return meteorological_data

def load_meteorological_data(indexes, csv_meteo_for_one_day, stations_id):
  """
     Loads meteorological data for all indexes. Creates an unique dateframe containing meteorological data for all days (indexes). 
  """
  meteorological_data = pd.DataFrame()
  already_loaded = []

  for index in pd.DatetimeIndex(indexes):
    reference = index_to_reference(index)
    if reference_to_string(reference) not in already_loaded:
      print('adding new day : ' + reference_to_string(reference))
      already_loaded.append(reference_to_string(reference))
      reference['{STATIONID}'] = stations_id[0]
      meteorological_data = load_day_meteorological_data(meteorological_data, replace_from_dic(csv_meteo_for_one_day, reference))
  meteorological_data = meteorological_data.loc[~meteorological_data.index.duplicated(keep='first')]
  return meteorological_data

def remove_unused_columns(data):
  """
    Removes unused columns from meteorological data.
  """
  unused_columns = ['Temps', 'Année', 'Mois', 'Jour', 'Heure (UTC)', 'ID climatologique', 'Nom de la Station', 'Longitude (x)', 'Latitude (y)']
  for unused_column in unused_columns:
    data.drop(unused_column, axis=1, inplace=True)
    
  return data

def convert_columns_to_float_type(data):
  """
    Changes , to . in order to change the data type and have columns as float
  """
  float_columns = ['Temp (°C)', 'Point de rosée (°C)', 'Pression à la station (kPa)', 'Visibilité (km)']
  for float_column in float_columns:
    data[float_column] = data[float_column].str.replace(",", ".")
    data[float_column] = data[float_column].astype(float)
 
  return data



def plot_meteorological_data(dataframe):
  """
    Plots the meteorological data
  """
  
  columns = ['Temp (°C)', 'Point de rosée (°C)', 'Hum. rel (%)',
        'Dir. du vent (10s deg)', 'Vit. du vent (km/h)', 'Visibilité (km)',
        'Pression à la station (kPa)', 'Refroid. éolien']
  fig, axs = plt.subplots(3, 3, figsize=(30, 15))
  fig.tight_layout()
  for i, column in enumerate(columns):
    ax = axs[i // 3][i % 3]
    ax.title.set_text(column)
    pal = ['#20F']*sum(dataframe[column].isna())
    if len(pal) == 0:
        pal=['#20F']
    g = sns.lineplot(ax=ax, 
                  data=dataframe, 
                  x=dataframe.index, 
                  y=column,
                  hue=dataframe[column].isna().cumsum(),
                  palette=pal,
                  legend=False,
                  markers=True,
                  alpha=.9
              )

    ax.set(ylabel=None)
