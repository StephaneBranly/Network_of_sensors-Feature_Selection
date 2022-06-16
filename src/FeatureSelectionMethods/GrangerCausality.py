# ************************************************************************************************************************* #
#   UTC Header                                                                                                              #
#                                                         ::::::::::::::::::::       :::    ::: :::::::::::  ::::::::       #
#      GrangerCausality.py                                ::::::::::::::::::::       :+:    :+:     :+:     :+:    :+:      #
#                                                         ::::::::::::::+++#####+++  +:+    +:+     +:+     +:+             #
#      By: branlyst and ismailkad < >                     ::+++##############+++     +:+    +:+     +:+     +:+             #
#                                                     +++##############+++::::       +#+    +:+     +#+     +#+             #
#                                                       +++##+++::::::::::::::       +#+    +:+     +#+     +#+             #
#                                                         ::::::::::::::::::::       +#+    +#+     +#+     +#+             #
#                                                         ::::::::::::::::::::       #+#    #+#     #+#     #+#    #+#      #
#      Update: 2022/06/16 17:51:15 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

from src.FeatureSelectionMethods.TemplateMethod import TemplateMethod
from src.scripts.utils import stationary_dataframe, symmetrize

from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.api import VAR

from sklearn_extra.cluster import KMedoids

import numpy as np
import pandas as pd


class GrangerCausality(TemplateMethod):
    """
    GrangerCausality is a class which implements the TemplateMethods in order to implement the Granger Causality feature selection
    Explaned in the paper [GFSM: a Feature Selection Method for Improving Time Series Forecasting](https://hal.archives-ouvertes.fr/hal-02448277/document)
    """

    def __init__(self):
        TemplateMethod.__init__(self, "GrangerCausality")

    def select(self, dataframe, target_columns, number_of_target_to_keep=1):

        # make dataframe stationary
        df, _ = stationary_dataframe(dataframe)

        # compute granger causality matrix
        lagrange_matrix = self.grangers_causation_matrix(
            df, df.columns, test="ssr_ftest"
        )

        # make the matrix symmetric using the max function agg
        lgm = symmetrize(lagrange_matrix)
        lgm_df = pd.DataFrame(lgm, columns=df.columns, index=df.columns)

        # clustering using KMedoid
        KMobj = KMedoids(
            n_clusters=number_of_target_to_keep,
            metric="precomputed",
            init="k-medoids++",
        ).fit(lgm)
        clusters = KMobj.labels_

        self._selected_features = dict()
        for target_column in target_columns:
            self._selected_features[target_column] = self.gfsm_features(
                lgm_df, clusters, target_column
            )
        self._score = lgm_df[target_columns]

    def grangers_causation_matrix(
        self, data, variables, test="ssr_ftest", maxlag=10, verbose=False
    ):
        """Check Granger Causality of all possible combinations of the Time series.
        The rows are the response variable, columns are predictors. The values in the table
        are the P-Values. P-Values lesser than the significance level (0.05), implies
        the Null Hypothesis that the coefficients of the corresponding past values is
        zero, that is, the X does not cause Y can be rejected.

        Args:
            data (DataFrame)     : pandas dataframe containing the time series variables
            variables : list containing names of the time series variables.
        """

        # TODO: assert dataframe is stationary
        df = pd.DataFrame(
            np.zeros((len(variables), len(variables))),
            columns=variables,
            index=variables,
        )

        # maxlag = int((data.shape[0]  - 1)  / (2 * (data.shape[1] + 1)))

        for c in df.columns:
            for r in df.index:

                if c != r:
                    # Computing the lag order
                    # check for stationarity
                    df_c_r, _ = stationary_dataframe(data[[r, c]])
                    lag = self.var_lag_order(df_c_r)
                    test_result = grangercausalitytests(
                        df_c_r, maxlag=lag, verbose=False
                    )
                    p_values = [
                        round(test_result[i + 1][0][test][1], 4) for i in range(lag)
                    ]
                    min_p_value = np.min(p_values)
                    if verbose:
                        print(f"Y = {r}, X = {c}, P Values = {p_values}")
                    df.loc[r, c] = min_p_value

                else:
                    df.loc[r, c] = 1

        df.columns = [var + "_x" for var in variables]
        df.index = [var + "_y" for var in variables]

        return df

    def var_lag_order(self, dataframe, criterion="aic"):
        """
        Pass in a dataframe
        Returns the optimal lag order given the criterion input for a VAR model

        Args:
            dataframe (DataFrame) : pandas dataframe
            criterion (str) : criterion, `aic` by default
        """
        # TODO: assert n_columns = 2
        # TODO: assert dataframe stationary
        model = VAR(dataframe)
        select_order = model.select_order()
        if criterion == "aic":
            # We select the order based on AIC criterion
            optimal_lag = select_order.aic
        else:
            # TODO: having other criterions handled
            optimal_lag = select_order.aic
        return optimal_lag

    def gfsm_features(self, matrix, labels, target):
        """
        Returns the features in matrix having the max causality with the target for each cluster

        Args:
            matrix (DataFrame) : the granger Matrix
            labels
            target (str) : target name
        """
        features = []
        for label in set(labels):
            ind = np.where(labels == label)
            max_feature = matrix[target].iloc[ind].idxmax()
            features.append(max_feature)
        return features
