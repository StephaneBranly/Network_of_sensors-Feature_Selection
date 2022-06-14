from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import kpss
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.api import VAR
from sklearn_extra.cluster import KMedoids

import plotly.express as px
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
    
    #TODO: assert dataframe is stationary
    df = pd.DataFrame(np.zeros((len(variables), len(variables))), columns=variables, index=variables)
    
    #maxlag = int((data.shape[0]  - 1)  / (2 * (data.shape[1] + 1)))
    
    for c in df.columns:
        for r in df.index:
            
            if (c != r):
                #Computing the lag order 
                #check for stationarity
                df_c_r, _ = stationary_dataframe(data[[r,c]])
                lag = var_lag_order(df_c_r)
                test_result = grangercausalitytests(df_c_r, maxlag=lag, verbose=False)
                p_values = [round(test_result[i+1][0][test][1],4) for i in range(lag)]
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
    
    for i in range(0,n_row):
        for j in range(i+1):
            if i == j:
                A[i,j] = 0
            A[i,j] = 1 - max(A[i,j],A[j,i])
            A[j,i] = A[i,j]
    
    return A

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
    df, _ = stationary_dataframe(dataframe, verbose=verbose)
    if lag is None:
        lag_order = var_lag_order(df, criterion=criterion)
    else:
        lag_order = lag
    model = VAR(df)
    model_fitted = model.fit(lag_order)
    return model_fitted

def k_medoids(matrix, n_clusters=[]):
    
    """
    Performs multiple clustering with different n_cluster and keep track of inertia
    Returns an pandas array
    """
    
    results = []
    
    for n_cluster in n_clusters:
        
        for method in ["alternate", "pam"]:
            
            KMobj = KMedoids(n_clusters=n_cluster, method=method, metric="precomputed").fit(matrix)
        
            results.append([n_cluster, method, KMobj.inertia_])
            
    return pd.DataFrame(results, columns=["n_clusters", "method", "inertia"])

def clustering_features(matrix, labels, target):
    """
    Returns the features in matrix having the max causality with the target for each cluster
    """
    features = []
    for label in set(labels):
        ind = np.where(labels == label)
        max_feature = matrix[target].iloc[ind].idxmax()
        features.append(max_feature)
    return features

def model_forecast(dataframe, features, nobs, target):
    
    """
    Takes as input a dataframe, a value nobs (the number of forecasts) and a target on which the RMSE will be calculated
    Returns a dataframe for forecasted values and RMSE (root mean square error)
    """
    
    df = dataframe[features]
    
    #Make sure target is integrated in df
    if target not in df.columns:
        df = df.join(df[target])
        
    #Split dataset to train/test sets
    df_train, df_test = df[0:-nobs], df[-nobs:]
        
    #Checks for stationarity and train models with optimal lag order 
    model = model_VAR(df_train)
    
    #Get the lag order
    model_lag_order = model.k_ar 

    #Input data for forecasting
    forecast_input = df.values[-model_lag_order:]
    
    #Forecasting
    forecast = model.forecast(y=forecast_input, steps=nobs)
    df_forecast = pd.DataFrame(forecast, index=df.index[-nobs:], columns=df.columns + '_fc')
    
    rmse = np.mean((df_forecast[target + "_fc"] - df_test[target])**2)**.5   
    
    return df_forecast, rmse

def plot_forecast_vs_actual(df, forecast, nobs, target):
    """
    Input: initial dataframe, forecast dataframe, nobs, target
    Return: plot of forecast vers actual values of target 
    """
    merged_df = df[-nobs:].join(forecast)
    plot_df = merged_df[[target, target + '_fc']]
    fig = px.line(plot_df, x=plot_df.index, y=plot_df.columns)
    fig.update_layout(title='Forecast versus actual values',
                   xaxis_title='Time',
                   yaxis_title='Value')
    fig.show()
    
def pca_features(df, pca):
    """
    Input: a dataframe and a fitted PCA model
    Returns PCA most relevant features
    """
    
    pd.DataFrame(pca.components_, columns = df.columns)

    n_pcs= pca.n_components_ # get number of component
    
    # get the index of the most important feature on EACH component
    most_important = [np.abs(pca.components_[i]).argmax() for i in range(n_pcs)]
    initial_feature_names = df.columns
    # get the most important feature names
    most_important_names = list(set([initial_feature_names[most_important[i]] for i in range(n_pcs)]))
    
    return most_important_names