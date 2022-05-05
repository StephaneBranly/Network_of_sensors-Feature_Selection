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
#      Update: 2022/05/05 17:12:03 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

from src.FeatureSelectionMethods.TemplateMethod import TemplateMethod

class PearsonCorrelation(TemplateMethod):
    def __init__(self):
        TemplateMethod.__init__(self, 'PearsonCorrelation')

    def select(self, dataframe, target_columns):
        target_correlation = dataframe.corr()[target_columns]
        self._score = target_correlation
