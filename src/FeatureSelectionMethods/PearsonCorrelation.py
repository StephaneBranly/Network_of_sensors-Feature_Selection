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
#      Update: 2022/05/01 22:38:23 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

from src.FeatureSelectionMethods.TemplateMethod import TemplateMethod

class PearsonCorrelation(TemplateMethod):
    def __init__(self):
        TemplateMethod.__init__(self, 'PearsonCorrelation')

    def select(self, dataframe, target_column):
        target_correlation = dataframe.corr()[[target_column]]
        self._score = list(abs(target_correlation).sort_values(by=target_column, ascending=False)[:15].index)
