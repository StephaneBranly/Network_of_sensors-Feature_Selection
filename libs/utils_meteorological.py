import pandas as pd
import numpy as np

def replace_from_dic(string, dic):
  for key in dic.keys():
    string = string.replace(key, str(dic[key]))
  return string

def index_to_reference(dt):
  return {
      '{DAY}': dt.day,
      '{MONTH}': dt.month,
      '{YEAR}': dt.year,
  }

def reference_to_string(reference):
  return f"{reference['{DAY}']}-{reference['{MONTH}']}-{reference['{YEAR}']}"

def load_day_meteorological_data(meteorological_data, day_url):
  data = pd.read_csv(day_url)
  data['Date/Heure (UTC)'] = pd.to_datetime(data['Date/Heure (UTC)'], format='%Y-%m-%d %H:%M')
  data = data.set_index('Date/Heure (UTC)')
  meteorological_data = pd.concat([meteorological_data, data], axis=0)
  return meteorological_data

def load_meteorological_data(indexes, csv_meteo_for_one_day, stations_id):
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
  unused_columns = ['Temps', 'Année', 'Mois', 'Jour', 'Heure (UTC)', 'ID climatologique', 'Nom de la Station', 'Longitude (x)', 'Latitude (y)']
  for unused_column in unused_columns:
    data.drop(unused_column, axis=1, inplace=True)
    
  return data

def convert_columns_to_float_type(data):
  # change , to . in order to change the data type and have columns as float
  float_columns = ['Temp (°C)', 'Point de rosée (°C)', 'Pression à la station (kPa)', 'Visibilité (km)']
  for float_column in float_columns:
    data[float_column] = data[float_column].str.replace(",", ".")
    data[float_column] = data[float_column].astype(float)
 
  return data