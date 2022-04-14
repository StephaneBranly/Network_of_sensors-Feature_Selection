import pandas as pd
import numpy as np


def concatenate_new_station(data, station_data, station_id):
  station_data = station_data.drop(columns=['numero_station'])
  station_data[['date','heure']] = station_data['date_heure'].str.split(expand=True)
  station_data['date_heure'] = (pd.to_datetime(station_data.pop('date'), format='%d-%m-%Y') + pd.to_timedelta(station_data.pop('heure') + ':00'))
  station_data = station_data.set_index('date_heure')

  # add station_id to pollutant column name
  station_data.columns = [feature + "_station_" + str(station_id) for feature in station_data.columns]
  data = pd.concat([data, station_data], axis=1, join='outer')
  return data

def transform_all_pollutants_data(data):
  fr = pd.DataFrame()
  for station_id in data['numero_station'].unique():
    fr = concatenate_new_station(fr, data[data['numero_station'] == station_id], station_id)
  return fr

def convert_unknown_values_to_na(data):
  considered_as_unknown = ['<Samp', 'InVld', 'NoData', 'Down', 'Calib', 'Zero', 'Span', 'Purge', 'Alarm', 'FailPwr', 'N/M']
  for column in data.columns:
    for to_replace in considered_as_unknown:
      data[column] = np.where((data[column] == to_replace), np.nan ,data[column])
    data[column] = data[column].astype(float)

  return data
