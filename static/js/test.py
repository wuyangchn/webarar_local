#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2024 Yang 
# webarar - test
# ==========================================
#
#
# 
"""

# === External import ===
import traceback
import numpy as np
import pandas as pd
from scipy.stats import distributions
from scipy.optimize import fsolve
import warnings
from scipy.optimize import minimize
warnings.simplefilter(action="ignore", category=RuntimeWarning)


def york2(x: list, sx: list, y: list, sy: list, ri: list, f: int = 1,
          convergence: float = 0.001, iteration: int = 100):
    """
    Parameters
    ----------
    x : isochron x-axis
    sx : standard error of x
    y : isochron y-axis, y = b + m * x
    sy : standard error of y
    ri : error correlation coefficient of errors of x and y
    f : factor of errors, default 1
    convergence: float. Convergence tolerate, default 0.001
    iteration: int. Number of iteration, default 100

    Returns
    -------
    Intercept | Error | slope | Error | MSWD | Convergence | Number of Iterations | error magnification | other
     b, sb, a, sa, mswd, dF, Di, k, r2, chi_square, p_value
    b, seb, m, sem, mswd, abs(m - last_m), Di, k, r2, chi_square, p_value, avg_err_s
    """
    data = np.array([x, sx, y, sy, ri])
    data = data[:, np.where(
        np.logical_or(data == np.inf, pd.isna(data)), False, True).all(axis=0)].astype(np.float64)
    x, sx, y, sy, ri = data
    n = data.shape[-1]
    X, sX, Y, sY, R = data
    # change to 1 sigma
    if np.issubdtype(type(f), np.integer) and f > 1:
        sX, sY = np.divide([sX, sY], f)
    # weights of x and y
    wX = 1 / sX ** 2
    wY = 1 / sY ** 2
    # weight of S
    Z = lambda m, b: wX * wY / (m ** 2 * wY + wX - 2 * m * R * (wX * wY) ** .5)
    # weighted mean of X and Y
    mX = lambda m, b: sum(Z(m, b) * X) / sum(Z(m, b))
    mY = lambda m, b: sum(Z(m, b) * Y) / sum(Z(m, b))
    # Equation to minimize
    S = lambda m, b: sum(Z(m, b) * (Y - m * X - b) ** 2)
    # Slope by OLS is used as the initial values in weights calculation
    temp_lst = linest(Y, X)
    if not temp_lst:
        return False
    b, seb, m, sem = temp_lst[5][0], temp_lst[6][0], temp_lst[5][1], temp_lst[6][1]
    b = mY(m, b) - m * mX(m, b)
    last_m = 1e10
    Di = 0  # Iteration number
    mswd, k = 1, 1  # Initial return values
    while abs(m - last_m) >= abs(m * convergence / 100):
        last_m = m
        U = X - mX(m, b)
        V = Y - mY(m, b)
        # Expression from York 2004, which differs to York 1969
        Up = Z(m, b) ** 2 * V * (U / wY + m * V / wX - R * (V + m * U) / (wX * wY) ** .5)
        Lo = Z(m, b) ** 2 * U * (U / wY + m * V / wX - R * (V + m * U) / (wX * wY) ** .5)
        m = sum(Up) / sum(Lo)  # New slope
        b = mY(m, b) - m * mX(m, b)  # From York 2004, calculate b again after final value of m has been obtained
        sumUUZ = sum(U * U * Z(m, b))
        sumXXZ = sum(X * X * Z(m, b))
        sem = 1 / sumUUZ ** .5
        seb = (sumXXZ / sum(Z(m, b))) ** .5 * sem
        mswd = S(m, b) / (n - 2)
        # print(f"York 2004 regression, m = {m}, b = {b}, S = {S(m, b)}, Di = {Di}")
        if mswd > 1:
            k = mswd ** .5  # k为误差放大系数
        else:
            k = 1

        sem = sem * k
        seb = seb * k

        Di = Di + 1
        if Di >= iteration:
            break

    # Calculate Y values base on the regression results
    estimate_y = b + m * X
    resid = (estimate_y - Y) ** 2
    reg = (estimate_y - np.mean(estimate_y)) ** 2
    ssresid = sum(resid)  # residual sum of squares / sum squared residual
    ssreg = sum(reg)  # regression sum of square
    sstotal = ssreg + ssresid  # total sum of squares
    r2 = ssreg / sstotal if sstotal != 0 else np.inf  # r2 = ssreg / sstotal
    chi_square = mswd * (n - 2)
    p_value = distributions.chi2.sf(chi_square, n - 2)
    # average error of S
    err_s = lambda m, b: list(map(lambda Zi, Yi, Xi: (1 / Zi) ** (1./2.) / abs(Yi - m * Xi - b), Z(m, b), y, x))
    avg_err_s = sum(err_s(m, b)) / len(x) * 100

    # print('----------------------------------------------------------------')
    # print('截距>>>' + str(b) + '  ' + '误差>>>' + str(seb))
    # print('斜率>>>' + str(m) + '  ' + '误差>>>' + str(sem))
    # print('Absolute Convergence' + '>>>' + str(abs(m - last_m)))
    # print('Number of Iterations' + '>>>' + str(Di))
    # print('MSWD' + '>>>' + str(mswd))
    # print('Error Magnification>>>' + str(k))
    # print('----------------------------------------------------------------')

    # keys = [
    #     k, sk, m, sm, mswd, conv, iter, mag, r2, chisq, p, avg_err
    # ]

    return b, seb, m, sem, mswd, abs(m - last_m), Di, k, r2, chi_square, p_value, avg_err_s


def linest(a0: list, a1: list, *args):
    """
    Parameters
    ----------
    a0 : known_y's, y = b + m * x
    a1 : known_x's
    args : more known_x's

    Returns
    -------
    intercept | standard error | relative error | R2 | MSWD | other params: list |
             error of other params: list | equation | m_ssresid (y估计值的标准误差)

    """
    # beta = (xTx)^-1 * xTy >>> xtx * beta = xty
    # crate matrix of x and y, calculate the transpose of x
    if not args:
        x = np.concatenate(([[1]*len(a1)], [a1]), axis=0).transpose()
    else:
        x = np.concatenate(([[1]*len(a1)], [a1], args), axis=0).transpose()
    n = x.shape[-1]  # number of unknown x, constant is seen as x^0
    m = x.shape[0]  # number of data
    y = np.array([a0]).transpose()
    try:
        inv_xtx = np.linalg.inv(np.matmul(x.transpose(), x))
    except np.linalg.LinAlgError:
        raise np.linalg.LinAlgError(f"The determinant of the given matrix must not be zero ")
    beta = np.matmul(inv_xtx, np.matmul(x.transpose(), y))

    # calculate Y values base on the fitted formula
    estimate_y = np.matmul(x, beta)
    resid = (estimate_y - y) ** 2
    reg = (estimate_y - np.mean(estimate_y)) ** 2
    ssresid = resid.sum()
    ssreg = reg.sum()
    sstotal = ssreg + ssresid
    df = m - n
    m_ssresid = ssresid / df
    se_beta = (m_ssresid * np.diagonal(inv_xtx)) ** .5
    beta = beta.transpose()[0]
    rse_beta = se_beta / beta
    r2 = ssreg / sstotal if sstotal != 0 else np.inf

    def get_adjusted_y(*args):
        args = [[1] * len(args[0]), *args]
        return [sum([beta[i] * args[i][j] for i in range(len(beta))]) for j in range(len(args[0]))]

    return beta[0], se_beta[0], rse_beta[0] * 100, r2, m_ssresid, beta, se_beta, get_adjusted_y, m_ssresid





a = york2([1,2,3,4,5],[0.001,0.002,0.003,0.004,0.005], [1.1,1.9,3.1,4.2,4.9],[0.001,0.002,0.003,0.004,0.005],[0.001,0.002,0.003,0.004,0.005])
print(a)
