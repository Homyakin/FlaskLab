import numpy as np
import pandas as pd
import rpy2
import rpy2.robjects.numpy2ri as numpy2ri
from rpy2.robjects.packages import importr
from app import data
from scipy.stats import chi2_contingency


def get_contingency_table(field1: str, field2: str):
    '''

    :param field1:
    :param field2:
    :return: таблица сопряженности
    '''

    cross_table = pd.crosstab(data[field1], data[field2])
    return cross_table

def pearsons_chi2(crosstab, correction=False):
    '''
    :param crosstab: numpy.ndarray -- table of actual frequences
    :param correction: bool -- use Yates correction
    :return: tuple -- (chi2 statistic, p-value, table of expected values)
    '''
    chi2_stat, pval, df, expected = chi2_contingency(crosstab, correction=correction)
    return chi2_stat, pval, expected


def exact_fisher(crosstab, correction=False):
    '''
    :param crosstab: numpy.ndarray -- table of actual frequences
    :param correction: bool -- use Yates correction
    :return: tuple -- (chi2 statistic, p-value,)
    '''
    numpy2ri.activate()
    stats = importr('stats')
    
    if correction:
        return stats.fisher_test(crosstab, simulate_p_value=correction, B=5000)
    else:
        try:
            return stats.fisher_test(crosstab, simulate_p_value=correction, B=5000)
        except rpy2.rinterface.RRuntimeError:
            return 'Fisher test cannot be performed!'


def choose_method(field1: str, field2: str):
    '''
        super duper AI function for choosing tests

        :param field1:
        :param field2:
        :return: 
    '''
    crosstab = get_contingency_table(field1, field2)
    if np.all(crosstab > 10):
        return pearsons_chi2(crosstab, False)
    elif np.any((crosstab >= 5) & (crosstab <= 9)):
        return pearsons_chi2(crosstab, True)
    # TODO 

