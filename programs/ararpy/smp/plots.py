#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - smp - plots
# ==========================================
#
#
#
"""

import traceback
import numpy as np

from scipy.signal import find_peaks


from .. import calc
from .sample import Sample, Table, Plot
from . import basic, initial

Set = Plot.Set
Label = Plot.Label
Axis = Plot.Axis
Text = Plot.Text


ISOCHRON_INDEX_DICT = {
    'figure_2': {'data_index': [0, 5], 'name': 'Normal Isochron', 'figure_type': 1},
    'figure_3': {'data_index': [6, 11], 'name': 'Inverse Isochron', 'figure_type': 2},
    'figure_4': {'data_index': [12, 17], 'name': 'Cl Correlation 1', 'figure_type': 1},
    'figure_5': {'data_index': [18, 23], 'name': 'Cl Correlation 2', 'figure_type': 2},
    'figure_6': {'data_index': [24, 29], 'name': 'Cl Correlation 3', 'figure_type': 3},
    'figure_7': {'data_index': [30, 39], 'name': 'Cl Correlation 3D', 'figure_type': 0},
}


# =======================
# Reset plot data
# =======================
def set_plot_data(sample: Sample, isInit: bool = True, isIsochron: bool = True,
                  isPlateau: bool = True, **kwargs):
    """
    Parameters
    ----------
    sample
    isInit
    isIsochron
    isPlateau
    kwargs

    Returns
    -------

    """
    # print(f"isInit: {isInit}, isIsochron: {isIsochron}, isPlateau: {isPlateau}")

    # Initialization, apply age spectra data and isochron plot data
    if isInit:
        try:
            initial_plot_data(sample)
        except (Exception, BaseException):
            print(traceback.format_exc())
            pass

    # Recalculate isochron lines
    if isIsochron:
        try:
            recalc_isochrons(sample, **kwargs)
            reset_isochron_line_data(sample)
        except (Exception, BaseException):
            print(traceback.format_exc())
            pass

    # Recalculate plateaus
    if isPlateau:
        try:
            recalc_plateaus(sample)
        except (Exception, BaseException):
            print(traceback.format_exc())
            pass


# =======================
# Initialize plot data
# =======================
def initial_plot_data(sample: Sample):
    """
    Assign initial data for plots
    Parameters
    ----------
    sample : Sample instance

    Returns
    -------
    None
    """
    for key, val in ISOCHRON_INDEX_DICT.items():
        figure = basic.get_component_byid(sample, key)
        try:
            # data = [x, sx, y, sy, (z, sz,) r1, (r2, r3,), index from 1]
            figure.data = sample.IsochronValues[val['data_index'][0]:val['data_index'][1]] + \
                          [[i + 1 for i in range(len(sample.SequenceName))]]
        except (Exception, BaseException):
            print(traceback.format_exc())
            figure.data = [[]] * (val['data_index'][1] - val['data_index'][0]) + \
                          [[i + 1 for i in range(len(sample.SequenceName))]]
        finally:
            # Ellipse
            if key != 'figure_7':
                ellipse_data = []
                for point in calc.arr.transpose(figure.data[:5]):
                    if '' not in point and None not in point:
                        ellipse_data.append(calc.isochron.get_ellipse(*point))
                        getattr(figure, 'ellipse', Set(id='ellipse')).data = ellipse_data

    # Set age spectra lines
    # Try to calculate total gas age
    try:
        a0, e0 = sum(sample.DegasValues[24]), pow(sum([i ** 2 for i in sample.DegasValues[25]]), 0.5)
        a1, e1 = sum(sample.DegasValues[20]), pow(sum([i ** 2 for i in sample.DegasValues[21]]), 0.5)
        total_f = [a0 / a1, calc.err.div((a0, e0), (a1, e1))]
        total_age = basic.calc_age(total_f[:2], smp=sample)
    except (Exception, BaseException):
        print(traceback.format_exc())
        total_f = [np.nan] * 2
        total_age = [np.nan] * 4
    sample.Info.results.age_spectra['TGA'].update(
        {'Ar39': 100, 'F': total_f[0], 'sF': total_f[1], 'age': total_age[0],
         's1': total_age[1], 's2': total_age[2], 's3': total_age[3], 'Num': len(sample.DegasValues[24])}
    )
    try:
        sample.AgeSpectraPlot.data = calc.spectra.get_data(
            *sample.ApparentAgeValues[2:4], sample.ApparentAgeValues[7])
        sample.AgeSpectraPlot.data = calc.arr.transpose(sample.AgeSpectraPlot.data)
    except (Exception, BaseException):
        print(traceback.format_exc())
        sample.AgeSpectraPlot.data = []

    # Degassing plot
    try:
        if not hasattr(sample, 'DegasPatternPlot'):
            setattr(sample, 'DegasPatternPlot', Plot(id='figure_8', name='Degas Pattern Plot'))
        isotope_percentage = lambda l: [e / sum(l) * 100 if sum(l) != 0 else 0 for e in l]
        sample.DegasPatternPlot.data = [
            isotope_percentage(sample.DegasValues[0]),  # Ar36a
            isotope_percentage(sample.DegasValues[8]),  # Ar37Ca
            isotope_percentage(sample.DegasValues[10]),  # Ar38Cl
            isotope_percentage(sample.DegasValues[20]),  # Ar39K
            isotope_percentage(sample.DegasValues[24]),  # Ar40r
            isotope_percentage(sample.CorrectedValues[0]),  # Ar36
            isotope_percentage(sample.CorrectedValues[2]),  # Ar37
            isotope_percentage(sample.CorrectedValues[4]),  # Ar38
            isotope_percentage(sample.CorrectedValues[6]),  # Ar39
            isotope_percentage(sample.CorrectedValues[8]),  # Ar40
        ]
        sample.DegasPatternPlot.info = [True] * 10
    except Exception as e:
        print(traceback.format_exc())
        pass

    # Set age distribution plot data
    try:
        recalc_agedistribution(sample)
    except Exception as e:
        print(traceback.format_exc())


# =======================
# Isochron results
# =======================
def recalc_isochrons(sample: Sample, **kwargs):
    """

    Parameters
    ----------
    sample
    kwargs

    Returns
    -------

    """
    figures = kwargs.pop('figures', ['figure_2', 'figure_3', 'figure_4', 'figure_5', 'figure_6', 'figure_7', ])
    for key, val in ISOCHRON_INDEX_DICT.items():
        if key not in figures:
            continue
        figure = basic.get_component_byid(sample, key)
        figure.set3.data, figure.set1.data, figure.set2.data = \
            sample.UnselectedSequence.copy(), sample.SelectedSequence1.copy(), sample.SelectedSequence2.copy()
        for index, sequence in enumerate([figure.set1.data, figure.set2.data, figure.set3.data]):
            set_data = calc.arr.partial(
                sample.IsochronValues, rows=sequence, cols=list(range(*val['data_index'])))
            if key != 'figure_7':
                iso_res = get_isochron_results(
                    set_data, figure_type=val["figure_type"], smp=sample, sequence=sequence)
                sample.Info.results.isochron[figure.id].update({index: iso_res})
            else:
                iso_res = get_3D_results(data=set_data, sequence=sequence, sample=sample)
                sample.Info.results.isochron[figure.id].update({index: iso_res})


def get_isochron_results(data: list, smp: Sample, sequence, figure_type: int = 0):
    """
    Get isochron figure results based on figure type.
    Parameters
    ----------
    data : isochron figure data, 5 columns list
    smp : sample instance
    sequence : data section index
    figure_type : int, 0 for normal isochron, 1 for inverse isochron, 2 for K-Cl-Ar plot 3

    Returns
    -------
    dict, isochron regression results, keys are [
        'k', 'sk', 'm1', 'sm1', 'MSWD', 'abs_conv', 'iter', 'mag', 'R2', 'Chisq', 'Pvalue',
        'rs',  'age', 's1', 's2', 's3', 'conv', 'initial', 'sinitial', 'F', 'sF'
    ]
    """
    reg_res_index = [
        'k', 'sk', 'm1', 'sm1',
        'MSWD', 'abs_conv', 'iter', 'mag', 'R2', 'Chisq', 'Pvalue',
        'rs',  # 'rs' means relative error of the total sum
    ]
    age_res_index = ['age', 's1', 's2', 's3', ]
    iso_res = dict(zip(
        [*reg_res_index, *age_res_index, 'conv', 'initial', 'sinitial', 'F', 'sF'],
        [np.nan] * (len(reg_res_index + age_res_index) + 5)
    ))

    if len(sequence) < 3:
        return iso_res
    regression_method = {
        "york-2": calc.regression.york2, "olst": calc.regression.olst
    }.get(smp.TotalParam[97][min(sequence)].lower(), calc.regression.york2)
    try:
        regression_res = regression_method(*data[:5])
    except (Exception, BaseException):
        print(f"Warning: {traceback.format_exc()}")
        return iso_res
    else:
        iso_res.update(dict(zip(reg_res_index, regression_res)))
        if figure_type == 1:
            iso_res.update(zip(['initial', 'sinitial'], regression_res[0:2]))
            iso_res.update(zip(['F', 'sF'], regression_res[2:4]))
        elif figure_type == 2:
            iso_res.update(zip(['initial', 'sinitial'], calc.arr.rec(regression_res[0:2])))
            k = regression_method(*data[2:4], *data[0:2], data[4])
            iso_res.update(zip(['F', 'sF'], calc.arr.rec(k[0:2])))
        elif figure_type == 3:
            iso_res.update(zip(['initial', 'sinitial'], regression_res[2:4]))
            iso_res.update(zip(['F', 'sF'], regression_res[0:2]))
    # age, analytical err, internal err, full external err
    try:
        age = basic.calc_age([iso_res['F'], iso_res['sF']], smp=smp)
        iso_res.update(dict(zip(age_res_index, age)))
    except ValueError:
        pass
    return iso_res


def get_3D_results(data: list, sequence: list, sample: Sample):
    """
    Get 3D regression results.
    Parameters
    ----------
    data : 3D regression data with 9 columns.
    sequence : list, data section index
    sample : sample instance

    Returns
    -------
    dict, isochron regression results, with keys = [
        'k', 'sk', 'm1', 'sm1', 'm2', 'sm2',
        'S', 'MSWD', 'R2', 'abs_conv', 'iter', 'mag', 'Chisq', 'Pvalue',
        'rs', 'age', 's1', 's2', 's3', 'conv', 'initial', 'sinitial', 'p_Cl', 'F', 'sF'
    ]
    """
    reg_res_index = [
        'k', 'sk', 'm1', 'sm1', 'm2', 'sm2',
        'S', 'MSWD', 'R2', 'abs_conv', 'iter', 'mag', 'Chisq', 'Pvalue',
        'rs',  # 'rs' means relative error of the total sum
    ]
    age_res_index = ['age', 's1', 's2', 's3', ]
    iso_res = dict(zip(
        [*reg_res_index, *age_res_index,
         'conv', 'initial', 'sinitial', 'p_Cl', 'F', 'sF'],
        [np.nan] * (len(reg_res_index + age_res_index) + 8)
    ))
    try:
        if len(sequence) < 4:
            raise ValueError(f"Data points not enough.")
        k = calc.regression.wtd_3D_regression(*data[:9])
        ar38ar36 = sample.TotalParam[4][0]
        sar38ar36 = sample.TotalParam[5][0] * sample.TotalParam[4][0] / 100
        ar40ar36 = (k[2] + k[4] * ar38ar36) * -1 / k[0]
        sar40ar36 = calc.err.div(
            ((k[2] + k[4] * ar38ar36) * -1,
             calc.err.add(k[3], calc.err.mul((k[4], k[5]), (ar38ar36, sar38ar36)))), (k[0], k[1]))
        f = 1 / k[0]
        sf = calc.err.div((1, 0), (k[0], k[1]))
        try:
            PQ = -1 * k[4] / k[2]
            Q = 1 - np.exp(-1 * sample.TotalParam[46][0] * sum(sample.TotalParam[32]) / len(sample.TotalParam[32]))
            P = PQ / Q
        except:
            print(f"Warning: {traceback.format_exc()}")
            P = 0
        age = basic.calc_age([f, sf], smp=sample)
    except:
        print(f"Warning: {traceback.format_exc()}")
        k = [0] * 15
        age = [0] * 4
        ar40ar36, sar40ar36, P = 0, 0, 0
        f, sf = 0, 0
    iso_res.update(dict(zip(iso_res, [*k, *age, np.nan, ar40ar36, sar40ar36, P, f, sf])))
    return iso_res


def reset_isochron_line_data(smp: Sample):
    """
    Set isochron regression lines
    Parameters
    ----------
    smp : sample instance

    Returns
    -------
    None, set regression lines data to sample instance.
    """
    for k, v in basic.get_components(smp).items():
        if not isinstance(v, Plot):
            continue
        for index in [0, 1]:
            try:
                xscale, yscale = [v.xaxis.min, v.xaxis.max], [v.yaxis.min, v.yaxis.max]
                coeffs = [smp.Info.results.isochron[k][index]['k'], smp.Info.results.isochron[k][index]['m1']]
                line_point = calc.isochron.get_line_points(xscale, yscale, coeffs)
                setattr(getattr(v, ['line1', 'line2'][index]), 'data', line_point)
                setattr(getattr(v, ['text1', 'text2'][index]), 'text', "")  # 注意和js的配合，js那边根据text是否为空判断是否重新生成文字
            except Exception:
                # print(traceback.format_exc())
                continue


def set_selection(smp: Sample, index: int, mark: int):
    """
    Parameters
    ----------
    smp : sample instance
    index : int, data point index
    mark : int, 0 for unselected, 1 for set1, 2 for set2

    Returns
    -------

    """
    if mark not in [1, 2]:
        raise ValueError(f"{mark = }, mark must be 1 or 2.")

    def seq(_i): return [smp.UnselectedSequence, smp.SelectedSequence1, smp.SelectedSequence2][_i]

    if index in seq(mark):
        seq(mark).remove(index)
        smp.UnselectedSequence.append(index)
    else:
        for i in [0, [0, 2, 1][mark]]:
            if index in seq(i):
                seq(i).remove(index)
        seq(mark).append(index)
    smp.IsochronMark = [
        1 if i in smp.SelectedSequence1 else 2 if i in smp.SelectedSequence2 else '' for i in
        range(len(smp.IsochronValues[2]))]
    #
    smp.Info.results.selection[0]['data'] = smp.SelectedSequence1
    smp.Info.results.selection[1]['data'] = smp.SelectedSequence2
    smp.Info.results.selection[2]['data'] = smp.UnselectedSequence


# =======================
# Age spectra results
# =======================
def recalc_plateaus(sample: Sample, **kwargs):
    if sample.Info.sample.type == "Unknown":
        return recalc_age_plateaus(sample, **kwargs)
    if sample.Info.sample.type == "Standard":
        return recalc_j_plateaus(sample, **kwargs)
    if sample.Info.sample.type == "Air":
        return recalc_j_plateaus(sample, **kwargs)


def recalc_age_plateaus(sample: Sample, **kwargs):
    """
    Calculate age plateaus results
    Parameters
    ----------
    sample : sample instance
    kwargs : optional args, keys in [r1, sr1, r2, sr2]

    Returns
    -------
    None
    """
    params_initial_ratio = calc.arr.partial(sample.TotalParam, cols=list(range(115, 120)))
    ratio_set1 = [[], []]
    ratio_set2 = [[], []]
    for row, item in enumerate(params_initial_ratio[0]):
        if str(item) == '0':
            ratio_set1[0].append(sample.Info.results.isochron['figure_3'][0]['initial'])
            ratio_set1[1].append(sample.Info.results.isochron['figure_3'][0]['sinitial'])
            ratio_set2[0].append(sample.Info.results.isochron['figure_3'][1]['initial'])
            ratio_set2[1].append(sample.Info.results.isochron['figure_3'][1]['sinitial'])
        elif str(item) == '1':
            ratio_set1[0].append(sample.Info.results.isochron['figure_2'][0]['initial'])
            ratio_set1[1].append(sample.Info.results.isochron['figure_2'][0]['sinitial'])
            ratio_set2[0].append(sample.Info.results.isochron['figure_2'][1]['initial'])
            ratio_set2[1].append(sample.Info.results.isochron['figure_2'][1]['sinitial'])
        elif str(item) == '2':
            ratio_set1[0].append(params_initial_ratio[1][row])
            ratio_set1[1].append(params_initial_ratio[2][row])
            ratio_set2[0].append(params_initial_ratio[3][row])
            ratio_set2[1].append(params_initial_ratio[4][row])
        else:
            ratio_set1[0].append(298.56)
            ratio_set1[1].append(0.31)
            ratio_set2[0].append(298.56)
            ratio_set2[1].append(0.31)

    # Get ages and line data points for each set
    try:
        set1_res, set1_age, set1_data = \
            get_plateau_results(sample, sample.SelectedSequence1, calc_ar40ar39(*ratio_set1, smp=sample))
    except ValueError:
        pass
        # raise ValueError(f"Set 1 Plateau results calculation error.")
    else:
        sample.Info.results.age_plateau.update({0: set1_res})
        sample.AgeSpectraPlot.set1.data = calc.arr.transpose(set1_data)
        sample.AgeSpectraPlot.text1.text = ""  # 注意和js的配合，js那边根据text是否为空判断是否重新生成文字
    try:
        set2_res, set2_age, set2_data = \
            get_plateau_results(sample, sample.SelectedSequence2, calc_ar40ar39(*ratio_set2, smp=sample))
    except ValueError:
        pass
        # raise ValueError(f"Set 2 Plateau results calculation error.")
    else:
        sample.Info.results.age_plateau.update({1: set2_res})
        sample.AgeSpectraPlot.set2.data = calc.arr.transpose(set2_data)
        sample.AgeSpectraPlot.text2.text = ""  # 注意和js的配合，js那边根据text是否为空判断是否重新生成文字

    # Get weighted mean ages of two sets
    try:
        set1_res = get_wma_results(sample, sample.SelectedSequence1)
    except ValueError:
        pass
        # raise ValueError(f"Set 1 WMA calculation error.")
    else:
        sample.Info.results.age_spectra.update({0: set1_res})
    try:
        set2_res = get_wma_results(sample, sample.SelectedSequence2)
    except ValueError:
        pass
        # raise ValueError(f"Set 2 WMA calculation error.")
    else:
        sample.Info.results.age_spectra.update({1: set2_res})

    # # """3D corrected plateaus"""
    # # 3D ratio, 36Ar(a+cl)/40Ar(a+r), 38Ar(a+cl)/40Ar(a+r), 39Ar(k)/40Ar(a+r),
    # ar40ar = calc_funcs.list_sub(*sample.CorrectedValues[8:10], *sample.DegasValues[30:32])
    # # 36Ar deduct Ca, that is sum of 36Ara and 36ArCl
    # ar36acl = calc_funcs.list_sub(*sample.CorrectedValues[0:2], *sample.DegasValues[4:6])
    # # 38Ar deduct K and Ca, that is sum of 38Ara and 38ArCl
    # ar38acl = calc_funcs.list_sub(*calc_funcs.list_sub(*sample.CorrectedValues[4:6], *sample.DegasValues[16:18]),
    #                               *sample.DegasValues[18:20])
    # # 39ArK
    # ar39k = sample.DegasValues[20:22]
    #
    # # 40Arr
    # def get_modified_f(c, sc, a, sa, b, sb):
    #     ar40r = list(map(lambda zi, xi, yi: zi - a * xi - b * yi, ar40ar[0], ar36acl[0], ar38acl[0]))
    #     sar40r = list(map(lambda zi, szi, xi, sxi, yi, syi:
    #                       calc.err.add(szi, calc_funcs.error_mul((xi, sxi), (a, sa)),
    #                                            calc_funcs.error_mul((yi, syi), (b, sb))),
    #                       *ar40ar, *ar36acl, *ar38acl))
    #     f = list(map(lambda ar40ri, ar39ki: ar40ri / ar39ki, ar40r, ar39k[0]))
    #     sf = list(map(lambda ar40ri, sar40ri, ar39ki, sar39ki:
    #                   calc.err.div((ar40ri, sar40ri), (ar39ki, sar39ki)),
    #                   ar40r, sar40r, *ar39k))
    #     return [f, sf]
    #
    # isochron_7 = calc_funcs.get_3D_isochron(*ar36acl, *ar38acl, *ar40ar, *ar39k)
    # [set1_data, set2_data, set3_data] = basic_funcs.getIsochronSetData(
    #     isochron_7, sample.SelectedSequence1, sample.SelectedSequence2, sample.UnselectedSequence)
    #
    # __isochron_7 = calc_funcs.get_3D_isochron(*ar36acl, *ar38acl, *ar39k, *ar40ar)
    # [__set1_data, __set2_data, __set3_data] = basic_funcs.getIsochronSetData(
    #     __isochron_7, sample.SelectedSequence1, sample.SelectedSequence2, sample.UnselectedSequence)
    #
    # def __get_modified_f(c, sc, a, sa, b, sb):
    #     f = list(
    #         map(lambda zi, xi, yi: 1 / (zi - a * xi - b * yi), __isochron_7[4], __isochron_7[0], __isochron_7[2]))
    #     sf = [0] * len(f)
    #     return [f, sf]
    #
    # # set 1:
    # try:
    #     k = calc_funcs.wtd_3D_regression(*set1_data[:9])
    #     set1_ar40rar39k = get_modified_f(*k[:6])
    #
    #     # __k = calc_funcs.wtd_3D_regression(*__set1_data[:9])
    #     # __set1_ar40rar39k = __get_modified_f(*__k[:6])
    #     #
    #     # for i in range(len(set1_ar40rar39k[0])):
    #     #     print(f"{set1_ar40rar39k[0][i]} == {__set1_ar40rar39k[0][i]}")
    #     #
    #     # k = calc_funcs.wtd_3D_regression(*__set1_data[:9])
    #     # set1_ar40rar39k = __get_modified_f(*k[:6])
    #
    # except:
    #     print(traceback.format_exc())
    #     set1_ar40rar39k = [[0] * len(ar39k[0]), [0] * len(ar39k[0])]
    # # set 2:
    # try:
    #     k = calc_funcs.wtd_3D_regression(*set2_data[:9])
    #     set2_ar40rar39k = get_modified_f(*k[:6])
    # except:
    #     set2_ar40rar39k = [[0] * len(ar39k[0]), [0] * len(ar39k[0])]
    # set4_age, set4_data, set4_wmf, set4_wmage, set4_text = \
    #     get_plateau_results(sample, sample.SelectedSequence1, set1_ar40rar39k)
    # set5_age, set5_data, set5_wmf, set5_wmage, set5_text = \
    #     get_plateau_results(sample, sample.SelectedSequence2, set2_ar40rar39k)
    # # Set set4 and set5
    # sample.AgeSpectraPlot.set4.data = calc.arr.transpose(set4_data)
    # sample.AgeSpectraPlot.set5.data = calc.arr.transpose(set5_data)
    # sample.AgeSpectraPlot.set4.info = [*set4_wmf, *set4_wmage]  # Info = weighted mean f, sf, np, mswd, age, s, s, s
    # sample.AgeSpectraPlot.set5.info = [*set5_wmf, *set5_wmage]  # Info = weighted mean f, sf, np, mswd, age, s, s, s
    # # """end"""


def calc_ar40ar39(r, sr, smp):
    """
    Calculate Ar40r / Ar39K based on passed initial ratio.
    Parameters
    ----------
    r : ratio value, float or list
    sr : error of the ratio, same type as r
    smp : sample instance

    Returns
    -------
    Two dimensional list, Ar40r / Ar39K values and errors
    """
    try:
        ar36a = np.array(smp.DegasValues[0:2])
        ar39k = smp.DegasValues[20:22]
        ar40 = smp.CorrectedValues[8:10]
        ar40k = smp.DegasValues[30:32]
        size = ar36a.shape[-1]
        if isinstance(r, float) and isinstance(sr, float):
            ratio = np.array([[r] * size, [sr] * size])
        elif isinstance(r, list) and isinstance(sr, list):
            ratio = np.array([r, sr])
        else:
            raise ValueError(f"Initial ratio is unsupported.")
        # print(f"{ratio = }")
        # print(f"{ar36a = }")
        ar40a = calc.arr.mul(ar36a, ratio)
        ar40r = calc.arr.sub(ar40, ar40k, ar40a)
        ar40rar39k: list = calc.arr.div(ar40r, ar39k)
    except (IndexError, AttributeError, ValueError):
        raise ValueError(f"Check tables of corrected values and degas values.")
    else:
        return ar40rar39k


def get_plateau_results(sample: Sample, sequence: list, ar40rar39k: list = None,
                        ar39k_percentage: list = None):
    """
    Get initial ratio re-corrected plateau results
    Parameters
    ----------
    sample : sample instance
    sequence : data slice index
    ar40rar39k :
    ar39k_percentage : Ar39K released

    Returns
    -------
    three itmes tuple, result dict, age, and plot data, results keys = [
        'F', 'sF', 'Num', 'MSWD', 'Chisq', 'Pvalue',
        'age', 's1', 's2', 's3', 'Ar39', 'rs'
    ]
    """
    plateau_res_keys = [
        'F', 'sF', 'Num', 'MSWD', 'Chisq', 'Pvalue', 'age', 's1', 's2', 's3', 'Ar39',
        'rs',  # 'rs' means relative error of the total sum
    ]
    plateau_res = dict(zip(plateau_res_keys, [np.nan for i in plateau_res_keys]))

    def _get_partial(points, *args):
        return [arg[min(points): max(points) + 1] for arg in args]

    if len(sequence) == 0:
        return plateau_res, [], []
    if ar40rar39k is None:
        ar40rar39k = sample.ApparentAgeValues[0:2]
    if ar39k_percentage is None:
        ar39k_percentage = sample.ApparentAgeValues[7]

    age = basic.calc_age(ar40ar39=ar40rar39k, smp=sample)[0:2]
    plot_data = calc.spectra.get_data(*age, ar39k_percentage, indices=sequence)
    f_values = _get_partial(sequence, *ar40rar39k)
    age = _get_partial(sequence, *age)
    sum_ar39k = sum(_get_partial(sequence, ar39k_percentage)[0])
    wmf = calc.arr.wtd_mean(*f_values)
    wmage = basic.calc_age(wmf[0:2], smp=sample)

    plateau_res.update(dict(zip(
        plateau_res_keys, [*wmf, *wmage, sum_ar39k, np.nan]
    )))
    return plateau_res, age, plot_data


def get_wma_results(sample: Sample, sequence: list):
    """
    Get initial ratio re-corrected plateau results
    Parameters
    ----------
    sample : sample instance
    sequence : data slice index

    Returns
    -------
    three itmes tuple, result dict, age, and plot data, results keys = [
        'F', 'sF', 'Num', 'MSWD', 'Chisq', 'Pvalue',
        'age', 's1', 's2', 's3', 'Ar39', 'rs'
    ]
    """
    spectra_res = initial.SPECTRA_RES.copy()
    # spectra_res = initial.SPECTRA_RES

    def _get_partial(points, *args):
        return [arg[min(points): max(points) + 1] for arg in args]

    if len(sequence) > 0:
        sum_ar39k = sum(_get_partial(sequence, sample.ApparentAgeValues[7])[0])
        fs = _get_partial(sequence, sample.ApparentAgeValues[0])[0]
        sfs = _get_partial(sequence, sample.ApparentAgeValues[1])[0]

        wmf, swmf, num, mswd, chisq, p = calc.arr.wtd_mean(fs, sfs)
        age, s1, s2, s3 = basic.calc_age([wmf, swmf], smp=sample)

        spectra_res.update({
            'age': age, 's1': s1, 's2': s2, 's3': s3, 'Num': num, 'MSWD': mswd, 'Chisq': chisq, 'Pvalue': p,
            'F': wmf, 'sF': swmf, 'Ar39': sum_ar39k
        })
    return spectra_res


def recalc_j_plateaus(sample: Sample, **kwargs):

    print(f"Recalc J plateau")

    j = sample.ApparentAgeValues[2:4]

    try:
        set1_res, _, set1_data = \
            get_j_plateau_results(sample, sample.SelectedSequence1, j)
    except ValueError:
        pass
    else:
        sample.Info.results.age_plateau.update({0: set1_res})
        sample.AgeSpectraPlot.set1.data = calc.arr.transpose(set1_data)
        sample.AgeSpectraPlot.text1.text = ""  # 注意和js的配合，js那边根据text是否为空判断是否重新生成文字

    try:
        set2_res, _, set2_data = \
            get_j_plateau_results(sample, sample.SelectedSequence2, j)
    except ValueError:
        pass
    else:
        sample.Info.results.age_plateau.update({1: set2_res})
        sample.AgeSpectraPlot.set2.data = calc.arr.transpose(set2_data)
        sample.AgeSpectraPlot.text2.text = ""  # 注意和js的配合，js那边根据text是否为空判断是否重新生成文字


def get_j_plateau_results(sample: Sample, sequence: list, j: list, ar39k_percentage: list = None):

    def _get_partial(points, *args):
        # return [arg[min(points): max(points) + 1] for arg in args]
        return [[arg[i] for i in points] for arg in args]

    if ar39k_percentage is None:
        ar39k_percentage = sample.ApparentAgeValues[7]
    sum_ar39k = sum(_get_partial(sequence, ar39k_percentage)[0])

    j_values = _get_partial(sequence, *j)
    wmj = calc.arr.wtd_mean(*j_values)
    plot_data = [[sum(ar39k_percentage[:min(sequence)]), sum(ar39k_percentage[:max(sequence) + 1])],
                 [wmj[0], wmj[0]]]

    plateau_res_keys = [
        'F', 'sF', 'Num', 'MSWD', 'Chisq', 'Pvalue', 'age', 's1', 's2', 's3', 'Ar39',
        'rs',  # 'rs' means relative error of the total sum
    ]
    plateau_res = dict(zip(plateau_res_keys, [np.nan for i in plateau_res_keys]))
    plateau_res.update(dict(zip(plateau_res_keys, [*wmj, np.nan, np.nan, np.nan, np.nan, sum_ar39k, np.nan])))

    return plateau_res, 0, plot_data


# =======================
# Age Distribution Plot
# =======================
def recalc_agedistribution(sample: Sample, **kwargs):
    for i in range(2):
        try:
            # Age bars
            sample.AgeDistributionPlot.set3.data = calc.arr.remove(sample.ApparentAgeValues[2:4], (None, np.nan))
            # Set histogram data
            s = getattr(sample.AgeDistributionPlot.set1, 'bin_start', None)
            w = getattr(sample.AgeDistributionPlot.set1, 'bin_width', None)
            c = getattr(sample.AgeDistributionPlot.set1, 'bin_count', None)
            r = getattr(sample.AgeDistributionPlot.set1, 'bin_rule', None)
            # print(f's = {s}, r = {r}, w = {w}, c = {c}')
            histogram_data = calc.histogram.get_data(sample.ApparentAgeValues[2], s=s, r=r, w=w, c=c)
            sample.AgeDistributionPlot.set1.data = [histogram_data[1], histogram_data[0], histogram_data[2]]  # [half_bins, counts]
            setattr(sample.AgeDistributionPlot.set1, 'bin_start', histogram_data[3])
            setattr(sample.AgeDistributionPlot.set1, 'bin_rule', histogram_data[4])
            setattr(sample.AgeDistributionPlot.set1, 'bin_width', histogram_data[5])
            setattr(sample.AgeDistributionPlot.set1, 'bin_count', histogram_data[6])
            h = getattr(sample.AgeDistributionPlot.set2, 'band_width', None)
            k = getattr(sample.AgeDistributionPlot.set2, 'band_kernel', 'normal')
            t = getattr(sample.AgeDistributionPlot.set2, 'band_extend', False)
            a = getattr(sample.AgeDistributionPlot.set2, 'auto_width', 'Scott')
            n = getattr(sample.AgeDistributionPlot.set2, 'band_points', 1000)
            # print(f'h = {h}, k = {k}, a = {a}, n = {n}, extend = {t}')
            kda_data = calc.histogram.get_kde(
                sample.ApparentAgeValues[2], h=h, k=k, n=n, a=a,
                s=float(getattr(sample.AgeDistributionPlot.xaxis, 'min')) if t else histogram_data[3],
                e=float(getattr(sample.AgeDistributionPlot.xaxis, 'max')) if t else histogram_data[7],
            )
            sample.AgeDistributionPlot.set2.data = kda_data[0]  # [values, kda]
            setattr(sample.AgeDistributionPlot.set2, 'band_width', kda_data[1])
            setattr(sample.AgeDistributionPlot.set2, 'band_kernel', kda_data[2])
            setattr(sample.AgeDistributionPlot.set2, 'auto_width', kda_data[3])
            # sorted_data = [i[0] for i in sorted(zipped_data, key=lambda x: x[1])]
            text = f'n = {len(sample.ApparentAgeValues[2])}'
            peaks = find_peaks(kda_data[0][1])
            for index, peak in enumerate(peaks[0].tolist()):
                text = text + f'\nPeak {index}: {kda_data[0][0][peak]:.2f}'
            setattr(sample.AgeDistributionPlot.text1, 'text', text)
        except AttributeError:
            print(traceback.format_exc())
            initial.re_set_smp(sample)
            continue
        except (Exception, BaseException):
            print(traceback.format_exc())
            sample.AgeDistributionPlot.data = [[], []]
            sample.AgeDistributionPlot.set1.data = [[], []]
            sample.AgeDistributionPlot.set2.data = [[], []]
        break


