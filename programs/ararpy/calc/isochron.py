#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - calc - data
# ==========================================
#
# Get plot data, including isochron diagram data points, age spectra data
#
"""

from math import atan, cos, sin
from . import arr
import numpy as np


def get_data(x: list, sx: list, y: list, sy: list, z: list, sz: list, f: int = 1):
    """
    Get isochron data based on isotopic values. Values of two x and y axes of isochron
    plots are x / z and y / z.

    Parameters
    ----------
    x :
    sx :
    y :
    sy :
    z :
    sz :
    f :

    Returns
    -------
    2D lists  [X, sX, Y, sY, Ri]
        X and Y are coordinate values of data points in x and y axes respectively.
        sX and sY are corresponding errors. Ri is a list of error correlation factors.
    """
    if np.issubdtype(type(f), np.integer) and f > 1:
        sx, sy, sz = np.divide([sx, sy, sz], f)
    # x / z
    k0, k1 = arr.div((x, sx), (z, sz))
    # y / z
    k2, k3 = arr.div((y, sy), (z, sz))
    # ri
    k4 = arr.cor(np.divide(sx, x), np.divide(sy, y), np.divide(sz, z))
    return [k0, k1, k2, k3, k4]


def get_3d_data(x1: list, sx1: list, x2: list, sx2: list,
                x3: list, sx3: list, z: list, sz: list, f: int = 1):
    """ Get values of three axes, x, y, z, based on the given isotopic values
    x = x1 / z, y = x2 / z, z = x3 / z
    Parameters
    ----------
    x1
    sx1
    x2
    sx2
    x3
    sx3
    z
    sz
    f

    Returns
    -------
    list.
    """
    if np.issubdtype(type(f), np.integer) and f > 1:
        sx1, sx2, sx3 = np.divide([sx1, sx2, sx3], f)
    # x1 / z
    k0, k1 = arr.div((x1, sx1), (z, sz))
    # x2 / z
    k2, k3 = arr.div((x2, sx2), (z, sz))
    # x3 / z
    k4, k5 = arr.div((x3, sx3), (z, sz))
    # r1 between x and y
    r1 = arr.cor(np.divide(sx1, x1), np.divide(sx2, x2), np.divide(sz, z))
    # r2 between x and z
    r2 = arr.cor(np.divide(sx1, x1), np.divide(sx3, x3), np.divide(sz, z))
    # r3 between y and z
    r3 = arr.cor(np.divide(sx2, x2), np.divide(sx3, x3), np.divide(sz, z))
    return [k0, k1, k2, k3, k4, k5, r1, r2, r3]


def get_ellipse(x: float, sx: float, y: float, sy: float, r: float, plt_sfactor: int = 1, size: int = 24):
    """ Error ellipses of data points in isochrons. Get 24 points of a ellispse

    Parameters
    ----------
    x
    sx
    y
    sy
    r
    plt_sfactor
    size

    Returns
    -------
    list of 24 points. [[x1, y1], ..., [x24, y24]]
    """
    x, sx, y, sy, r = float(x), float(sx), float(y), float(sy), float(r)
    Qxx = sx ** 2
    Qxy = sx * sy * r
    Qyy = sy ** 2
    # Calculate the ellipse's short semi-axial and long semi-axial
    k = pow((Qxx - Qyy) ** 2 + 4 * Qxy ** 2, 0.5)
    Qee = (Qxx + Qyy + k) / 2
    Qff = (Qxx + Qyy - k) / 2
    e = pow(Qee, 0.5)  # long semi-axial
    f = pow(Qff, 0.5)  # short semi-axial
    phi_e = atan((Qee - Qxx) / Qxy) if Qxy != 0 else 0 if Qxx >= Qyy else np.pi / 2  # radian

    # adjust
    if plt_sfactor == 1:
        v = 2.279  # 68% confidence limit, 1 sigma
    elif plt_sfactor == 2:
        v = 5.991  # 95% confidence limit, 2 sigma, Isoplot R always gives ellipse with 95% confidence
    else:
        v = 1
    e = e * pow(v, 0.5)
    f = f * pow(v, 0.5)

    ellipse_points = []
    for i in range(size):
        theta = i * 2 / size * np.pi
        ellipse_points.append([
            e * cos(theta) * cos(phi_e) - f * sin(theta) * sin(phi_e) + x,
            e * cos(theta) * sin(phi_e) + f * sin(theta) * cos(phi_e) + y
        ])

    return ellipse_points


def get_line_points(xscale, yscale, coeffs=None):
    """

    Parameters
    ----------
    xscale : x boundary, [min, max]
    yscale : y boundary, [min, max]
    coeffs : y = coeffs[0] + coeffs[1:] * [x]

    Returns
    -------
    List of data points
    """

    if not isinstance(coeffs, list) or len(coeffs) < 2:
        raise ValueError(f"Coeffs should be a list with length with 2.")
    get_y = lambda x: coeffs[0] + coeffs[1] * x
    get_x = lambda y: (y - coeffs[0]) / coeffs[1] if coeffs[1] != 0 else None
    res = []
    for point in [
        [xscale[0], get_y(xscale[0])], [xscale[1], get_y(xscale[1])],
        [get_x(yscale[0]), yscale[0]], [get_x(yscale[1]), yscale[1]],
    ]:
        if xscale[0] <= point[0] <= xscale[1] and yscale[0] <= point[1] <= yscale[1]:
            res.append(point)
    return res


def get_set_data(total_data: list, set1_index: list, set2_index: list, unselected_index: list):
    """

    Parameters
    ----------
    total_data
    set1_index
    set2_index
    unselected_index

    Returns
    -------

    """
    set_1, set_2, unslected = [], [], []
    # Remove string and None type in data
    none_index = []
    for each in total_data:
        none_index = none_index + [key for key, val in enumerate(each) if isinstance(val, (str, type(None)))]
    none_index = list(set(none_index))
    none_index.sort(reverse=True)
    for each in total_data:
        for i in none_index:
            each.pop(i)
    set1_index.sort()
    set2_index.sort()
    for col in total_data:
        unslected.append([col[i] for i in unselected_index if i < len(col)])
        set_1.append([col[i] for i in set1_index if i < len(col)])
        set_2.append([col[i] for i in set2_index if i < len(col)])
    return set_1, set_2, unslected
