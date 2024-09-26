#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - smp - corr
# ==========================================
#
#
#
"""

import traceback
import numpy as np
import copy
import re

from .. import calc
from .sample import Sample


# =======================
# Corr Blank
# =======================
def corr_blank(sample: Sample):
    """Blank Correction"""
    corrBlank = sample.TotalParam[102][0]
    # if not corrBlank:
    #     sample.BlankCorrected = copy.deepcopy(sample.SampleIntercept)
    #     sample.CorrectedValues = copy.deepcopy(sample.BlankCorrected)
    #     return
    blank_corrected = [[]] * 10
    try:
        for i in range(5):
            blank_corrected[i * 2:2 + i * 2] = calc.corr.blank(
                *sample.SampleIntercept[i * 2:2 + i * 2], *sample.BlankIntercept[i * 2:2 + i * 2])
    except Exception as e:
        print(traceback.format_exc())
        raise ValueError('Blank correction error')
    for i in range(0, 10, 2):
        blank_corrected[i] = [blank_corrected[i][index] if sample.TotalParam[102][index] else j for index, j in enumerate(sample.SampleIntercept[i])]
        blank_corrected[i + 1] = [blank_corrected[i + 1][index] if sample.TotalParam[102][index] else j for index, j in enumerate(sample.SampleIntercept[i + 1])]
        blank_corrected[i] = [0 if j < 0 and sample.TotalParam[101][index] else j for index, j in enumerate(blank_corrected[i])]
    sample.BlankCorrected = blank_corrected
    sample.CorrectedValues = copy.deepcopy(sample.BlankCorrected)


# =======================
# Mass Discrimination
# =======================
def corr_massdiscr(sample: Sample):
    """Mass Discrimination Correction"""
    corrMassdiscr = sample.TotalParam[103][0]
    if not corrMassdiscr:
        sample.MassDiscrCorrected = copy.deepcopy(sample.BlankCorrected)
        sample.CorrectedValues = copy.deepcopy(sample.MassDiscrCorrected)
        return
    MASS = sample.TotalParam[71:81]
    mdf_corrected = [[]] * 10
    try:
        for i in range(5):
            if len(sample.BlankCorrected[i * 2:2 + i * 2]) == 0:
                raise ValueError("sample.BlankCorrected is empty.")
            mdf_corrected[i * 2:2 + i * 2] = calc.corr.discr(
                *sample.BlankCorrected[i * 2:2 + i * 2],
                *sample.TotalParam[69:71], m=MASS[i * 2], m40=MASS[8], isRelative=True,
                method=sample.TotalParam[100][0])
    except Exception as e:
        print(traceback.format_exc())
        raise ValueError(f'Mass discrimination correction error: {e}')
    sample.MassDiscrCorrected = mdf_corrected
    sample.CorrectedValues = copy.deepcopy(sample.MassDiscrCorrected)


# =======================
# Decay correction
# =======================
def corr_decay(sample: Sample):
    """ Ar37 and Ar39 Decay Correction
    Parameters
    ----------
    sample

    Returns
    -------

    """
    decay_corrected = [[]] * 10
    try:
        irradiation_cycles = [list(filter(None, re.split(r'[DS]', each_step))) for each_step in sample.TotalParam[27]]
        t1 = [re.findall(r"\d+", i) for i in sample.TotalParam[31]]  # t1: experimental times
        t2, t3 = [], []  # t2: irradiation times, t3: irradiation durations
        for each_step in irradiation_cycles:
            t2.append([re.findall(r"\d+", item) for i, item in enumerate(each_step) if i % 2 == 0])
            t3.append([item for i, item in enumerate(each_step) if i % 2 == 1])
        decay_corrected[2:4] = calc.corr.decay(
            *sample.MassDiscrCorrected[2:4], t1, t2, t3, *sample.TotalParam[44:46], isRelative=True)
        decay_corrected[6:8] = calc.corr.decay(
            *sample.MassDiscrCorrected[6:8], t1, t2, t3, *sample.TotalParam[42:44], isRelative=True)
        # Negative number set to zero in decay correction
        decay_corrected[2] = [0 if i < 0 else i for i in decay_corrected[2]]
        decay_corrected[6] = [0 if i < 0 else i for i in decay_corrected[6]]
    except Exception as e:
        print(traceback.format_exc())
        raise ValueError('Decay correction correction error')

    corrDecay37 = sample.TotalParam[104]
    corrDecay39 = sample.TotalParam[105]
    sample.CorrectedValues[2] = [val if corrDecay37[idx] else 0 for idx, val in enumerate(decay_corrected[2])]
    sample.CorrectedValues[3] = [val if corrDecay37[idx] else 0 for idx, val in enumerate(decay_corrected[3])]
    sample.CorrectedValues[6] = [val if corrDecay39[idx] else 0 for idx, val in enumerate(decay_corrected[6])]
    sample.CorrectedValues[7] = [val if corrDecay39[idx] else 0 for idx, val in enumerate(decay_corrected[7])]


# =======================
# Degas Calcium derived 37Ar 36Ar 38Ar 39Ar
# =======================
def calc_degas_ca(sample: Sample):
    """ Degas Pattern for Ca
    Parameters
    ----------
    sample

    Returns
    -------

    """
    corrDecasCa = sample.TotalParam[106]
    # n = len(sample.CorrectedValues[2])
    ar37ca = sample.CorrectedValues[2:4]
    ar39ca = calc.arr.mul_factor(ar37ca, sample.TotalParam[8:10], isRelative=True)
    ar38ca = calc.arr.mul_factor(ar37ca, sample.TotalParam[10:12], isRelative=True)
    ar36ca = calc.arr.mul_factor(ar37ca, sample.TotalParam[12:14], isRelative=True)
    sample.DegasValues[8:10] = copy.deepcopy(ar37ca)
    # sample.DegasValues[22:24] = ar39ca if corrDecasCa else [[0] * n, [0] * n]
    # sample.DegasValues[18:20] = ar38ca if corrDecasCa else [[0] * n, [0] * n]
    # sample.DegasValues[4:6] = ar36ca if corrDecasCa else [[0] * n, [0] * n]
    sample.DegasValues[ 4] = [val if corrDecasCa[idx] else 0 for idx, val in enumerate(ar36ca[0])]
    sample.DegasValues[ 5] = [val if corrDecasCa[idx] else 0 for idx, val in enumerate(ar36ca[1])]
    sample.DegasValues[18] = [val if corrDecasCa[idx] else 0 for idx, val in enumerate(ar38ca[0])]
    sample.DegasValues[19] = [val if corrDecasCa[idx] else 0 for idx, val in enumerate(ar38ca[1])]
    sample.DegasValues[22] = [val if corrDecasCa[idx] else 0 for idx, val in enumerate(ar39ca[0])]
    sample.DegasValues[23] = [val if corrDecasCa[idx] else 0 for idx, val in enumerate(ar39ca[1])]
    sample.PublishValues[1] = copy.deepcopy(ar37ca[0])


# =======================
# Degas Potassium derived 39Ar 38Ar 40Ar
# =======================
def calc_degas_k(sample: Sample):
    """ Degas Pattern for K
    Parameters
    ----------
    sample

    Returns
    -------

    """
    corrDecasK = sample.TotalParam[107]
    set_negative_zero = sample.TotalParam[101]
    # n = len(sample.CorrectedValues[6])
    ar39k = calc.arr.sub(sample.CorrectedValues[6:8], sample.DegasValues[22:24])
    ar39k[0] = [0 if val < 0 and set_negative_zero[idx] else val for idx, val in enumerate(ar39k[0])]
    ar40k = calc.arr.mul_factor(ar39k, sample.TotalParam[14:16], isRelative=True)
    ar38k = calc.arr.mul_factor(ar39k, sample.TotalParam[16:18], isRelative=True)

    sample.PublishValues[3] = copy.deepcopy(ar39k[0])
    sample.DegasValues[20:22] = copy.deepcopy(ar39k)
    # sample.DegasValues[30:32] = ar40k if corrDecasK else [[0] * n, [0] * n]
    # sample.DegasValues[16:18] = ar38k if corrDecasK else [[0] * n, [0] * n]
    sample.DegasValues[16] = [val if corrDecasK[idx] else 0 for idx, val in enumerate(ar38k[0])]
    sample.DegasValues[17] = [val if corrDecasK[idx] else 0 for idx, val in enumerate(ar38k[1])]
    sample.DegasValues[30] = [val if corrDecasK[idx] else 0 for idx, val in enumerate(ar40k[0])]
    sample.DegasValues[31] = [val if corrDecasK[idx] else 0 for idx, val in enumerate(ar40k[1])]


# =======================
# Degas Chlorine derived 36Ar 38Ar
# =======================
def calc_degas_cl(sample: Sample):
    """ Degas Pattern for Cl
    Parameters
    ----------
    sample

    Returns
    -------

    """
    corrDecasCl = sample.TotalParam[108]
    decay_const = sample.TotalParam[46:48]
    cl36_cl38_p = sample.TotalParam[56:58]
    ar38ar36 = sample.TotalParam[4:6]
    stand_time_year = sample.TotalParam[32]
    set_negative_zero = sample.TotalParam[101]
    # ============
    decay_const[1] = [decay_const[0][i] * decay_const[1][i] / 100 for i in
                      range(len(decay_const[0]))]  # convert to absolute error
    cl36_cl38_p[1] = [cl36_cl38_p[0][i] * cl36_cl38_p[1][i] / 100 for i in
                      range(len(cl36_cl38_p[0]))]  # convert to absolute error
    # convert to absolute error
    ar38ar36[1] = [ar38ar36[0][i] * ar38ar36[1][i] / 100 for i in range(len(ar38ar36[0]))]
    # ============
    # 36Ar deduct Ca, that is sum of 36Ara and 36ArCl
    ar36acl = calc.arr.sub(sample.CorrectedValues[0:2], sample.DegasValues[4:6])
    # 38Ar deduct K and Ca, that is sum of 38Ara and 38ArCl
    ar38acl = calc.arr.sub(calc.arr.sub(
        sample.CorrectedValues[4:6], sample.DegasValues[16:18]), sample.DegasValues[18:20])
    for index, item in enumerate(ar36acl[0]):
        if set_negative_zero[index]:
            if item < 0:
                ar36acl[0][index] = 0
            if ar38acl[0][index] < 0:
                ar38acl[0][index] = 0
    try:
        if not corrDecasCl:
            raise ValueError("Do not apply degas chlorine")
        v3 = [cl36_cl38_p[0][i] * (1 - np.exp(-1 * decay_const[0][i] * stand_time_year[i])) for i in
              range(len(stand_time_year))]
        s3 = [pow((cl36_cl38_p[1][i] * (1 - np.exp(-1 * decay_const[0][i] * stand_time_year[i]))) ** 2 +
                  (cl36_cl38_p[0][i] * stand_time_year[i] * (np.exp(-1 * decay_const[0][i] * stand_time_year[i])) *
                   decay_const[1][i]) ** 2, 0.5) for i in range(len(stand_time_year))]
        s3 = [calc.err.div((1, 0), (v3[i], s3[i])) for i in range(len(s3))]
        v3 = [1 / v3[i] for i in range(len(v3))]
        # 36ArCl
        ar36cl = [[], []]
        ar36cl[0] = [(ar36acl[0][i] * ar38ar36[0][i] - ar38acl[0][i]) / (ar38ar36[0][i] - v3[i])
                     for i in range(len(ar36acl[0]))]
        s1 = [(ar36acl[1][i] * ar38ar36[0][i] / (ar38ar36[0][i] - v3[i])) ** 2 for i in range(len(ar36cl[0]))]
        s2 = [(ar38acl[1][i] / (ar38ar36[0][i] - v3[i])) ** 2 for i in range(len(ar36cl[0]))]
        s3 = [(s3[i] * (ar36acl[0][i] * ar38ar36[0][i] - ar38acl[0][i]) / (ar38ar36[0][i] - v3[i]) ** 2) ** 2
              for i in range(len(ar36cl[0]))]
        s4 = [(ar36acl[0][i] / (ar38ar36[0][i] - v3[i]) -
               (ar36acl[0][i] * ar38ar36[0][i] - ar38acl[0][i]) / (ar38ar36[0][i] - v3[i]) ** 2) ** 2 *
              (ar38ar36[1][i]) ** 2 for i in range(len(ar36cl[0]))]
        ar36cl[1] = [pow(s1[i] + s2[i] + s3[i] + s4[i], 0.5) for i in range(len(ar36cl[0]))]

        # 38ArCl
        ar38cl = [[], []]
        ar38cl[1] = [calc.err.mul((ar36cl[0][i], ar36cl[1][i]), (v3[i], s3[i])) for i in range(len(ar36cl[0]))]
        ar38cl[0] = [ar36cl[0][i] * v3[i] for i in range(len(ar36cl[0]))]

        # Negative number set to zero
        ar36cl[0] = [0 if i < 0 and set_negative_zero else i for i in ar36cl[0]]
        # force 36ArCl to zero if 36Ar - 36ArCa - 36Cl < 0
        ar36cl[0] = [0 if ar36acl[0][i] - item < 0 and set_negative_zero else item
                     for i, item in enumerate(ar36cl[0])]

    except Exception as e:
        print('Error in corr Cl: {}, lines: {}'.format(e, e.__traceback__.tb_lineno))
        n = len(ar36acl[0])
        ar36cl = [[0] * n, [0] * n]
        ar38cl = [[0] * n, [0] * n]

    # sample.DegasValues[6:8] = ar36cl
    # sample.DegasValues[10:12] = ar38cl
    sample.PublishValues[2] = copy.deepcopy(ar38cl[0])
    sample.DegasValues[ 6] = [val if corrDecasCl[idx] else 0 for idx, val in enumerate(ar36cl[0])]
    sample.DegasValues[ 7] = [val if corrDecasCl[idx] else 0 for idx, val in enumerate(ar36cl[1])]
    sample.DegasValues[10] = [val if corrDecasCl[idx] else 0 for idx, val in enumerate(ar38cl[0])]
    sample.DegasValues[11] = [val if corrDecasCl[idx] else 0 for idx, val in enumerate(ar38cl[1])]


# =======================
# Degas atmospheric 36Ar 38Ar 40Ar
# =======================
def calc_degas_atm(sample: Sample):
    """ Degas for Atmospheric Gas
    Parameters
    ----------
    sample

    Returns
    -------

    """
    corrDecasAtm = sample.TotalParam[109]
    set_negative_zero = sample.TotalParam[101]
    # n = len(sample.CorrectedValues[0])
    # 36Ar deduct Ca, that is sum of 36Ara and 36ArCl
    ar36acl = calc.arr.sub(sample.CorrectedValues[0:2], sample.DegasValues[4:6])
    ar36acl[0] = [0 if val < 0 and set_negative_zero[idx] else val for idx, val in enumerate(ar36acl[0])]
    # 38Ar deduct K and Ca, that is sum of 38Ara and 38ArCl
    # ar38acl = calc.arr.sub()(
    #     calc.arr.sub()(sample.CorrectedValues[2:4], sample.DegasValues[16:18]), sample.DegasValues[18:20])
    # 36ArAir
    ar36a = calc.arr.sub(ar36acl, sample.DegasValues[6:8])
    # If ar36acl - ar36cl < 0, let ar36a = ar36 - ar36ca
    ar36a[0] = [ar36acl[index] if item < 0 and set_negative_zero[index] else item for index, item in enumerate(ar36a[0])]
    if sample.Info.sample.type == "Air":
        ar38a = copy.deepcopy(sample.CorrectedValues[4:6])
        ar40a = copy.deepcopy(sample.CorrectedValues[8:10])
    else:
        # 38ArAir
        ar38a = calc.arr.mul_factor(ar36a, sample.TotalParam[4:6], isRelative=True)
        # 40ArAir
        ar40a = calc.arr.mul_factor(ar36a, sample.TotalParam[0:2], isRelative=True)

    sample.PublishValues[0] = copy.deepcopy(ar36a[0])
    # sample.DegasValues[12:14] = ar38a if corrDecasAtm else [[0] * n, [0] * n]
    # sample.DegasValues[26:28] = ar40a if corrDecasAtm else [[0] * n, [0] * n]
    sample.DegasValues[ 0] = [val if corrDecasAtm[idx] else 0 for idx, val in enumerate(ar36a[0])]
    sample.DegasValues[ 1] = [val if corrDecasAtm[idx] else 0 for idx, val in enumerate(ar36a[1])]
    sample.DegasValues[12] = [val if corrDecasAtm[idx] else 0 for idx, val in enumerate(ar38a[0])]
    sample.DegasValues[13] = [val if corrDecasAtm[idx] else 0 for idx, val in enumerate(ar38a[1])]
    sample.DegasValues[26] = [val if corrDecasAtm[idx] else 0 for idx, val in enumerate(ar40a[0])]
    sample.DegasValues[27] = [val if corrDecasAtm[idx] else 0 for idx, val in enumerate(ar40a[1])]


# =======================
# Degas radiogenic 40Ar
# =======================
def calc_degas_r(sample: Sample):
    """ Degas for Radiogenic Ar40
    Parameters
    ----------
    sample

    Returns
    -------

    """
    ar40ar = calc.arr.sub(sample.CorrectedValues[8:10], sample.DegasValues[30:32])
    ar40r = calc.arr.sub(ar40ar, sample.DegasValues[26:28])
    ar40r[0] = [item if item >= 0 else 0 for item in ar40r[0]]
    sample.DegasValues[24:26] = copy.deepcopy(ar40r)
    sample.PublishValues[4] = copy.deepcopy(ar40r[0])


# =======================
# Calc ratio
# =======================
def calc_ratio(sample: Sample, monte_carlo: bool = False):
    """ Calculate isochron ratio data, 40Arr/39ArK, Ar40r percentage,
        Ar39K released percentage, Ca/K
    Parameters
    ----------
    sample : Sample instance
    monte_carlo : whether conduct monte carlo simulation for calculating 40Arr/39ArK

    Returns
    -------
    None
    """
    ar40r_percent = [item / sample.CorrectedValues[8][index] * 100 if sample.CorrectedValues[8][index] != 0 else 0
                     for index, item in enumerate(sample.DegasValues[24])]
    sum_ar39k = sum(sample.DegasValues[20])
    ar39k_percent = [item / sum_ar39k * 100 if sum_ar39k != 0 else 0 for item in sample.DegasValues[20]]
    sum_ar36a = sum(sample.DegasValues[ 0])
    ar36a_percent = [item / sum_ar36a * 100 if sum_ar36a != 0 else 0 for item in sample.DegasValues[ 0]]
    ar40rar39k = calc.arr.mul_factor(
        sample.DegasValues[24:26], calc.arr.rec_factor(sample.DegasValues[20:22], isRelative=False),
        isRelative=False)
    ar40aar36a = calc.arr.mul_factor(
        sample.DegasValues[26:28], calc.arr.rec_factor(sample.DegasValues[0:2], isRelative=False),
        isRelative=False)
    CaK = calc.arr.mul_factor(calc.arr.mul_factor(
        sample.DegasValues[8:10], calc.arr.rec_factor(sample.DegasValues[20:22], isRelative=False)),
        calc.arr.rec_factor(sample.TotalParam[20:22], isRelative=True))
    isochron_1 = calc.isochron.get_data(*sample.DegasValues[20:22], *calc.arr.sub(
        sample.CorrectedValues[8:10], sample.DegasValues[30:32]), *sample.DegasValues[0:2])
    isochron_2 = calc.isochron.get_data(*sample.DegasValues[20:22], *sample.DegasValues[0:2], *calc.arr.sub(
        sample.CorrectedValues[8:10], sample.DegasValues[30:32]))
    isochron_3 = calc.isochron.get_data(
        *sample.DegasValues[20:22], *sample.DegasValues[24:26], *sample.DegasValues[10:12])
    isochron_4 = calc.isochron.get_data(
        *sample.DegasValues[20:22], *sample.DegasValues[10:12], *sample.DegasValues[24:26])
    isochron_5 = calc.isochron.get_data(
        *sample.DegasValues[10:12], *sample.DegasValues[24:26], *sample.DegasValues[20:22])

    # assignation
    sample.ApparentAgeValues[0:2] = ar40aar36a if sample.Info.sample.type == "Air" else ar40rar39k
    sample.ApparentAgeValues[6] = ar40r_percent
    sample.ApparentAgeValues[7] = ar36a_percent if sample.Info.sample.type == "Air" else ar39k_percent
    sample.PublishValues[7:11] = [ar40r_percent, ar39k_percent, *CaK]
    sample.IsochronValues[0:5] = isochron_1
    sample.IsochronValues[6:11] = isochron_2
    sample.IsochronValues[12:17] = isochron_3
    sample.IsochronValues[18:23] = isochron_4
    sample.IsochronValues[24:29] = isochron_5

    # === Cl-Atm-Correlation Plot ===
    # === Ar values ===
    # 3D ratio, 36Ar(a+cl)/40Ar(a+r), 38Ar(a+cl)/40Ar(a+r), 39Ar(k)/40Ar(a+r),
    ar40ar = calc.arr.sub(sample.CorrectedValues[8:10], sample.DegasValues[30:32])
    # 36Ar deduct Ca, that is sum of 36Ara and 36ArCl (and also 36Arc)
    ar36acl = calc.arr.sub(sample.CorrectedValues[0:2], sample.DegasValues[4:6])
    # 38Ar deduct K and Ca, that is sum of 38Ara and 38ArCl (and also 38Arc)
    ar38acl = calc.arr.sub(calc.arr.sub(sample.CorrectedValues[4:6], sample.DegasValues[16:18]),
                           sample.DegasValues[18:20])
    # 38ArCl
    ar38cl = sample.DegasValues[10:12]
    # 39ArK
    ar39k = sample.DegasValues[20:22]
    # isochron_6 = calc.isochron.get_3d_data(*ar36acl, *ar38acl, *ar40ar, *ar39k)
    isochron_6 = calc.isochron.get_3d_data(*ar36acl, *ar38acl, *ar39k,
                                           *ar40ar)  # Points on the plot will be more disperse than the above
    sample.IsochronValues[30:39] = isochron_6

    # Turner 1988 3D cake mix plots
    # ar40 = sample.CorrectedValues[8:10]  # ar40 = atm + r + k
    # ar36a = sample.DegasValues[0:2]  # ar36a
    # isochron_6 = calc.isochron.get_3d_data(*ar39k, *ar38cl, *ar40, *ar36a)
    # sample.IsochronValues[30:39] = isochron_6

    # Note that the difference between Turner 3D plots and our 3D plots.

    if monte_carlo:
        res = monte_carlo_f(sample=sample)
        # where to display simulation results
        res = calc.arr.transpose(list(res))  # res is a generator for [age, sage, ...]
        age, sage = res[:2]
        sample.ApparentAgeValues[1] = sage

        # isochron data
        isochron_1 = res[2:7]
        isochron_2 = res[7:12]
        sample.IsochronValues[0:5] = isochron_1
        sample.IsochronValues[6:11] = isochron_2


def monte_carlo_f(sample: Sample):
    """
    Parameters
    ----------
    sample

    Returns
    -------

    """

    sequence_num = sample.sequence().size

    ar40m = np.transpose(sample.SampleIntercept[8:10])
    ar39m = np.transpose(sample.SampleIntercept[6:8])
    ar38m = np.transpose(sample.SampleIntercept[4:6])
    ar37m = np.transpose(sample.SampleIntercept[2:4])
    ar36m = np.transpose(sample.SampleIntercept[0:2])
    ar40b = np.transpose(sample.BlankIntercept[8:10])
    ar39b = np.transpose(sample.BlankIntercept[6:8])
    ar38b = np.transpose(sample.BlankIntercept[4:6])
    ar37b = np.transpose(sample.BlankIntercept[2:4])
    ar36b = np.transpose(sample.BlankIntercept[0:2])

    M36 = np.transpose(sample.TotalParam[71:73])
    M37 = np.transpose(sample.TotalParam[73:75])
    M38 = np.transpose(sample.TotalParam[75:77])
    M39 = np.transpose(sample.TotalParam[77:79])
    M40 = np.transpose(sample.TotalParam[79:81])

    # M36 = [[35.96754628, 0] for i in range(sequence_num)]
    # M37 = [[36.9667759, 0] for i in range(sequence_num)]
    # M38 = [[37.9627322, 0] for i in range(sequence_num)]
    # M39 = [[38.964313, 0] for i in range(sequence_num)]
    # M40 = [[39.962383123, 0] for i in range(sequence_num)]

    MDF = np.transpose(sample.TotalParam[69:71])

    L39ar = np.transpose(sample.TotalParam[42:44])
    L37ar = np.transpose(sample.TotalParam[44:46])
    L36cl = np.transpose(sample.TotalParam[46:48])

    R39v37ca = np.transpose(sample.TotalParam[8:10])
    R38v37ca = np.transpose(sample.TotalParam[10:12])
    R36v37ca = np.transpose(sample.TotalParam[12:14])
    R40v39k = np.transpose(sample.TotalParam[14:16])
    R38v39k = np.transpose(sample.TotalParam[16:18])

    R40v36a = np.transpose(sample.TotalParam[0:2])
    R38v36a = np.transpose(sample.TotalParam[4:6])
    R36v38clp = np.transpose(sample.TotalParam[56:58])

    stand_time_year = np.transpose(sample.TotalParam[32])

    irradiation_cycles = [list(filter(None, re.split(r'[DS]', each_step))) for each_step in sample.TotalParam[27]]
    t1 = [re.findall(r"\d+", i) for i in sample.TotalParam[31]]  # t1: experimental times
    t2, t3 = [], []  # t2: irradiation times, t3: irradiation durations
    for each_step in irradiation_cycles:
        t2.append([re.findall(r"\d+", item) for i, item in enumerate(each_step) if i % 2 == 0])
        t3.append([item for i, item in enumerate(each_step) if i % 2 == 1])

    # for i in range(sequence_num):
    #     P37Decay = calc.corr.get_decay_factor(t1[i], t2[i], t3[i], L37ar[i][0], L37ar[i][0] * L37ar[i][1] / 100)
    #     print(P37Decay)
    #
    # for i in range(sequence_num):
    #     P39Decay = calc.corr.get_decay_factor(t1[i], t2[i], t3[i], L39ar[i][0], L39ar[i][0] * L39ar[i][1] / 100)
    #     print(P39Decay)

    for i in range(sequence_num):

        print(f"Monte Carlo Simulation For sequence {i + 1}")

        res = calc.corr.Monte_Carlo_F(
            ar40m=ar40m[i], ar39m=ar39m[i], ar38m=ar38m[i], ar37m=ar37m[i], ar36m=ar36m[i],
            ar40b=ar40b[i], ar39b=ar39b[i], ar38b=ar38b[i], ar37b=ar37b[i], ar36b=ar36b[i],
            M40=M40[i], M39=M39[i], M38=M38[i], M37=M37[i], M36=M36[i],
            t1=t1[i], t2=t2[i], t3=t3[i],
            R40v36a=R40v36a[i], R38v36a=R38v36a[i],
            R39v37ca=R39v37ca[i], R36v37ca=R36v37ca[i], R38v37ca=R38v37ca[i],
            R40v39k=R40v39k[i], R38v39k=R38v39k[i],
            R36v38clp=R36v38clp[i],
            L37ar=L37ar[i], L39ar=L39ar[i], L36cl=L36cl[i],
            MDFunc=None,
            MDF=MDF[i], stand_time_year=stand_time_year[i]
        )

        yield res
