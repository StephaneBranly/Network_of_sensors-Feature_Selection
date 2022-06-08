# ************************************************************************************************************************* #
#   UTC Header                                                                                                              #
#                                                         ::::::::::::::::::::       :::    ::: :::::::::::  ::::::::       #
#      utils.py                                           ::::::::::::::::::::       :+:    :+:     :+:     :+:    :+:      #
#                                                         ::::::::::::::+++#####+++  +:+    +:+     +:+     +:+             #
#      By: branlyst and ismailkad < >                     ::+++##############+++     +:+    +:+     +:+     +:+             #
#                                                     +++##############+++::::       +#+    +:+     +#+     +#+             #
#                                                       +++##+++::::::::::::::       +#+    +:+     +#+     +#+             #
#                                                         ::::::::::::::::::::       +#+    +#+     +#+     +#+             #
#                                                         ::::::::::::::::::::       #+#    #+#     #+#     #+#    #+#      #
#      Update: 2022/06/08 15:23:32 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller


def adf_test(series, title="", verbose=False):
    """
    Pass in a time series and an optional title, returns an ADF report
    """
    result = adfuller(
        series.dropna(), autolag="AIC"
    )  # .dropna() handles differenced data
    labels = ["ADF test statistic", "p-value", "# lags used", "# observations"]
    out = pd.Series(result[0:4], index=labels)
    for key, val in result[4].items():
        out[f"critical value ({key})"] = val
    if verbose == True:
        print(f"Augmented Dickey-Fuller Test: {title}")
        print(out.to_string())  # .to_string() removes the line "dtype: float64"
    if result[1] <= 0.05:
        if verbose == True:
            print(f"Strong evidence against the null hypothesis for {series.name}")
            print("Reject the null hypothesis")
            print("Data has no unit root and is stationary")
        return True
    else:
        if verbose == True:
            print(f"Weak evidence against the null hypothesis for {series.name}")
            print("Fail to reject the null hypothesis")
            print("Data has a unit root and is non-stationary")
        return False


def is_stationary(ts):
    """
    Check for stationarity of time series composing a dataframe or a series
    returns a boolean
    """

    if isinstance(ts, pd.Series):
        return adf_test(ts)
    elif isinstance(ts, pd.DataFrame):
        for c in ts.columns:
            if not adf_test(ts[c]):
                return False
        return True
    else:
        print("Wrong input")
        return False


def stationary_dataframe(dataframe, verbose=False):
    """
    Pass in a dataframe, checks for stationarity for each series with adf test and if not verified performs differentiation
    returns a dataframe with each series verifying stationarity property
    """
    df = dataframe
    diff = 0
    while not is_stationary(df):
        df = df.diff().dropna()
        diff += 1
    if verbose:
        print("Number of times dataframe got differed: ", diff)
    return df, diff


def symmetrize(df):
    A = df
    if not isinstance(df, np.ndarray):
        A = df.to_numpy()
    n_row, n_col = A.shape

    if n_row != n_col:
        print("Please use a square matrix")
        return 0

    for i in range(0, n_row):
        for j in range(i + 1):
            if i == j:
                A[i, j] = 0
            A[i, j] = 1 - max(A[i, j], A[j, i])
            A[j, i] = A[i, j]

    return A
