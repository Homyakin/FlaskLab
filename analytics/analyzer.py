import numpy as np
import pandas as pd
import scipy.stats as st
import rpy2
import rpy2.robjects.numpy2ri as numpy2ri
from rpy2.robjects.packages import importr
from scipy.stats import chi2_contingency
from scipy.stats.contingency import expected_freq
from statsmodels.api import OLS
from statsmodels.tools.tools import add_constant


def get_expected_values(crosstab):
    expected = expected_freq(crosstab)
    return expected


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
    chi2_stat, pval, _, expected = chi2_contingency(crosstab,
                                                     correction=correction)

    result = f'''
    Used method: Pearson's chi2;\n
    Yates correction: {'Yes' if correction else 'No'};\n
    Chi2 statistic = {chi2_stat:.4f};\n
    P-value = {pval:.4f}
    '''
    return result, expected


def exact_fisher(crosstab, length, correction=False):
    """
    :param crosstab: numpy.ndarray -- table of actual frequencies
    :param correction: bool -- use Yates correction
    :return: tuple -- (chi2 statistic, None)
    """
    numpy2ri.activate()
    stats = importr('stats')

    try:
        result = str(stats.fisher_test(crosstab,
                                       simulate_p_value=correction, B=length * 10))
    except rpy2.rinterface_lib.embedded.RRuntimeError:
        result = str(stats.fisher_test(crosstab, simulate_p_value=True, B=length * 10))

    return str(result)


def get_statistic_and_expected_table(crosstab):
    """
        super duper AI function for choosing tests

        :param crosstab: pd.crosstab() for field1 and field2:
        :return: tuple (function result, table of expected values or None)
    """
    expected_df = pd.DataFrame(get_expected_values(crosstab).T)
    crosstab = crosstab.values
    expected = expected_df.values
    length = np.sum(expected)
    if length > 10000:
        return exact_fisher(crosstab, length, True), expected_df
    else:
        if np.all(expected >= 10):
            return pearsons_chi2(crosstab, False)
        elif np.any((expected > 5) & (expected <= 9)):
            return pearsons_chi2(crosstab, True)
        else:
            return exact_fisher(crosstab, length, False), expected_df


def anova(data, cols):
    res = ''
    data = pd.DataFrame(data, columns=cols)
    data = data[data['Gender'].isin(['male', 'female'])]
    data.dropna(inplace=True)
    X = data.loc[:, data.columns != 'Income']
    y = data['Income']
    # Normality tests
    if len(y) > 500:
        test = st.jarque_bera
        res += 'Big dataset -> Jarque-Bera test\n'
    else:
        test = st.shapiro
        res += 'Big dataset -> Shapiro-Wilk\'s test\n'

    stat, pval = test(y)
    res += f'Statistic = {stat:.4f}, P-value = {pval:.4f}\n\n'

    if pval < .05:
        res += '!P-value < 0.05 -> log transformation and test again\n'
        y = np.log(y + 1)
        stat, pval = test(y)
        res += f'Statistic = {stat:.4f}, P-value = {pval:.4f}\n'
        if pval < .05:
            res += '!P-value < 0.05 -> cut 100 first\n'
            data = data.sample(100)
            X = X[X.index.isin(data.index)]
            y = y[y.index.isin(data.index)]
        else:
            res += '!P-value > 0.05 -> ok, normal distribution\n'
    else:
        res += '!P-value > 0.05 -> ok, normal distribution\n'
    for column in X.columns:
        res += f'?Column: {column}\nLinear model:\n'
        exog = pd.get_dummies(X[column], drop_first=True)
        model = OLS(y, add_constant(exog)).fit()
        res += str(model.summary2())
        g = data.groupby(column)['Income']
        res += f'ANOVA test:\n'
        stat, pval = st.f_oneway(*[data for name, data in g])
        res += f'Statistic = {stat:.4f}, P-value = {pval:.4f}\n'
        if pval < .05:
            res += f'!P-value < 0.05 -> Income depends on {column}\n\n'
        else:
            res += f'!P-value >= 0.05 -> Income doesn\'t depend on {column}\n\n'
    return res
