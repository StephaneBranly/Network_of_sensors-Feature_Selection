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
#      Update: 2022/04/14 15:42:24 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

import missingno as msno
import matplotlib.pyplot as plt

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
