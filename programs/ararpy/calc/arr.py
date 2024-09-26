#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - calc - arr
# ==========================================
#
# Basic functions related to array-like objects
# List, np.array, pd.DataFrame
#
"""

# === Internal import ===
import traceback

from . import err
# === External import ===
import numpy as np
from scipy.stats import distributions
from types import MethodType
from typing import Optional, List, Union
from decimal import Decimal


# =======================
# Error propagation for array-like objects
# =======================
def mul(*args):
    """
    Parameters
    ----------
    args :
        2D array like objects of numbers
        lists: [[1, 2, 3], [1, 2, 3]], [[3, 4, 5], [3, 4, 5]]
        np.array([[1, 2, 3], [1, 2, 3]]), np.array([[3, 4, 5], [3, 4, 5]])
        pd.DataFrame([[1, 1], [2, 2], [3, 3]]), pd.DataFrame([[3, 3], [4, 4], [5, 5]])

    Returns
    -------
    2D list, [values, errors]
    """
    v = np.array(args)
    res = np.zeros([2, v.shape[-1]], dtype=np.float64)
    for i in range(v.shape[-1]):
        res[0, i] = np.prod(v[:, 0, i])
        res[1, i] = err.mul(*v[:, :, i])

    return res


def div(a, b):
    """
    Y = a / b
    Parameters
    ----------
    a : two dimensional array like objects of numbers
    b : two dimensional array like objects of numbers
        lists: [[1, 2, 3], [1, 2, 3]], [[3, 4, 5], [3, 4, 5]]
        np.array([[1, 2, 3], [1, 2, 3]]), np.array([[3, 4, 5], [3, 4, 5]])
        pd.DataFrame([[1, 1], [2, 2], [3, 3]]), pd.DataFrame([[3, 3], [4, 4], [5, 5]])

    Returns
    -------
    [values, errors]
    """
    n = np.shape([a, b])[-1]
    k0, k1 = [], []
    for i in range(n):
        k0.append(np.divide(a[0][i], b[0][i]))
        k1.append(
            (np.divide(a[1][i] ** 2, b[0][i] ** 2) +
             np.divide(a[0][i] ** 2 * b[1][i] ** 2, b[0][i] ** 4)) ** .5)
    return [k0, k1]


def rec(a):
    """
    Parameters
    ----------
    a :
        2D array like objects of numbers

    Returns
    -------
        two dimensional list, [values, errors]
    """
    try:
        n = np.shape(a)[1]
        k0, k1 = [], []
        for i in range(n):
            k0.append(np.divide(1, a[0][i]))
            k1.append(err.rec((a[0][i], a[1][i])))
        return [k0, k1]
    except IndexError:
        return [1 / a[0], err.rec(a)]


def add(*args):
    """ For y = x1 + x2 + ...
    Parameters
    ----------
    args : two dimensional lists, or tuple of two list
        [x1, sx1], [x2, sx2], ...

    Returns
    -------
    list
    """
    n = np.shape(args)[-1]
    k0, k1 = [], []
    for i in range(n):
        k0.append(sum([arg[0][i] for arg in args]))
        k1.append(err.add(*[arg[1][i] for arg in args]))
    return [k0, k1]


def sub(*args):
    """ For y = x1 - x2 - ...
    Parameters
    ----------
    args : two dimensional lists, or tuple of two list
        [x1, sx1], [x2, sx2], ...

    Returns
    -------

    """
    args = np.array(args, dtype=np.float64)
    args[np.isnan(args)] = 0
    n = np.shape(args)[-1]
    k0, k1 = [], []
    for i in range(n):
        k0.append(sum([arg[0][i] * [-1, 1][index == 0] for index, arg in enumerate(args)]))
        k1.append(err.add(*[arg[1][i] for arg in args]))
    return [k0, k1]


def cor(sx: list, sy: list, sz: list):
    """
    Parameters
    ----------
    sx
    sy
    sz

    Returns
    -------

    """
    n = np.shape([sx, sy, sz])[-1]
    return [err.cor(sx[i], sy[i], sz[i]) for i in range(n)]


def mul_factor(a, factor, isRelative: bool = False):
    """ a × factor
    Parameters
    ----------
    a :
    factor : two dimensional list
    isRelative : if the error of factor is relative

    Returns
    -------

    """
    f, sf = np.array(factor)
    if isRelative:
        sf = f * sf / 100
    return mul(a, (f, sf))


def rec_factor(factor, isRelative: bool = False):
    """ 1 / factor
    Parameters
    ----------
    factor : two dimensional list
    isRelative : if the error of factor is relative

    Returns
    -------

    """
    f, sf = np.array(factor)
    if isRelative:
        sf = f * sf * 100
    return rec((f, sf))


# =======================
# Basic functions for array-like objects
# =======================
def partial(a: list, rows=None, cols=None):
    """ Get partial object from a two dimensional list according to the given rows and cols.

    Parameters
    ----------
    a : two dimensional array-like object with shape of (m, n)
    rows :
        rows index like [1, 2, ...], or int
    cols :
        cols index like [0 ,1, ...], or int

    Returns
    -------
    array-like object, if rows or cols is int, one dimensional list will be returned
    """
    res = []
    try:
        (m, n) = np.shape(a)
    except ValueError:
        # ValueError, the requested array has an inhomogeneous shape
        return partial(homo(a), rows=rows, cols=cols)
    default_col = [np.nan for i in range(n)]
    if rows is None:
        rows = list(range(n))
    if cols is None:
        cols = list(range(m))
    if isinstance(cols, list):
        res = [a[i] if i != -1 else default_col for i in cols]
    elif isinstance(cols, int):
        res = a[cols] if cols != -1 else default_col
    if isinstance(rows, list):
        if isinstance(cols, list):
            res = [[i[j] for j in rows] for i in res]
        else:
            res = [res[i] for i in rows]
    elif isinstance(rows, int):
        res = res[rows]
    return res


def array_as_float(p_object):
    """ Get array of floats from list like object
    Parameters
    ----------
    p_object

    Returns
    -------

    """
    try:
        return np.array(p_object, dtype=np.float64)
    except ValueError as e:
        item = str(e).split('could not convert string to float: ')
        return array_as_float(replace(p_object, item[1][1:-1], np.nan))


def replace(array, old, new):
    """ Replace all old items with new items in a array

    Parameters
    ----------
    array
    old : function or object
    new

    Returns
    -------

    """
    if np.iterable(array) and not isinstance(array, str):
        res = [replace(i, old, new) for i in array]
    else:
        if callable(old):
            if old(array):
                res = new
            else:
                res = old
        elif array in [old]:
            res = new
        else:
            res = array
    return res


def remove(array, old):
    """ Remove all old items

    Parameters
    ----------
    array : n dimensional list
    old : tuple, like (None, ), (None, np.nan)

    Returns
    -------

    """
    if is_oneD(array):
        res = []
        for each in array:
            if each in old:
                continue
            res.append(each)
    else:
        res = [remove(each, old=old) for each in array]
    return res


def merge(*args):
    """ Merge list objects, one dimensional or two dimensional list should be passed in.

    Parameters
    ----------
    args : one or two dimensional list

    Returns
    -------

    """
    res = []
    for arg in args:
        if is_oneD(arg):
            res.append(arg)
        else:
            res = res + arg
    return res


def multi_append(a, *args):
    """
    Parameters
    ----------
    a
    args

    Returns
    -------

    """
    for arg in args:
        a.append(arg)
    return a


def filter(a: list, func: MethodType, get: Optional[MethodType], unique: Optional[bool]):
    """
    Parameters
    ----------
    a
    func
    get
    unique

    Returns
    -------

    """
    res = []
    for i in a:
        if func(i):
            if type(get) is MethodType:
                res.append(get(i))
            else:
                res.append(i)
            if unique:
                return res[0]
    return res


def create_arr(shape: tuple):
    """
    Parameters
    ----------
    shape

    Returns
    -------

    """
    if len(shape) == 1:
        return []
    return [create_arr(shape[1:]) for i in range(shape[0])]


def is_empty(a):
    """ Check if a list is empty. Return True if it is empty, or it is not a list,
    or all items in it are '', None or np.nan.

    Parameters
    ----------
    a : list

    Returns
    -------
    bool. True if a is empty or is not a instance of list
    """
    if not isinstance(a, list) or a == [] or len(a) == 0:
        return True
    for i in a:
        if i not in ['', None, np.nan]:
            return False
    return True


def ndim(obj):
    """

    Parameters
    ----------
    obj

    Returns
    -------

    """
    if np.iterable(obj) and not isinstance(obj, str):
        if len(obj) == 0:
            return 1
        return max([ndim(i) for i in obj]) + 1
    return 0


def is_oneD(obj):
    """ Check if a list-like object is one dimensional
    Parameters
    ----------
    obj

    Returns
    -------

    """
    try:
        return ndim(obj) == 1
    except (ValueError, AttributeError):
        return False


def is_twoD(obj):
    """ Check if a list-like object is two dimensional
    Parameters
    ----------
    obj

    Returns
    -------

    """
    try:
        return ndim(obj) == 2
    except (ValueError, AttributeError):
        return False


def is_homo(obj):
    """ Check if the requested obj is homogeneous

    Parameters
    ----------
    obj

    Returns
    -------

    """
    try:
        np.shape(obj)
    except (ValueError, AttributeError):
        return False
    else:
        return True


def homo(obj):
    """ Get a homogeneous two dimensional list. If the passed list object is inhomogeneous,
    np.nan will be added to make it homogeneous.

    Parameters
    ----------
    obj : two dimensional list

    Returns
    -------

    """
    if not is_twoD(obj):
        return obj
    try:
        np.shape(obj)
    except (ValueError, AttributeError):
        pass
    else:
        return obj
    length = max(len(i) for i in obj)
    return [i if len(i) == length else i + [np.nan] * (length - len(i)) for i in obj]


def transpose(obj, ignore: bool = True):
    """ Get the transpose of a list-like object
    Parameters
    ----------
    obj : two dimensional list-like object
    ignore : return obj if ignore error is true

    Returns
    -------

    """
    try:
        if not is_twoD(obj):
            raise ValueError("The requested object is not two dimensional.")
        obj = obj if is_homo(obj) else homo(obj)
        m, n = np.shape(obj)
        return [[obj[i][j] for i in range(m)] for j in range(n)]
    except (ValueError, TypeError):
        print(traceback.format_exc())
        if ignore:
            return obj
        else:
            raise ValueError


def get_item(obj: list, loc: (list, tuple, int), default: Union[str, int, float, bool] = None,
             base: Union[int, tuple, list] = 0) -> Union[str, int, float, bool]:
    """ Get item from a n-dimension list
    Parameters
    ----------
    obj
    loc
    default
    base

    Returns
    -------
    """
    try:
        if not isinstance(obj, list):
            raise TypeError
        if isinstance(loc, int):
            loc = [loc]
        if isinstance(base, int):
            base = [base for i in range(len(loc))]
        if len(loc) == 1:
            return obj[loc[0] - base[0]] if loc[0] - base[0] >= 0 else ""
        if loc[0] - base[0] < 0:
            raise IndexError
        return get_item(obj[loc[0] - base[0]], loc[1:], base=base[1:], default=default)
    except (IndexError, TypeError, ValueError):
        return default
    raise ValueError(f"Cannot get a item from {obj = }, {loc = }")


# =======================
# Weighted mean
# =======================
def wtd_mean(a: list, e: list, sf: int = 1, adjust_error: bool = True):
    """
    :param a: x
    :param e: error
    :param sf: sigma number for age error, default = 1
    :param adjust_error: adjust error by multiply Sqrt(MSWD)
    :return: error-weighted mean value | error in 1 sigma | number of data points | MSWD | Chisq | P value
    """
    a, e = np.array([a, e])
    e = e / sf  # change error to 1 sigma
    k2 = a.size
    df = k2 - 1
    if k2 == 0:
        return np.nan, np.nan, 0, np.nan, np.nan, np.nan
    wt = 1 / e ** 2
    k0 = sum(a * wt) / sum(wt)  # error weighting
    k4 = sum((a - k0) ** 2 * wt)  # Chi square
    k3 = k4 / df  # MSWD mentioned in Min et al., 2000
    if adjust_error:
        k1 = (k3 / sum(wt)) ** .5
    else:
        k1 = (1 / sum(wt)) ** .5
    k5 = distributions.chi2.sf(k4, df)
    return k0, k1, k2, k3, k4, k5


# =======================
# Number format
# =======================
def change_number_format(numbers: Union[list, tuple], flag: str = "Scientific", precision: int = None):
    """
    Parameters
    ----------
    precision
    flag
    numbers

    Returns
    -------

    """
    flag = flag.replace(" ", "")
    _precision = [len(str(num).split(".")[1]) if "." in str(num) else 0 for num in numbers]
    if flag.startswith("AddZero"):
        precision = max(_precision) if precision is None else precision
        for index, num in enumerate(numbers):
            numbers[index] = str(num) + ('.' if '.' not in str(num) else '') + '0' * (precision - _precision[index])
        return change_number_format(numbers, flag=flag.replace("AddZero", ""), precision=precision)

    if flag.startswith("Scientific"):
        numbers = [
            ("{:." + f"{(len(str(num).replace('.', '')) - 1) if precision is None else precision}" + "e}").format(
                Decimal(str(num))) for num in numbers]
        return change_number_format(numbers, flag=flag.replace("Scientific", ""), precision=precision)

    if flag.startswith("NonZero"):
        numbers = [str(num).rstrip("0") if "." in str(num) else str(num) for num in numbers]
        return change_number_format(numbers, flag=flag.replace("NonZero", ""), precision=precision)

    if flag.startswith("Round"):
        numbers = [str(round(float(num), min(_precision) if precision is None else precision)) for num in numbers]
        return change_number_format(numbers, flag=flag.replace("Round", ""), precision=precision)

    return numbers


if __name__ == '__main__':
    pass

