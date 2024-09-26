#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - calc- spectra
# ==========================================
#
# Spectra
#
"""
import numpy as np


def get_data(y: list, sy: list, x: list, f: int = 1, indices: list = None,
             cumulative: bool = False, successive: bool = True):
    """
    Get spectra data based on passed x, y, and sy.

    Parameters
    ----------
    y :
    sy :
    x :
    f : error factor of sy, 1 or 2 for 1 or 2 sigma
    indices : array-like, default None for all sequences included
        An array of ints indicating which sequences to include.
    cumulative : bool, default False.
        This parameter should be True if x is already cumulative.
    successive : If setting indices successive

    Returns
    -------
    list of lists of float. [x, y1, y2]
    """
    if np.issubdtype(type(f), np.integer) and f > 1:
        sy = np.divide(sy, f)
    dp = np.shape([y, sy, x])[-1]
    if indices is None:
        indices = list(range(dp))
    if successive:
        indices = list(range(min(indices), max(indices) + 1))
    if not cumulative:
        x = np.divide(np.cumsum(x) * 100, sum(x)).tolist()
    k0, k1, k2 = [], [], []
    for i in range(dp):
        if i not in indices:
            continue
        else:
            k0.append([x[i - 1], 0][i == 0])
            k0.append(x[i])
            k1.append(y[i] + sy[i] if i % 2 == 0 else y[i] - sy[i])
            k1.append(y[i] + sy[i] if i % 2 == 0 else y[i] - sy[i])
            k2.append(y[i] - sy[i] if i % 2 == 0 else y[i] + sy[i])
            k2.append(y[i] - sy[i] if i % 2 == 0 else y[i] + sy[i])
    # Close the spectrum
    k0.insert(0, k0[0])
    k0.append(k0[-1])
    k1.insert(0, k2[0])
    k1.append(k2[-1])
    k2.insert(0, k1[0])
    k2.append(k1[-1])
    return [k0, k1, k2]
