#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - calc - regression
# ==========================================
#
# Regression functions
#
"""
from . import arr

# === External import ===
import traceback
import numpy as np
import pandas as pd
from scipy.stats import distributions
from scipy.optimize import fsolve
import warnings
from scipy.optimize import minimize
warnings.simplefilter(action="ignore", category=RuntimeWarning)


""" regression functions for isochrons """


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


def york2_df(data: pd.DataFrame, f: int = 1, convergence: float = 0.001,
             iteration: int = 100) -> pd.DataFrame:
    """
    DataFrame format input and output
    Parameters
    ----------
    data
    f
    convergence
    iteration

    Returns
    -------
    data frame with keys [
            'k', 'sk', 'm1', 'sm1',
            'iter', 'conv', 'rs', 'MSWD', 'R2', 'Chisq', 'Pvalue',  # 'rs' means relative error of the total sum
            'mag', 'abs_conv',  # 'mag' is error magnification factor, 'abs_conv' is absolute convergence at the last time
        ]
    Intercept | Error | slope | Error | MSWD | Convergence | Number of Iterations | error magnification | other
         b, sb, a, sa, mswd, dF, Di, k, r2, chi_square, p_value
    """
    # remove nan, inf from data
    data: pd.DataFrame = data.replace([-np.inf], np.nan).dropna(axis=0)
    data: list = data.transpose().values.tolist()[:5]

    columns = [
        'k', 'sk', 'm1', 'sm1',
        'MSWD', 'abs_conv', 'iter', 'mag', 'R2', 'Chisq', 'Pvalue',  # 'rs' means relative error of the total sum
        'rs'
    ]
    values = york2(*data, f=f, convergence=convergence, iteration=iteration)
    res = pd.DataFrame([list(values)], columns=columns)

    return res


def wtd_3D_regression(x: list, sx: list, y: list, sy: list, z: list, sz: list, r1: list,
                      r2: list, r3: list, f: int = 1, convergence: float = 0.001,
                      iteration: int = 100):
    """
    Error weighted regression for 3D plots
    Parameters
    ----------
    x
    sx
    y
    sy
    z
    sz
    r1 : error correlation between x and y
    r2 : error correlation between x and z
    r3 : error correlation between y and z
    f : factor of errors, default 1.
    convergence : convergence tolerate in percentage, default 0.001 indicating 0.001%
    iteration : number of iteration, default 100

    Returns
    -------
    c (interceept), sc, a, sa, b, sb, S, mswd, r2, abs(a - last_a), Di, k  # length == 12
    """
    n = np.shape([x, sx, y, sy, z, sz, r1, r2, r3])[-1]
    x, sx, y, sy, z, sz, r1, r2, r3 = np.array([x, sx, y, sy, z, sz, r1, r2, r3])
    # change to 1 sigma
    if np.issubdtype(type(f), np.integer) and f > 1:
        sx, sy, sz = np.divide([sx, sy, sz], f)
    if n <= 3:
        return False

    Di = 0

    # Weights of S
    W = lambda a, b: 1 / (
                a ** 2 * sx ** 2 + b ** 2 * sy ** 2 + sz ** 2 + 2 * a * b * r1 * sx * sy -
                2 * a * r2 * sx * sz - 2 * b * r3 * sy * sz)
    # Weighted mean values of X, Y, and Z, respectively
    mX = lambda a, b: sum(W(a, b) * x) / sum(W(a, b))
    mY = lambda a, b: sum(W(a, b) * y) / sum(W(a, b))
    mZ = lambda a, b: sum(W(a, b) * z) / sum(W(a, b))
    # Minimizing this equation
    S = lambda a, b, c: sum(W(a, b) * (a * x + b * y + c - z) ** 2)
    # Calculate new c based on iterated a and b
    new_c = lambda a, b: mZ(a, b) - a * mX(a, b) - b * mY(a, b)
    # Initial values of a, b, and c from OLS
    linest_res = linest(z, x, y)
    c, sc, k2, k3, k4, [_, a, b], [_, sa, sb] = linest_res[0:7]
    c = new_c(a, b)
    k = 1  # Error magnification factor
    last_a = 1e10
    mswd, f = 1000, 0
    # print(f"初始值：a = {a}, b = {b}, c = {c}")
    # ar38ar36 = 0.1885
    # ar40ar36 = (a + b * ar38ar36) * -1 / c
    # print(f"Ar38/Ar36 = {ar38ar36}, Ar40/Ar36 = {ar40ar36}, S = {S(a, b, c)}")
    while abs(a - last_a) >= abs(a * convergence / 100):
        last_a = a
        U = x - mX(a, b)
        V = y - mY(a, b)
        G = z - mZ(a, b)
        # P and Q are Xi - mX and Yi - mY, respectively. These values are obtained by weighted Orthogonal regression
        P = W(a, b) * ((a * sx ** 2 + b * r1 * sx * sy - r2 * sx * sz) * (G - b * V) + (
                    a * b * r1 * sx * sy + b ** 2 * sy ** 2 - a * r2 * sx * sz - 2 * b * r3 * sy * sz + sz ** 2) * U)
        Q = W(a, b) * ((b * sy ** 2 + a * r1 * sx * sy - r3 * sy * sz) * (G - a * U) + (
                a * b * r1 * sx * sy + a ** 2 * sx ** 2 - b * r3 * sy * sz - 2 * a * r2 * sx * sz + sz ** 2) * V)
        a_Up = sum(W(a, b) * P * G).sum() * sum(W(a, b) * Q * V).sum() - \
               sum(W(a, b) * P * V).sum() * sum(W(a, b) * Q * G)
        a_Lo = sum(W(a, b) * P * U).sum() * sum(W(a, b) * Q * V).sum() - \
               sum(W(a, b) * P * V).sum() * sum(W(a, b) * Q * U)
        new_a = a_Up / a_Lo
        b_Up = sum(W(a, b) * Q * G) * sum(W(a, b) * P * U) - sum(W(a, b) * P * G) * sum(W(a, b) * Q * U)
        b_Lo = sum(W(a, b) * P * U) * sum(W(a, b) * Q * V) - sum(W(a, b) * P * V) * sum(W(a, b) * Q * U)
        new_b = b_Up / b_Lo

        # Standard errors
        mU = sum(W(a, b) * U) / sum(W(a, b))
        mV = sum(W(a, b) * V) / sum(W(a, b))
        mP = sum(W(a, b) * P) / sum(W(a, b))
        mQ = sum(W(a, b) * Q) / sum(W(a, b))

        D_PU = W(a, b) * (a * b * r1 * sx * sy + b ** 2 * sy ** 2 - a * r2 * sx * sz - 2 * b * r3 * sy * sz + sz ** 2)
        D_QU = -1 * a * W(a, b) * (b * sy ** 2 + a * r1 * sx * sy - r3 * sy * sz)
        D_PV = -1 * b * W(a, b) * (a * sx ** 2 + b * r1 * sx * sy - r2 * sx * sz)
        D_QV = W(a, b) * (a * b * r1 * sx * sy + a ** 2 * sx ** 2 - b * r3 * sy * sz - 2 * a * r2 * sx * sz + sz ** 2)
        D_PG = W(a, b) * (a * sx ** 2 + b * r1 * sx * sy - r2 * sx * sz)
        D_QG = W(a, b) * (b * sy ** 2 + a * r1 * sx * sy - r3 * sy * sz)
        D_UX = D_VY = D_GZ = 1 - W(a, b) / sum(W(a, b))
        D_Wa = -1 * W(a, b) ** 2 * (2 * a * sx ** 2 + 2 * b * r1 * sx * sy - 2 * r2 * sx * sz)
        D_Wb = -1 * W(a, b) ** 2 * (2 * b * sy ** 2 + 2 * a * r1 * sx * sy - 2 * r3 * sy * sz)

        D_aX = W(a, b) * D_UX * (a * (sum(W(a, b) * P * U) * V * D_QU + sum(W(a, b) * Q * V) * (
                U * D_PU + P) - sum(W(a, b) * Q * U) * V * D_PU - sum(W(a, b) * P * V) * (U * D_QU + Q)) -
                                 (sum(W(a, b) * P * G) * V * D_QU + sum(W(a, b) * Q * V) * G * D_PU) +
                                 (sum(W(a, b) * Q * G) * V * D_PU + sum(W(a, b) * P * V) * G * D_QU))

        D_aY = W(a, b) * D_VY * (a * (sum(W(a, b) * P * U) * (Q + V * D_QV) + sum(W(a, b) * Q * V) * (
                U * D_PV) - sum(W(a, b) * Q * U) * (P + V * D_PV) - sum(W(a, b) * P * V) * (U * D_QV)) -
                                 (sum(W(a, b) * P * G) * (Q + V * D_QV) + sum(W(a, b) * Q * V) * G * D_PV) +
                                 (sum(W(a, b) * Q * G) * (P + V * D_PV) + sum(W(a, b) * P * V) * G * D_QV))


        D_aZ = W(a, b) * D_GZ * (a * (sum(W(a, b) * P * U) * (V * D_QG) + sum(W(a, b) * Q * V) * (
                U * D_PG) - sum(W(a, b) * Q * U) * (V * D_PG) - sum(W(a, b) * P * V) * (U * D_QG)) -
                                 (sum(W(a, b) * P * G) * (V * D_QG) + sum(W(a, b) * Q * V) * (P + G * D_PG)) +
                                 (sum(W(a, b) * Q * G) * (V * D_PG) + sum(W(a, b) * P * V) * (Q + G * D_QG)))

        D_WPU_a = D_Wa * P * U
        D_WQV_a = D_Wa * Q * V
        D_WQU_a = D_Wa * Q * U
        D_WPV_a = D_Wa * P * V
        D_WPG_a = D_Wa * P * G
        D_WQG_a = D_Wa * Q * G

        D_aa = a_Lo + \
               a * (sum(D_WPU_a) * sum(W(a, b) * Q * V) + sum(D_WQV_a) * sum(W(a, b) * P * U) -
                    sum(D_WQU_a) * sum(W(a, b) * P * V) - sum(D_WPV_a) * sum(W(a, b) * Q * U)
        ) - (sum(D_WPG_a) * sum(W(a, b) * Q * V) + sum(D_WQV_a) * sum(W(a, b) * P * G) -
             sum(D_WQG_a) * sum(W(a, b) * P * V) - sum(D_WPV_a) * sum(W(a, b) * Q * G))

        D_bX = W(a, b) * D_UX * (b * (sum(W(a, b) * P * U) * (V * D_QU) + sum(W(a, b) * Q * V) * (P + U * D_PU) -
                                      sum(W(a, b) * Q * U) * (V * D_PU) - sum(W(a, b) * P * V) * (Q + U * D_QU)) -
                                 (sum(W(a, b) * Q * G) * (P + U * D_PU) + sum(W(a, b) * P * U) * G * D_QU) +
                                 (sum(W(a, b) * P * G) * (Q + U * D_QU) + sum(W(a, b) * Q * U) * G * D_PU))

        D_bY = W(a, b) * D_VY * (b * (sum(W(a, b) * P * U) * (Q + V * D_QV) + sum(W(a, b) * Q * V) * (U * D_PV) -
                                      sum(W(a, b) * Q * U) * (P + V * D_PV) - sum(W(a, b) * P * V) * (U * D_QV)) -
                                 (sum(W(a, b) * Q * G) * (U * D_PV) + sum(W(a, b) * P * U) * (G * D_QV)) +
                                 (sum(W(a, b) * P * G) * (U * D_QV) + sum(W(a, b) * Q * U) * (G * D_PV)))

        D_bZ = W(a, b) * D_GZ * (b * (sum(W(a, b) * P * U) * (V * D_QG) + sum(W(a, b) * Q * V) * (U * D_PG) -
                                      sum(W(a, b) * Q * U) * (V * D_PG) - sum(W(a, b) * P * V) * (U * D_QG)) -
                                 (sum(W(a, b) * Q * G) * (U * D_PG) + sum(W(a, b) * P * U) * (Q + G * D_QG)) +
                                 (sum(W(a, b) * P * G) * (U * D_QG) + sum(W(a, b) * Q * U) * (P + G * D_PG)))

        D_WPU_b = D_Wb * P * U
        D_WQV_b = D_Wb * Q * V
        D_WQU_b = D_Wb * Q * U
        D_WPV_b = D_Wb * P * V
        D_WPG_b = D_Wb * P * G
        D_WQG_b = D_Wb * Q * G

        D_bb = b_Lo + b * (
                sum(D_WPU_b) * sum(W(a, b) * Q * V) + sum(D_WQV_b) * sum(W(a, b) * P * U) -
                sum(D_WQU_b) * sum(W(a, b) * P * V) - sum(D_WPV_b) * sum(W(a, b) * Q * U)
        ) - (
                sum(D_WQG_b) * sum(W(a, b) * P * U) + sum(D_WPU_b) * sum(W(a, b) * Q * G) -
                sum(D_WPG_b) * sum(W(a, b) * Q * U) - sum(D_WQU_b) * sum(W(a, b) * P * G)
               )

        Va = sum(D_aX ** 2 * sx ** 2 + D_aY ** 2 * sy ** 2 + D_aZ ** 2 * sz ** 2 +
                 2 * r1 * sx * sy * D_aX * D_aY + 2 * r2 * sx * sz * D_aX * D_aZ + 2 * r3 * sy * sz * D_aY * D_aZ)
        Vb = sum(D_bX ** 2 * sx ** 2 + D_bY ** 2 * sy ** 2 + D_bZ ** 2 * sz ** 2 +
                 2 * r1 * sx * sy * D_bX * D_bY + 2 * r2 * sx * sz * D_bX * D_bZ + 2 * r3 * sy * sz * D_bY * D_bZ)

        D_cX = - 1 * a * W(a, b) / sum(W(a, b)) + (-1 * D_aX) * (2 * mP - 2 * mU + mX(a, b)) + (-1 * D_bX) * (
                                2 * mQ - 2 * mV + mY(a, b))
        D_cY = - 1 * b * W(a, b) / sum(W(a, b)) + (-1 * D_aY) * (2 * mP - 2 * mU + mX(a, b)) + (-1 * D_bY) * (
                                2 * mQ - 2 * mV + mY(a, b))
        D_cZ = W(a, b) / sum(W(a, b)) + (-1 * D_aZ) * (2 * mP - 2 * mU) + (-1 * D_bZ) * (2 * mQ - 2 * mV)
        Vc = sum(D_cX ** 2 * sx ** 2 + D_cY ** 2 * sy ** 2 + D_cZ ** 2 * sz ** 2 +
                 2 * r1 * sx * sy * D_cX * D_cY + 2 * r2 * sx * sz * D_cX * D_cZ + 2 * r3 * sy * sz * D_cY * D_cZ)

        sa = (Va / D_aa) ** .5
        sb = (Vb / D_bb) ** .5
        sc = Vc ** .5

        mswd = S(a, b, c) / (n - 3)
        if mswd > 1:
            k = mswd ** .5  # k为误差放大系数
        else:
            k = 1

        sa, sb, sc = sa * k, sb * k, sc * k

        a = new_a
        b = new_b
        c = new_c(new_a, new_b)

        # ar40ar36 = (a + b * ar38ar36) * -1 / c
        # f = 1 / c
        # print(f"new_a = {a}, new_b = {b}, new_c = {c}, S = {S(a, b, c)}, MSWD = {mswd}, Ar38/Ar36 = {ar38ar36}, Ar40/Ar36 = {ar40ar36}")
        #
        # print(f"Iteration info: a = {a:.4f} ± {sa:.4f} | {sa/a * 100:.2f}%, b = {b:.4f} ± {sb:.4f} | {sb/b * 100:.2f}%, c = {c:.4f} ± {sc:.4f} | {sc/c * 100:.2f}% "
        #       f"S = {S(a, b, c)}， Di = {Di}, MSWD = {mswd}")

        Di = Di + 1
        if Di >= iteration:
            break

    estimate_z = c + a * x + b * y
    resid = (estimate_z - z) ** 2
    reg = (estimate_z - np.mean(estimate_z)) ** 2
    ssresid = sum(resid)  # residual sum of squares / sum squared residual
    ssreg = sum(reg)  # regression sum of square
    sstotal = ssreg + ssresid  # total sum of squares
    R = ssreg / sstotal if sstotal != 0 else np.inf  # r2 = ssreg / sstotal
    chi_square = mswd * (n - 3)
    p_value = distributions.chi2.sf(chi_square, n - 3)

    # relative error of S
    err_s = lambda a, b, c: (1 / W(a, b)) ** .5 / abs(a * x + b * y + c - z)
    avg_err_s = np.mean(err_s(a, b, c)) * 100
    # print(f"Average relative error of S = {avg_err_s}%")

    # print(f"a = {a}, b = {b}, c = {c}, S = {S(a, b, c)}， Di = {Di}, MSWD = {mswd}, r2 = {R}")

    return c, sc, a, sa, b, sb, S(a, b, c), mswd, R, abs(a - last_a), \
           Di, k, chi_square, p_value, avg_err_s


def wtd_3D_regression_df(data: pd.DataFrame, f: int = 1, convergence: float = 0.001,
                         iteration: int = 100) -> pd.DataFrame:
    """
    :param data: isochron data
    :param f: factor of error, should be 1 for 1 sigma, or 2 for 2 sigma, default = 1
    :param convergence: convergence toleration in percentage, default = 0.001, means 0.001%
    :param iteration number of iteration, default = 100
    :return: data frame with keys [
        'k', 'sk', 'm1', 'sm1',
        'iter', 'conv', 'rs', 'MSWD', 'R2', 'Chisq', 'Pvalue',  # 'rs' means relative error of the total sum
        'mag', 'abs_conv',  # 'mag' is error magnification factor, 'abs_conv' is absolute convergence at the last time
    ]
    """
    # remove nan, inf from data
    data: pd.DataFrame = data.replace([-np.inf], np.nan).dropna(axis=0)
    data = data.transpose().values.tolist()
    res_list = wtd_3D_regression(*data[:9], f=f, convergence=convergence, iteration=iteration)

    columns = [
        'k', 'sk', 'm1', 'sm1', 'm2', 'sm2',
        'S', 'MSWD', 'R2', 'abs_conv', 'iter', 'mag',
        'Chisq', 'Pvalue', 'rs',  # 'rs' means relative error of the total sum

    ]
    res = pd.DataFrame([list(res_list)], columns=columns)
    return res


def max_likelihood(x: list, sx: list, y: list, sy: list, ri: list):
    """
    Parameters
    ----------
    x
    sx
    y
    sy
    ri

    Returns
    -------

    """

    # 定义线性模型
    def linear_model(params, _x):
        return params[0] * _x + params[1]

    # 定义负对数似然函数
    def negative_log_likelihood(params, _x, _y):
        predicted_y = linear_model(params, _x)
        # 使用高斯误差进行似然计算
        errors = predicted_y - _y
        likelihood = np.sum(-0.5 * np.log(2 * np.pi) - 0.5 * errors ** 2)
        return -likelihood

    initial = linest(y, x)[5]
    res = minimize(negative_log_likelihood, initial, args=(np.array(x), np.array(y)))
    slope, intercept = res.x
    return intercept, 0, slope, 0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan


def olst(x: list, sx: list, y: list, sy: list, ri: list):
    """
    Parameters
    ----------
    x
    sx
    y
    sy
    ri

    Returns
    -------

    """

    res = linest(y, x)
    # b, sb, m, sm, mswd, m - last m, Di, k, r2,
    return *res[:2], res[5][1], res[6][1], np.nan, np.nan, np.nan, np.nan, res[3], np.nan, np.nan, np.nan


""" regression functions for raw data """


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


def average(a0: list, a1=None):
    """
    :param a0: known_y's
    :param a1:
    :return: intercept | standard error | relative error | r2 | MSWD | other params | errors of other params |
             euqation | m_ssresid
    """
    if a1 is None:
        a1 = []
    k0 = sum(a0) / len(a0)

    # calculate Y values base on the fitted formula
    estimate_y = [k0 for x in a0]
    resid = [(x - k0) ** 2 for x in a0]
    reg = [(i - sum(estimate_y) / len(estimate_y)) ** 2 for i in estimate_y]
    ssresid = sum(resid)  # residual sum of squares / sum squared residual
    ssreg = sum(reg)  # regression sum of square
    sstotal = ssreg + ssresid  # total sum of squares
    df = len(a0) - 1  # df = degree of freedom
    m_ssresid = ssresid / df
    r2 = ssreg / sstotal if sstotal != 0 else 1  # r2 = ssreg / sstotal

    k1 = pow(sum([(i - k0) ** 2 for i in a0]) / df, 0.5)  # standard deviation
    k2 = k1 / k0 * 100 if k0 != 0 else 0  # relative standard error
    k3 = r2  # determination coefficient
    k4 = 'MSWD'
    k5 = [k0]
    k6 = [k1]
    k8 = m_ssresid

    def get_adjusted_y(x: list):
        return [k0] * len(x)

    k7 = get_adjusted_y

    return k0, k1, k2, k3, k4, k5, k6, k7, k8


#
# def wtd_linest(a0: list, a1: list):
#     """
#     y = m * x + b,
#     :param a0: known_y's
#     :param a1: known_x's
#     :return: intercept | standard error | relative error | R2 | [m] | [sem]
#     """
#     linest_res = linest(a0, a1)
#     b0, seb0, rseb0, r2, mswd, [m0], [rem0] = linest_res[0:7]
#     y0 = list(map(lambda i: m0 * i + b0, a1))
#     resid = list(map(lambda i, j: i - j, y0, a0))
#     weight = list(map(lambda i: 1 / i ** 2, resid))  # Use weighting by inverse of the squares of residual
#
#     sum_wi = sum(weight)
#     sum_wiyi = sum(list(map(lambda i, j: i * j, weight, a0)))
#     sum_wixi = sum(list(map(lambda i, j: i * j, weight, a1)))
#     sum_wiyixi = sum(list(map(lambda i, j, g: i * j * g, weight, a0, a1)))
#     sum_wixixi = sum(list(map(lambda i, j, g: i * j * g, weight, a1, a1)))
#
#     m = (sum_wiyixi - sum_wixi * sum_wiyi / sum_wi) / (sum_wixixi - sum_wixi * sum_wixi / sum_wi)
#     b = (sum_wiyi - m * sum_wixi) / sum_wi
#     a0 = list(map(lambda i, j: i * j, weight, a0))
#     a1 = list(map(lambda i, j: i * j, weight, a1))
#     linest_res = intercept_linest(a0, a1, weight=weight)
#     b, seb, rseb, r2, mswd, [m], [sem] = linest_res[0:7]
#     return b, seb, rseb, r2, [m], [sem]
#
#
# def intercept_linest(a0: list, a1: list, *args, weight: list = None, interceptIsZero: bool = False):
#     """
#     :param a0: known_y's, y = b + m * x
#     :param a1: known_x's
#     :param args: more known_x's
#     :param weight: necessary when weighted least squares fitting
#     :param interceptIsZero: set b as zero, y = m * x
#     :return: intercept | standard error | relative error | R2 | MSWD | other params: list |
#              error of other params: list | equation | m_ssresid (y估计值的标准误差)
#     """
#     if interceptIsZero:
#         if len(a0) != len(a1) or len(args) > 0:
#             return False
#         try:
#             df = len(a0) - 1
#             m = sum(list(map(lambda x, y: x * y, a1, a0))) / sum(list(map(lambda x: x ** 2, a1)))
#             SSresid = sum(list(map(lambda x, y: y - x * m, a1, a0)))
#             sey = pow(SSresid / df, 0.5)
#             SSreg = sum(list(map(lambda x: (x * m) ** 2, a1)))
#             SStotal = SSreg + SSresid
#             R2 = SStotal / SSreg
#             sem = pow(SSresid / df * 1 / sum(list(map(lambda x: x ** 2, a1))), 0.5)
#             return m, sem, R2
#         except Exception:
#             return False
#     # beta = (xTx)^-1 * xTy >>> xtx * beta = xty
#     # crate matrix of x and y, calculate the transpose of x
#     m = len(a1)  # number of data
#     n = len(args) + 2  # number of unknown x, constant is seen as x^0
#     if m - n < 1 or len(a0) != len(a1):
#         return False
#     if weight is not None:
#         xlst = [weight, a1, *args]
#     else:
#         xlst = [[1] * m, a1, *args]
#     ylst = a0
#     xtx = list()
#     xty = list()
#     for i in range(n):
#         xtx.append([])
#         xty.append([])
#         xty[i] = sum([xlst[i][k] * ylst[k] for k in range(m)])
#         for j in range(n):
#             xtx[i].append([])
#             xtx[i][j] = sum([xlst[i][k] * xlst[j][k] for k in range(m)])
#     # solve the system of linear equations using LU factorization algorithm
#     # LU * beta = xty, U * beta = b, L * b = xty
#     l: List[List[Any]] = list()
#     u: List[List[Any]] = list()
#     b: List[Any] = list()
#     beta: List[Any] = list()
#     for i in range(n):
#         l.append([])
#         u.append([])
#         b.append([])
#         beta.append([])
#         for j in range(n):
#             l[i].append([])
#             u[i].append([])
#             if j > i:
#                 l[i][j] = 0
#             elif i > j:
#                 u[i][j] = 0
#             else:
#                 l[i][j] = 1
#     for i in range(n):
#         if i >= 1:
#             l[i][0] = xtx[i][0] / u[0][0]
#         for j in range(n):
#             if i == 0:
#                 u[i][j] = xtx[i][j]
#             elif i == 1 and j >= 1:
#                 u[i][j] = xtx[i][j] - l[i][0] * u[0][j]
#             elif i < n - 1:
#                 if j in range(1, i):
#                     l[i][j] = (xtx[i][j] - sum([l[i][r] * u[r][j] for r in range(j)])) / u[j][j]
#                 if j in range(i, n):
#                     u[i][j] = xtx[i][j] - sum([l[i][r] * u[r][j] for r in range(i)])
#             elif i == n - 1:
#                 if j in range(1, i):
#                     l[n - 1][j] = (xtx[n - 1][j] - sum([l[n - 1][r] * u[r][j] for r in range(j)])) / u[j][j]
#                 if j == n - 1:
#                     u[i][j] = xtx[i][j] - sum([l[i][r] * u[r][j] for r in range(i)])
#     # calculate matrix b, L * b = y
#     b[0] = xty[0]
#     for i in range(1, n):
#         b[i] = xty[i] - sum([l[i][j] * b[j] for j in range(i)])
#     # calculate matrix beta, b = U * beta
#     beta[n - 1] = b[n - 1] / u[n - 1][n - 1]
#     for i in [n - k for k in range(2, n + 1)]:
#         beta[i] = (b[i] - sum([u[i][j] * beta[j] for j in range(i + 1, n)])) / u[i][i]
#
#     # calculate the inverse of matrix xTx
#     inv_l: List[List[Any]] = list()
#     inv_u: List[List[Any]] = list()
#     for i in range(n):
#         inv_l.append([])
#         inv_u.append([])
#         for j in range(n):
#             inv_l[i].append([])
#             inv_u[i].append([])
#             if i == j:
#                 inv_l[i][j] = 1 / l[i][j]
#                 inv_u[i][j] = 1 / u[i][j]
#             elif i > j:
#                 inv_u[i][j] = 0
#             elif j > i:
#                 inv_l[i][j] = 0
#
#     for j in range(1, n):
#         for i in range(n - 1):
#             if i + j > n - 1:
#                 break
#             else:
#                 inv_u[i][i + j] = -1 * sum([u[i][k] * inv_u[k][i + j] for k in range(i + 1, i + j + 1)]) / u[i][i]
#             if i + j > n - 1:
#                 break
#             else:
#                 inv_l[i + j][i] = -1 * sum([l[i + j][k] * inv_l[k][i] for k in range(i, i + j)]) / l[i + j][i + j]
#
#     # inv_xTx = inv_u * inv_l
#     inv_xtx: List[List[Any]] = list()
#     for i in range(n):
#         inv_xtx.append([])
#         for j in range(n):
#             inv_xtx[i].append([])
#             inv_xtx[i][j] = sum([inv_u[i][k] * inv_l[k][j] for k in range(n)])
#     # pow(inv_xtx[0][0], 0.5) is the errF in Excel Linest function
#
#     # calculate Y values base on the fitted formula
#     estimate_y = [sum([xlst[j][i] * beta[j] for j in range(n)]) for i in range(m)]
#     resid = [(estimate_y[i] - a0[i]) ** 2 for i in range(m)]
#     reg = [(i - sum(estimate_y) / len(estimate_y)) ** 2 for i in estimate_y]
#     ssresid = sum(resid)  # residual sum of squares / sum squared residual
#     ssreg = sum(reg)  # regression sum of square
#     sstotal = ssreg + ssresid  # total sum of squares
#     df = m - n + 1 - 1  # df = degree of freedom
#     m_ssresid = ssresid / df
#     se_beta = [pow(m_ssresid * inv_xtx[i][i], 0.5) for i in range(n)]
#     rseb = (se_beta[0] / beta[0]) * 100 if beta[0] != 0 else se_beta[0]  # relative error of intercept
#     r2 = ssreg / sstotal if sstotal != 0 else 1  # r2 = ssreg / sstotal
#
#     def get_adjusted_y(*args):
#         args = [[1] * len(args[0]), *args]
#         return [sum([beta[i] * args[i][j] for i in range(len(beta))]) for j in range(len(args[0]))]
#
#     return beta[0], se_beta[0], rseb, r2, 'mswd', beta[1:], se_beta[1:], get_adjusted_y, m_ssresid


def quadratic(a0: list, a1: list):
    """ y = b + m1 * x + m2 * x ^ 2
    :param a0: known_y's, y = b + m1 * x + m2 * x ^ 2
    :param a1: known_x's
    :return: intercept | standard error | relative error | r2 | MSWD | [m1, m2] | [sem1, sem2], equation
    """
    # y = b + m1 * x + m2 * x ^ 2
    k = list(linest(a0, a1, [i ** 2 for i in a1]))
    b, seb, rseb, r2, mswd, [b, m1, m2], [seb, sem1, sem2] = k[0:7]

    def get_adjusted_y(x: list):
        return [b + m1 * _x + m2 * _x ** 2 for _x in x]

    k[7] = get_adjusted_y

    return k


def polynomial(a0: list, a1: list, degree: int = 5):
    """ y = b + m1 * x + m2 * x ^ 2 + ... + m[n] * x ^ n
    :param a0: known_y's, y = b + m1 * x + m2 * x ^ 2
    :param a1: known_x's
    :param degree: the order of the fitting, default = 5
    :return: intercept | standard error | relative error | r2 | MSWD | [m1, m2] | [sem1, sem2], equation
    """
    # y = b + m1 * x + m2 * x ^ 2 + ... + m[n] * x ^ n
    k = list(linest(a0, *[[j ** (i + 1) for j in a1] for i in range(degree)]))
    b, seb, rseb, r2, mswd, beta, se_beta = k[0:7]

    def get_adjusted_y(x: list):
        return [sum([beta[i] * _x ** i for i in range(degree + 1)]) for _x in x]

    k[7] = get_adjusted_y

    return k


def logest(a0: list, a1: list):
    """
    :param a0: known_y's, y = b * m ^ x
    :param a1: known_x's
    :return: intercept | standard error | relative error | R2 | MSWD | m | sem
    """
    # y = b * m ^ x, Microsoft Excel LOGEST function, ln(y) = ln(b) + ln(m) * x
    a0 = [np.log(i) for i in a0]  # ln(y)
    linest_res = linest(a0, a1)
    b, seb, rseb, r2, mswd, [b, lnm], [seb, selnm] = linest_res[0:7]
    b = np.exp(b)
    m = np.exp(lnm)
    sem = np.exp(lnm) * selnm
    seb = b * seb  # Excel.Logest function do not consider the error propagation
    rseb = seb / b * 100
    return b, seb, rseb, r2, mswd, m, sem


def power(a0: list, a1: list):
    """
    :param a0: known_y's, y = a * x ^ b + c
    :param a1: known_x's
    :return: intercept | standard error of intercept | relative error | R2 | MSWD | [a, b, c] | [sem, sec, seb]
    """

    def _pow_func(x, a, b, c):
        return a * x ** b + c

    def _solve_pow(params):
        a, b, c = params
        x, y = [0, 0, 0], [0, 0, 0]
        x[0] = sum(a1[:3]) / 3
        y[0] = sum(a0[:3]) / 3
        x[1] = sum(a1) / len(a1)
        y[1] = sum(a0) / len(a0)
        x[2] = sum(a1[-3:]) / 3
        y[2] = sum(a0[-3:]) / 3
        return np.array([
            _pow_func(x[0], a, b, c) - y[0],
            _pow_func(x[1], a, b, c) - y[1],
            _pow_func(x[2], a, b, c) - y[2],
        ])

    def _get_sum(a, b, c):
        y_predicted = [_pow_func(_x, a, b, c) for _x in a1]
        return sum([(y_predicted[i] - a0[i]) ** 2 for i in range(len(a0))])

    def _get_abc(b):  # Return a, b, c given b based on linest regression
        f = linest(a0, [_x ** b for _x in a1])
        return f[5][1], b, f[0]

    try:
        a, b, c = fsolve(func=_solve_pow, x0=np.array([1, 1, 1]))  # initial estimate
        count = 0
        step = 0.01
        while count < 100:
            a, b, c = _get_abc(b)
            s = _get_sum(a, b, c)
            b_left, b_right = b - step * b, b + step * b
            s_left = _get_sum(*_get_abc(b_left))
            s_right = _get_sum(*_get_abc(b_right))
            if s_left > s > s_right:
                b = b_right
                continue
            elif s_left < s < s_right:
                b = b_left
                continue
            elif s_left < s_right:
                b = (b + b_left) / 2
            else:
                b = (b + b_right) / 2
            step = step * 0.5
            count += 1
            if step < 0.000001:
                break
    except RuntimeError:
        raise RuntimeError
    except np.linalg.LinAlgError:
        raise np.linalg.LinAlgError
    except TypeError or IndexError:
        raise IndexError

    f = linest(a0, [_x ** b for _x in a1])
    a, sea, c, sec = f[5][1], f[6][1], f[0], f[1]

    calculated_y = [_pow_func(i, a, b, c) for i in a1]
    resid = [(calculated_y[i] - a0[i]) ** 2 for i in range(len(a0))]
    reg = [(i - sum(calculated_y) / len(calculated_y)) ** 2 for i in calculated_y]
    ssresid = sum(resid)
    ssreg = sum(reg)
    sstotal = ssreg + ssresid
    df = len(a0) - 1
    m_ssresid = ssresid / df
    r2 = ssreg / sstotal if sstotal != 0 else 1

    intercept = c
    se_intercept_1 = sec
    dp = len(a1)  # data points
    z = [i ** b for i in a1]
    # calculate error of intercept
    errfz = pow(sum([i ** 2 for i in z]) / (dp * sum([i ** 2 for i in z]) - sum(z) ** 2), 0.5)
    errfx = pow(sum([i ** 2 for i in a1]) / (dp * sum([i ** 2 for i in a1]) - sum(a1) ** 2), 0.5)
    # seb = errfz * sey = errfz * ssresid / df -> se_intercept = sey * errfx = seb / errfz * errfx
    se_intercept = sec / errfz * errfx
    rse_intercept = se_intercept / intercept * 100

    return intercept, se_intercept, rse_intercept, r2, 'mswd', [a, b, c], 'se', \
           lambda x: [_pow_func(i, a, b, c) for i in x], m_ssresid


def exponential(a0: list, a1: list):
    """
    :param a0: known_y's, y = a * b ^ x + c
    :param a1: known_x's
    :return: intercept | standard error of intercept | relative error | R2 | MSWD | [m, c, b] | [sem, sec, seb]
    """

    def _exp_func(x, a, b, c):
        return a * b ** x + c

    def _solve_exp(params):
        a, b, c = params
        x, y = [0, 0, 0], [0, 0, 0]
        x[0] = sum(a1[:3]) / 3
        y[0] = sum(a0[:3]) / 3
        x[1] = sum(a1) / len(a1)
        y[1] = sum(a0) / len(a0)
        x[2] = sum(a1[-3:]) / 3
        y[2] = sum(a0[-3:]) / 3
        return np.array([
            _exp_func(x[0], a, b, c) - y[0],
            _exp_func(x[1], a, b, c) - y[1],
            _exp_func(x[2], a, b, c) - y[2],
        ])

    def _get_sum(a, b, c):
        y_predicted = [_exp_func(_x, a, b, c) for _x in a1]
        return sum([(y_predicted[i] - a0[i]) ** 2 for i in range(len(a0))])

    def _get_ac(b):
        f = linest(a0, [b ** _x for _x in a1])
        return f[5][1], b, f[0]

    try:
        a, b, c = fsolve(_solve_exp, np.array([1, 1, 1]))
        count = 0
        step = 0.01
        while count < 100:
            a, b, c = _get_ac(b)
            s = _get_sum(a, b, c)
            b_left, b_right = b - step * b, b + step * b
            s_left = _get_sum(*_get_ac(b_left))
            s_right = _get_sum(*_get_ac(b_right))
            if s_left > s > s_right:
                b = b_right
                continue
            elif s_left < s < s_right:
                b = b_left
                continue
            elif s_left < s_right:
                b = (b + b_left) / 2
            else:
                b = (b + b_right) / 2
            count += 1
            step = step * 0.5
            if step < 0.000001:
                break

    except RuntimeError:
        raise RuntimeError
    except np.linalg.LinAlgError:
        raise np.linalg.LinAlgError
    except TypeError or IndexError:
        raise IndexError

    f = linest(a0, [b ** _x for _x in a1])
    a, sea, c, sec = f[5][1], f[6][1], f[0], f[1]

    calculated_y = [_exp_func(i, a, b, c) for i in a1]
    resid = [(calculated_y[i] - a0[i]) ** 2 for i in range(len(a0))]
    reg = [(i - sum(calculated_y) / len(calculated_y)) ** 2 for i in calculated_y]
    ssresid = sum(resid)
    ssreg = sum(reg)
    sstotal = ssreg + ssresid
    dp = len(a1)
    df = dp - 1
    m_ssresid = ssresid / df
    r2 = ssreg / sstotal if sstotal != 0 else 1

    z = [b ** i for i in a1]
    intercept = a + c
    se_intercept_1 = np.sqrt(sea ** 2 + sec ** 2)
    # calculate error of intercept
    errfz = pow(sum([i ** 2 for i in z]) / (dp * sum([i ** 2 for i in z]) - sum(z) ** 2), 0.5)
    errfx = pow(sum([i ** 2 for i in a1]) / (dp * sum([i ** 2 for i in a1]) - sum(a1) ** 2), 0.5)
    # seb = errfz * sey = errfz * ssresid / df -> se_intercept = sey * errfx = seb / errfz * errfx
    se_intercept = sec / errfz * errfx
    rse_intercept = se_intercept / intercept * 100

    if abs(intercept) > 10 * max(a0):
        raise ValueError
    if intercept < 0:
        raise ValueError

    return intercept, se_intercept, rse_intercept, r2, 'mswd', [a, b, c], 'se', \
           lambda x: [_exp_func(i, a, b, c) for i in x], m_ssresid


""" line functions """


def linear_eq(x: list, beta: list):
    """ y = b0 * x^0 + b1 * x^1 + ... + bn * x^n
    Parameters
    ----------
    beta : coefficients
    x :

    Returns
    -------

    """
    return [np.prod([beta, [_x ** i for i in range(len(beta))]], axis=0).sum() for _x in x]


def exponential_eq(x: list, beta: list):
    """ y = a * b ^ x + c
    Parameters
    ----------
    beta : coefficients, [a, b, c]
    x :

    Returns
    -------

    """
    return [beta[0] * beta[1] ** _x + beta[0] for _x in x]


def power_eq(x: list, beta: list):
    """ y = y = a * x ^ b + c
    Parameters
    ----------
    beta : coefficients, [a, b, c]
    x :

    Returns
    -------

    """
    return [beta[0] * _x ** beta[1] + beta[0] for _x in x]


if __name__ == '__main__':
    pass

