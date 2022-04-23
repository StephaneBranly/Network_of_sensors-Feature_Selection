# ************************************************************************************************************************* #
#   UTC Header                                                                                                              #
#                                                         ::::::::::::::::::::       :::    ::: :::::::::::  ::::::::       #
#      utils_data.py                                      ::::::::::::::::::::       :+:    :+:     :+:     :+:    :+:      #
#                                                         ::::::::::::::+++#####+++  +:+    +:+     +:+     +:+             #
#      By: branlyst and ismailkad < >                     ::+++##############+++     +:+    +:+     +:+     +:+             #
#                                                     +++##############+++::::       +#+    +:+     +#+     +#+             #
#                                                       +++##+++::::::::::::::       +#+    +:+     +#+     +#+             #
#                                                         ::::::::::::::::::::       +#+    +#+     +#+     +#+             #
#                                                         ::::::::::::::::::::       #+#    #+#     #+#     #+#    #+#      #
#      Update: 2022/04/23 17:09:45 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

import missingno as msno
import matplotlib.pyplot as plt
import pandas as pd

def inspect_data(df=None, display_form='matrix', freq=None, figsize=(6,4)):
  """
    Generates a figure to inspect missing values
  """

  print(">>> Missing value visualization:")
  if display_form == 'matrix':
    if freq is not None:
      msno.matrix(df, freq=freq, figsize=figsize)
    else:
      msno.matrix(df, figsize=figsize)
  if display_form == 'bar':
    msno.bar(df, figsize=figsize)
  if display_form == 'heatmap':
    msno.heatmap(df, figsize=figsize)
  plt.show()
  return
  
def remove_empty_columns(data):
  """
    Removes columns of the dataframe which countains only unknown values
  """
  for column in data.columns:
    if all(data[column].isna()):
      data.drop(column, axis=1, inplace=True)
  return data

def shift_data(data, nb_shifts=1):
  """
    Duplicates columns of the dataframe with a shift.
    Possibility to apply multiple shifts.
    ie: if nb_shifts = 2; columns will be duplicated with a shift of 1 and a shift of 2
  """
  data_to_shift = data.copy()
  for i in range(nb_shifts):
    data_shifted = data_to_shift.copy()
    data_shifted = data_shifted.shift(periods=i+1)
    data_shifted = data_shifted.add_suffix(f"_h-{i+1}")
    data = pd.concat([data, data_shifted], axis=1)
  return data
  