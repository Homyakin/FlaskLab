import numpy as np
import pandas as pd
import rpy2
import rpy2.robjects.numpy2ri as numpy2ri
from rpy2.robjects.packages import importr
from scipy.stats import chi2_contingency


def get_contingency_table(data, field1: str, field2: str):
    """
    :param data: pandas dataframe
    :param field1:
    :param field2:
    :return: таблица сопряженности
    """
    data = pd.DataFrame(data, columns=[field1, field2])
    cross_table = pd.crosstab(data[field1], data[field2])
    return cross_table


def pearsons_chi2(crosstab, correction=False):
    """
    :param crosstab: numpy.ndarray -- table of actual frequencies
    :param correction: bool -- use Yates correction
    :return: tuple -- (chi2 statistic, p-value, table of expected values)
    """
    chi2_stat, pval, df, expected = chi2_contingency(crosstab,
                                                     correction=correction)

    result = f'''
    Used method: Pearson's chi2;\n
    Yates correction: {'Yes' if correction else 'No'};\n
    Chi2 statistic = {chi2_stat:.4f};\n
    P-value = {pval:.4f}
    '''
    return result, expected


def exact_fisher(crosstab, correction=False):
    """
    :param crosstab: numpy.ndarray -- table of actual frequencies
    :param correction: bool -- use Yates correction
    :return: tuple -- (chi2 statistic, None)
    """
    numpy2ri.activate()
    stats = importr('stats')

    try:
        result = str(stats.fisher_test(crosstab,
                                       simulate_p_value=correction, B=5000))
    except rpy2.rinterface.RRuntimeError:
        result = str(stats.fisher_test(crosstab, simulate_p_value=True, B=5000))

    return str(result), None


def get_statistic_and_expected_table(crosstab):
    """
        super duper AI function for choosing tests

        :param crosstab: pd.crosstab() for field1 and field2:
        :return: tuple (function result, table of expected values or None)
    """

    crosstab = crosstab.values
    if np.sum(crosstab) > 10000:
        return exact_fisher(crosstab, True)
    else:
        if np.all(crosstab >= 10):
            return pearsons_chi2(crosstab, False)
        elif np.any((crosstab > 5) & (crosstab <= 9)):
            return pearsons_chi2(crosstab, True)
        else:
            return exact_fisher(crosstab, False)
