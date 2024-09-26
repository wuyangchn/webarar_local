#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - calc - histogram
# ==========================================
#
#
"""


import numpy as np


def get_data(x: list, s: float = None, r: str = 'sturges', w: float = None, c: int = None):
    """

    Parameters
    ----------
    x : input data to yield bins
    s : starting point
    r : rules, string
    w : bin width or interval, float for specific number
    c : bin count

    Returns
    -------
    tuple. counts: [number of points in each bin], bins: [half bins], s, r, w, c, e, res: [values in each bin]
    """
    if len(x) == 0 or max(x) == min(x):
        return None
    else:
        x = [round(xi, 2) for xi in x]
    if isinstance(r, str) and r.lower().find('square-root') != -1:
        # Square-root choice, used by Excel's Analysis Toolpak histograms and many other
        c = np.ceil(len(x) ** (1. / 2.))
    if isinstance(r, str) and r.lower().find('sturges') != -1:
        # Sturges' formula, Ceiling(log2n)
        c = np.ceil(np.log2(len(x))) + 1
    if isinstance(r, str) and r.lower().find('rice') != -1:
        # Rice Rule
        c = np.ceil(2 * len(x) ** (1. / 3.))
    if isinstance(r, str) and r.lower().find('scott') != -1:
        # Scott's normal reference rule, optimal for random samples of normally distributed data
        w = np.ceil(3.49 * (sum([float(i - sum(x) / len(x)) ** 2 for i in x]) / len(x)) ** (1. / 2.) / len(x) ** (1. / 3.))
        d = 0.5 * 10 ** (int(np.log(w)) - 1)
    if w is None and c is None:
        return get_data(x=x, s=s, w=w, c=c, r='sturges')

    if s is None and isinstance(c, (int, np.float64)):
        d = 0.5 * 10 ** int(np.log(abs(max(x) - min(x)) / c))
    if s is None:
        d = d if min(x) - d >= 0 else min(x)
        s = round(min(x) - d, 2)
        e = round(max(x) + d, 2)
    else:
        e = round(max(x) + min(x) - s, 2)
    if isinstance(c, (int, np.float64)) and not isinstance(w, (int, float, np.float64)):
        w = round(abs(e - s) / c, 2)
    bins = [s + i * w for i in range(10000) if s + (i - 1) * w <= max(x)]
    bins = list(set(bins))
    bins.sort()
    c = len(bins) - 1
    counts = [0] * c
    res = [[]] * c
    half_bins = [round((bins[i] + bins[i + 1]) / 2, 2) for i in range(c)]
    bin_ranges = [[]] * c
    for i in range(c):
        bin_ranges[i] = [round(bins[i], 2), round(bins[i + 1], 2)]
        for xi in x:
            if bins[i] <= xi < bins[i + 1] or bins[i] <= xi <= bins[i + 1] and i == c - 1:
                counts[i] += 1
                res[i].append(xi)

    return counts, half_bins, bin_ranges, s, r, w, c, bins[-1], res


def get_kde(x: list, h: (float, int) = None, a: str = None, k: str = 'normal',
            s: (float, int) = None, e: (float, int) = None, n: int = 200):
    """

    Parameters
    ----------
    x : input data
    h : bandwidth
    a : auto width rule
    k : kernel function name, default is normal, standard normal density function
    s : KDE curve starting point
    e : KDE curve ending point
    n : points number of KDE line

    Returns
    -------

    """
    x = [round(xi, 2) for xi in x]
    x.sort()

    def get_uniform_x(_x: list, _s=s, _e=e, _np=n):
        _s = min(_x) if _s is None else _s
        _e = max(_x) if _e is None else _e
        _line_x = []
        _step = abs(_e - _s) / _np
        _line_x = [_s + i * _step for i in range(_np)] + [_e]
        _line_x.sort()
        return _line_x

    def h_scott(_x, _se):  # Scott, 1992
        return 1.06 * _se * len(_x) ** (-1. / 5.)

    def h_silverman(_x, _se):  # Silverman, 1986
        return 0.9 * min(_se, (_x[int(3 / 4 * len(_x))] - _x[int(1 / 4 * len(_x))]) / 1.34) * len(_x) ** (-1. / 5.)

    # Normal function
    def k_normal(_xi, _u=0, _se=1, _h=h):
        return 1 / (_se * np.sqrt(2 * np.pi)) * (np.exp(-1. / 2. * ((_xi - _u) / (_h * _se)) ** 2))

    def k_epanechnikov(_xi, _u=0, _h=h):
        _xi = (_xi - _u) / _h
        return 3 / 4 * (1 - _xi ** 2) if abs(_xi) <= 1 else 0

    def k_uniform(_xi, _u=0, _h=h):
        _xi = (_xi - _u) / _h
        return 1 / 2 if abs(_xi) <= 1 else 0

    def k_triangular(_xi, _u=0, _h=h):
        _xi = (_xi - _u) / _h
        return 1 - abs(_xi) if abs(_xi) <= 1 else 0

    mean_x = sum(x) / len(x)
    se = np.sqrt(sum([(xi - mean_x) ** 2 for xi in x]) / (len(x) - 1))

    if (a is None or a == 'none') and (h is None or h <= 0):
        # Default rule for h is Scott's rule
        a = 'Scott'
    if isinstance(a, str):
        if a.lower() == 'scott':
            h = h_scott(x, se)
        elif a.lower() == 'silverman':
            h = h_silverman(x, se)
        else:
            a = 'none'
    else:
        a = 'none'

    # Get points that are evenly distributed over the range (min_x, max_x) to get a KDE curve
    line_x = get_uniform_x(_x=x, _s=s, _e=e)

    if k.lower() == 'normal':
        k_normal_res = [[k_normal(_xi, _u=xi, _h=h) for _xi in line_x] for xi in x]
    elif k.lower() == 'epanechnikov':
        k_normal_res = [[k_epanechnikov(_xi, _u=xi, _h=h) for _xi in line_x] for xi in x]
    elif k.lower() == 'uniform':
        k_normal_res = [[k_uniform(_xi, _u=xi, _h=h) for _xi in line_x] for xi in x]
    elif k.lower() == 'triangular':
        k_normal_res = [[k_triangular(_xi, _u=xi, _h=h) for _xi in line_x] for xi in x]
    else:
        return get_kde(x=x, h=h, a=a, k='normal', s=s, e=e, n=n)

    res = [
        sum([k_normal_res[j][i] for j in range(len(x))]) / (len(x) * h) for i in range(len(line_x))
    ]

    return [[line_x, res], h, k, a]

