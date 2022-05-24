# ************************************************************************************************************************* #
#   UTC Header                                                                                                              #
#                                                         ::::::::::::::::::::       :::    ::: :::::::::::  ::::::::       #
#      TemplateMethod.py                                  ::::::::::::::::::::       :+:    :+:     :+:     :+:    :+:      #
#                                                         ::::::::::::::+++#####+++  +:+    +:+     +:+     +:+             #
#      By: branlyst and ismailkad < >                     ::+++##############+++     +:+    +:+     +:+     +:+             #
#                                                     +++##############+++::::       +#+    +:+     +#+     +#+             #
#                                                       +++##+++::::::::::::::       +#+    +:+     +#+     +#+             #
#                                                         ::::::::::::::::::::       +#+    +#+     +#+     +#+             #
#                                                         ::::::::::::::::::::       #+#    #+#     #+#     #+#    #+#      #
#      Update: 2022/05/24 15:29:28 by branlyst and ismai  ::::::::::::::::::::        ########      ###      ######## .fr   #
#                                                                                                                           #
# ************************************************************************************************************************* #

class TemplateMethod:
    """
        The class TemplateMethod provide a Template which can be implemented or extended to implement methods for Feature Selection.

        Args:
            method_name (str) : the name of the implemented method, name used to find the right instance

        Attributes:
            _score (DataFrame) : Dataframe which contains len(target_columns) columns and len(features) lines representing the score result of the feature selection
            _method_name (str) : variable which stores the method name
    """
    _score = None
    _method_name = None

    def __init__(self, method_name):
        self._method_name = method_name

    def select(self, dataframe, target_columns):
        """
            Select abstract method. Must be implemented. 

            Args:
                dataframe (DataFrame) : dataframe which contains the data used to apply the feature selection. 1 column by feature and 1 line by entry
                target_columns (str[]) : array of the target column names used to apply the feature selection
        """
        raise NotImplementedError

    def get_features_importance(self):
        """
            Accessor to the _score variable
        """
        return self._score

    def get_method_name(self):
        """
            Accessor to the _method_name variable
        """
        return self._method_name