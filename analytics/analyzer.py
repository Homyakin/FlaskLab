import numpy as np
import pandas as pd
import scipy.stats as st
import rpy2
import rpy2.robjects.numpy2ri as numpy2ri
from rpy2.robjects.packages import importr
from scipy.stats import chi2_contingency
from scipy.stats.contingency import expected_freq
from statsmodels.formula.api import ols
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms
from .processing import FileProcessor
from sklearn.decomposition import PCA
import random
import string

URL = r'https://sci2s.ugr.es/keel/dataset/data/classification/winequality-red.zip'
path_to_file = './app/data/winequality-red.dat'


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


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


def anova_cols(data, collist):
    """
    Conducts ANOVA procedure

    :param data: data to analyze
    :type data: list 
    :param collist: columns to include in analysis
    :type collist: list

    :return: string with result
    """

    if len(collist) == 1:
        return 'None'
    res = ''
    data = pd.DataFrame(data, columns=collist)
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
            res += '!P-value < 0.05 -> cut 100 random\n'
            data = data.sample(100)
            X = X[X.index.isin(data.index)]
            y = y[y.index.isin(data.index)]
        else:
            res += '!P-value > 0.05 -> ok, normal distribution\n'
    else:
        res += '!P-value > 0.05 -> ok, normal distribution\n'

    formula = 'Income ~ '
    formula += ' * '.join([f'C({col})' for col in X.columns])
    model = ols(formula, data).fit()
    res += str(model.summary2().tables[2]) + '\n\n'
    # print(model.summary2().tables[2])
    g = data.groupby(list(X.columns))['Income']
    res += f'ANOVA test:\n'
    stat, pval = st.f_oneway(*[data for name, data in g])
    res += f'Statistic = {stat:.4f}, P-value = {pval:.4f}\n'
    if pval < .05:
        res += f"!P-value < 0.05 -> Income depends on {', '.join(X.columns)}\n\n"
    else:
        res += f"!P-value >= 0.05 -> Income doesn\'t depend on {', '.join(X.columns)}\n\n"
        res += '?Again\n\n'
        res += anova_cols(data.drop(columns=collist[0]), collist[1:])
    return res


def update_data():
    """
    Updates local data from URL

    :return: status (Ok/not ok)
    :rtype: str
    """

    processor = FileProcessor()
    processor.download_file(URL)
    status = processor.unzip_file()
    return status


def draw_ellipse(x_col, y_col):
    """
    Draws confident ellips within two columns
    
    :param x_col: first column
    :type x_col: str
    :param y_col: second column
    :type y_col: str

    :return: None
    """

    processor = FileProcessor()
    df = processor.parse_file(path_to_file)
    fig, ax = plt.subplots()
    confidence_ellipse(df[x_col], df[y_col], ax, edgecolor='red')
    ax.scatter(df[x_col], df[y_col], marker='.')
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_title(f'Confident ellipse of {x_col} and {y_col}')
    fname = f'./app/static/ellipse{randomword(10)}.svg'
    fig.savefig(fname=fname, dpi=300, format='svg')
    return fname


def confidence_ellipse(x, y, ax, p_value=0.05, facecolor='none', **kwargs):
    """
    Create a plot of the covariance confidence ellipse of *x* and *y*.

    Parameters
    ----------
    x, y : array-like, shape (n, )
        Input data.

    ax : matplotlib.axes.Axes
        The axes object to draw the ellipse into.

    n_std : float
        The number of standard deviations to determine the ellipse's radiuses.

    Returns
    -------
    matplotlib.patches.Ellipse

    Other parameters
    ----------------
    kwargs : `~matplotlib.patches.Patch` properties
    """

    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    cov = np.cov(x, y)
    pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
    # Using a special case to obtain the eigenvalues of this
    # two-dimensionl dataset.
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0),
                      width=ell_radius_x * 2,
                      height=ell_radius_y * 2,
                      facecolor=facecolor,
                      **kwargs)

    if 0 < p_value < 1:
        n_std = np.sqrt(-2 * np.log(p_value))
    else:
        print("P-value must be between 0 and 1")
    # Calculating the stdandard deviation of x from
    # the squareroot of the variance and multiplying
    # with the given number of standard deviations.
    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)

    # calculating the stdandard deviation of y ...
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)


def define_equation(min_variance_explained=.95):
    """
    Function that calculates transition matrix U

    :param X: input dataset
    :type X: numpy.ndarray or pandas.DataFrame
    :param min_variance_explained: minimum sum of variance that should
                                   be explained bu principal components
    :type min_variance_explained: float

    :return: components of U and number of components
    :rtype: tuple
    """

    processor = FileProcessor()
    df = processor.parse_file(path_to_file)
    X = df.drop(columns=['Quality'])
    X = (X - X.mean()) / X.std()
    for n_comp in range(1, min(X.shape) + 1):
        pca = PCA(n_components=n_comp, random_state=11)
        pca.fit_transform(X)
        if sum(pca.explained_variance_ratio_) >= min_variance_explained:
            return pca.components_, pca.n_components_




def print_latex(u):
    """
    Function that creates latex-based strings with equations
    of principal components from transition matrix U

    :param u: transtion matrix
    :type u: numpy.ndarray with shape (2x2)

    :return: latex-based strings with equations
    :rtype: list
    """

    equations = []

    for j, row in enumerate(u, start=1):
        equation = ''
        equation += r'z_{%d} = ' % (j, )
        for i, val in enumerate(row, start=1):
            if i == 1 and val >= 0:
                equation += '%.4f x_{%d}' % (val, i)
                continue
            else:
                equation += '%+.4f x_{%d}' % (val, i)
                continue
        equations.append(equation)

    for j, row in enumerate(u.T, start=1):
        equation = ''
        equation += r'x_{%d} = ' % (j,)
        for i, val in enumerate(row, start=1):
            if i == 1 and val >= 0:
                equation += '%.4f z_{%d}' % (val, i)
                continue
            else:
                equation += '%+.4f z_{%d}' % (val, i)
                continue
        equations.append(equation)
    return equations
