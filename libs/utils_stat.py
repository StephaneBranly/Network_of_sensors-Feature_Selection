from statsmodels.tsa.stattools import adfuller
import pandas as pd

def adf_test(series,title='', verbose=False):
    """
    Pass in a time series and an optional title, returns an ADF report
    """
    result = adfuller(series.dropna(),autolag='AIC') # .dropna() handles differenced data
    labels = ['ADF test statistic','p-value','# lags used','# observations']
    out = pd.Series(result[0:4],index=labels)
    for key,val in result[4].items():
        out[f'critical value ({key})']=val
    if verbose == True:
        print(f'Augmented Dickey-Fuller Test: {title}')
        print(out.to_string())          # .to_string() removes the line "dtype: float64"
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