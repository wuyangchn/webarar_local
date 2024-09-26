#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - calc - err.py
# ==========================================
#
# This package contains error propagation functions
#
"""

import numpy as np
import pandas as pd


def add(*args: float) -> float:
    """
        For Y = X1 +/- X2 +/- ... +/- Xn
    Args:
        *args:errors in 1 sigma

    Returns: float, propagated error

    """
    k = sum([i ** 2 for i in args]) ** .5
    return k


def mul(*args: tuple) -> float:
    """
        For Y = X1 * X2 * ... * Xn
    Args:
        *args: tuple, (v1, s1), (v2, s2), ...

    Returns: float, propagated error

    """
    # k = abs(np.prod([arg[0] for arg in args])) * sum([np.divide(arg[1] ** 2, arg[0] ** 2) for arg in args]) ** .5
    v = np.ma.array(args, mask=False)
    k = 0
    for i in range(v.shape[0]):
        v.mask[i, 0] = True
        k += np.prod(v[:, 0]) ** 2 * v[i, 1] ** 2
        v.mask[i, 0] = False

    return np.sqrt(k)


def rec(a: tuple) -> float:
    """
        For Y = 1 / X
    Args:
        *a: tuple, (value, error)

    Returns: float, propagated error

    """
    if isinstance(a, pd.Series):
        a = a.values.tolist()
    k = np.divide(abs(a[1]), a[0] ** 2)
    return k


def div(*args: tuple) -> float:
    """
        For Y = X1 / X2 / ... / Xn
    Args:
        *args: float, (v1, s1), (v2, s2), ...

    Returns: float, propagated error

    """
    args = [arg if index == 0 else (np.divide(1, arg[0]), rec(arg)) for index, arg in enumerate(args)]
    k = mul(*args)
    return k


def pow(a0: tuple, a1: tuple):
    """
        For y = pow(a0, a1), y = a0 ^ a1
    Args:
        a0: tuple, (value, error)
        a1: tuple, (value, error)

    Returns: float, propagated error

    """
    p1 = a0[1] ** 2 * (a1[0] * a0[0] ** (a1[0] - 1)) ** 2
    p2 = a1[1] ** 2 * (a0[0] ** a1[0] * np.log(a0[0])) ** 2
    k = (p1 + p2) ** .5
    return k


def log(a: tuple) -> float:
    """
        For y = ln(a)
    Args:
        a: tuple, (value, error)

    Returns: float, propagated error

    """
    k = np.divide(abs(a[1]), abs(a[0]))
    return k


def cor(sX: float, sY: float, sZ: float):
    """
    Calculate correlation coefficient of errors.

    Parameters
    ----------
    sX : relative error of X, where X/Z vs. Y/Z
    sY : relative error of Y
    sZ : relative error of Z

    Returns
    -------
    """
    if sZ == 0:
        return np.nan
    k = np.divide(sZ ** 2, ((sZ ** 2 + sX ** 2) * (sZ ** 2 + sY ** 2)) ** .5)
    return k
