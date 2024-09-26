#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - calc - raw_funcs
# ==========================================
#
#
#
"""
import traceback
import numpy as np
from .arr import transpose, is_twoD
from . import regression


"""get regression results for raw data points"""


def get_raw_data_regression_results(points_data, unselected: list = None):
    """
    Parameters
    ----------
    points_data : two dimensional list. like [[x1, y1], [x2, y2], ..., [xn, yn]]
    unselected :

    Returns
    -------

    """
    # if unselected is None:
    #     unselected = []
    # linesData = []
    linesResults, regCoeffs = [], []
    # un_x = transpose(unselected)[0] if is_twoD(unselected) else []
    reg_handler = [
        regression.linest, regression.quadratic, regression.exponential,
        regression.power, regression.average]
    # size = 50
    # lines_x = [(max(x + un_x) - 0) / size * i for i in range(size + 1)]
    for i in range(len(reg_handler)):
        try:
            x, y = transpose(points_data, ignore=False)
            res = reg_handler[i](a0=y, a1=x)
            # line_data = transpose([lines_x, res[7](lines_x)])
            line_results = res[0:4]
            reg_coeffs = res[5]
            # if np.isin(np.inf, line_data) or np.isin(np.nan, line_data):
            #     raise ZeroDivisionError(f"Infinite value or nan value.")
            if abs(res[0] - min(y)) > 5 * (max(y) - min(y)):
                raise ValueError
        except RuntimeError:
            line_data, line_results, reg_coeffs = [], ['RuntimeError', np.nan, np.nan, np.nan, ], []
        except np.linalg.LinAlgError:
            line_data, line_results, reg_coeffs = [], ['MatrixError', np.nan, np.nan, np.nan, ], []
        except TypeError or IndexError:
            line_data, line_results, reg_coeffs = [], ['NotEnoughPoints', np.nan, np.nan, np.nan, ], []
        except ZeroDivisionError:
            line_data, line_results, reg_coeffs = [], [np.inf, np.nan, np.nan, np.nan, ], []
        except ValueError:
            line_data, line_results, reg_coeffs = [], ['BadFitting', np.nan, np.nan, np.nan, ], []
        except:
            line_data, line_results, reg_coeffs = [], [np.nan, np.nan, np.nan, np.nan, ], []
        # linesData.append(line_data)
        linesResults.append(line_results)
        regCoeffs.append(reg_coeffs)
    return None, linesResults, regCoeffs

