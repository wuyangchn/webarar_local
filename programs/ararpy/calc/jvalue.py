#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - calc - jvalue
# ==========================================
#
#
#
"""
import numpy as np


def j_value(age, sage, r, sr, f, rsf):
    """ Calculate J value according to the given age and the ratio

    Parameters
    ----------
    age : age of the reference standard sample, in Ma
    sage : 1 sigma error of age
    r : 40/39 ratio of the reference standard standard sample
    sr : 1 sigma error of 40/39 ratio
    f : decay constant(lambda) of K
    rsf : relative error of decay constant

    Returns
    -------
    tuple of  J value and error
    """
    age, sage, r, sr, f, rsf = np.array([age, sage, r, sr, f, rsf])
    f = f * 1000000  # exchange to unit of Ma
    rsf = f * rsf / 100  # exchange to absolute error
    k0 = (np.exp(f * age) - 1) / r
    v1 = rsf ** 2 * (age * np.exp(f * age) / r) ** 2
    v2 = sage ** 2 * (f * np.exp(f * age) / r) ** 2
    v3 = sr ** 2 * ((1 - np.exp(f * age)) / r ** 2) ** 2
    k1 = np.sqrt(v1 + v2 + v3)
    return k0, k1
