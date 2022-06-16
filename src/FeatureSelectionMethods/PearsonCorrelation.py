# ************************************************************************************************************************* #
#   UTC Header                                                                                                              #
#                                                         ::::::::::::::::::::       :::    ::: :::::::::::  ::::::::       #
#      PearsonCorrelation.py                              ::::::::::::::::::::       :+:    :+:     :+:     :+:    :+:      #
#                                                         ::::::::::::::+++#####+++  +:+    +:+     +:+     +:+             #
#      By: branlyst and ismailkad < >                     ::+++##############+++     +:+    +:+     +:+     +:+             #
#                                                     +++##############+++::::       +#+    +:+     +#+     +#+             #
#                                                       +++##+++::::::::::::::       +#+    +:+     +#+     +#+             #
#                                                         ::::::::::::::::::::       +#+    +#+     +#+     +#+             #
#                                                         ::::::::::::::::::::       #+#    #+#     #+#     #+#    #+#      #
#      Update: 2022/06/16 17:42:24 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

from src.FeatureSelectionMethods.TemplateMethod import TemplateMethod


class PearsonCorrelation(TemplateMethod):
    """
    PearsonCorrelation is a class which implements the TemplateMethods in order to implement the Pearson Correlation feature selection
    """

    def __init__(self):
        TemplateMethod.__init__(self, "PearsonCorrelation")

    def select(self, dataframe, target_columns, number_of_target_to_keep=1):
        target_correlation = dataframe.corr()[target_columns]
        self._score = abs(target_correlation)

        self._selected_features = dict()
        for target_column in target_columns:
            self._selected_features[target_column] = list(
                self._score.sort_values(by=target_column, ascending=False)[
                    :number_of_target_to_keep
                ].index
            )
