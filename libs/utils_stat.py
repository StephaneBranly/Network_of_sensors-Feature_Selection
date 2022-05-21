from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import kpss
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.api import VAR

import pandas as pd
import numpy as np

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
    
def kpss_test(series, verbose=False, **kw):  
    """
    Pass in a time series, returns an KPSS report
    """  
    statistic, p_value, n_lags, critical_values = kpss(series, **kw)
    # Format Output
    if verbose == True:
        print(f'KPSS Statistic: {statistic}')
        print(f'p-value: {p_value}')
        print(f'num lags: {n_lags}')
        print('Critial Values:')
        for key, value in critical_values.items():
            print(f'   {key} : {value}')
        print(f'Result: The series is {"not " if p_value < 0.05 else ""}stationary')
    if p_value < 0.05:
        return False
    else:
        return True
    
def stationarity_check(series, verbose=False):
    """
    Pass in a time series, checks for stationarity with adf test and if not verified performs differentiation
    returns a serie verifying stationarity property
    """
    s = series
    n_diff = 0
    while not adf_test(s, verbose):
        s = s.diff().dropna()
        n_diff +=1
    if verbose:
        print(f"Number of differentiation operations performed: {n_diff}")
    return s
    
def grangers_causation_matrix(data, variables, test='ssr_ftest', maxlag=10, verbose=False):    
    """Check Granger Causality of all possible combinations of the Time series.
    The rows are the response variable, columns are predictors. The values in the table 
    are the P-Values. P-Values lesser than the significance level (0.05), implies 
    the Null Hypothesis that the coefficients of the corresponding past values is 
    zero, that is, the X does not cause Y can be rejected.

    data      : pandas dataframe containing the time series variables
    variables : list containing names of the time series variables.
    """
    df = pd.DataFrame(np.zeros((len(variables), len(variables))), columns=variables, index=variables)
    
    #maxlag = int((data.shape[0]  - 1)  / (2 * (data.shape[1] + 1)))
    
    for c in df.columns:
        for r in df.index:
            
            if (c != r):
                #Computing the lag order 
                #check for stationarity
                df_c_r = stationary_dataframe(data[[c,r]])
                lag = var_lag_order(df_c_r)
                test_result = grangercausalitytests(df_c_r, maxlag=lag, verbose=False)
                p_values = [round(test_result[i+1][0][test][1],4) for i in range(maxlag)]
                min_p_value = np.min(p_values)
                #p_value = round(test_result[lag][0][test][1])
                #print(p_value)
                if verbose: print(f'Y = {r}, X = {c}, P Values = {p_values}')
                df.loc[r, c] = min_p_value
                
            else:
                df.loc[r, c] = 1
                
    df.columns = [var + '_x' for var in variables]
    df.index = [var + '_y' for var in variables]
    
    return df

def symmetrize(df):
    A = df
    if not isinstance(df,np.ndarray):
        A = df.to_numpy()
    n_row, n_col = A.shape
    
    if n_row != n_col:
        print("Please use a square matrix")
        return 0
    
    for i in range(1,n_row):
        for j in range(i+1):
            A[i,j] = 1 - max(A[i,j],A[j,i])
            A[j,i] = A[i,j]
    
    return A

def is_stationary(ts):
    """
    Check for stationarity of time series composing a dataframe or a series
    returns a boolean
    """
    
    try:
        if isinstance(ts, pd.Series):
            return adf_test(ts)
        elif isinstance(ts, pd.DataFrame):
            for c in ts.columns:
                if not adf_test(ts[c]):
                    return False
            return True
    except:
        print('Wrong input type')
        
def stationary_series(series, verbose=False):
    """
    Pass in a time series, checks for stationarity with adf test and if not verified performs differentiation
    returns a serie verifying stationarity property
    """
    s = series
    n_diff = 0
    while adf_test(s, verbose) == False:
        s = s.diff().dropna()
        n_diff +=1
    if verbose:
        print(f"Number of differentiation operations performed: {n_diff}")
    return s

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

def var_lag_order(dataframe, criterion='aic'):
    """
    Pass in a dataframe
    Returns the optimal lag order given the criterion input for a VAR model
    """
    #TODO: assert n_columns = 2
    #TODO: assert dataframe stationary
    model = VAR(dataframe)
    select_order = model.select_order()
    if criterion == 'aic':
    #We select the order based on AIC criterion
        optimal_lag = select_order.aic
    else:
        #TODO: having other criterions handled
        optimal_lag = select_order.aic
    return optimal_lag

def model_VAR(dataframe, lag=None, criterion='aic', verbose=False):
    """
    Pass in a dataframe, checks for stationarity and differ is necessary, then fit a VAR model with 
    the optimal lag order given the criterion input or the lag input
    Returns a model fitted to the data
    """
    df, n_diff = stationary_dataframe(dataframe, verbose=verbose)
    if lag is None:
        lag_order = var_lag_order(df, criterion=criterion)
    else:
        lag_order = lag
    model = VAR(df)
    model_fitted = model.fit(lag_order)
    return model_fitted
