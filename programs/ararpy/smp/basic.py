#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - smp - basic
# ==========================================
#
#
#
"""
# === Internal imports ===
import os
import traceback
import pandas as pd
import numpy as np
import copy
from typing import Optional, Union, List
from .. import calc
from ..files.basic import (read as read_params)
from .sample import Sample, Table, Plot, ArArData, ArArBasic, Sequence, RawData

Set = Plot.Set
Label = Plot.Label
Axis = Plot.Axis
Text = Plot.Text

pd.options.mode.chained_assignment = None  # default='warn'


# =======================
# Calculate ages
# =======================
def calc_apparent_ages(smp: Sample):
    """

    Parameters
    ----------
    smp

    Returns
    -------

    """
    if smp.Info.sample.type == "Unknown":
        age = calc_age(smp=smp)
        smp.ApparentAgeValues[2:6] = age
        smp.PublishValues[5:7] = copy.deepcopy(age[0:2])
    if smp.Info.sample.type == "Standard":
        j = calc_j(smp=smp)
        smp.ApparentAgeValues[2:4] = j
        smp.PublishValues[5:7] = copy.deepcopy(j[0:2])
    if smp.Info.sample.type == "Air":
        mdf = calc_mdf(smp=smp)
        smp.ApparentAgeValues[2:4] = mdf
        smp.PublishValues[5:7] = copy.deepcopy(mdf[0:2])


def calc_j(ar40ar39=None, params: dict = None, smp: Sample = None, index: list = None):
    std_age, std_err = smp.TotalParam[59:61]
    r, sr = smp.ApparentAgeValues[0:2]  # ar40ar39, error
    f, rsf = smp.TotalParam[34:36]  # L, sL
    j, sj = calc.jvalue.j_value(std_age, std_err, r, sr, f, rsf)
    return [j.tolist(), sj.tolist()]


def calc_mdf(ar40ar36=None, params: dict = None, smp: Sample = None, index: list = None):
    std_air, std_err = smp.TotalParam[93:95]
    m36, sm36 = smp.TotalParam[71:73]
    m40, sm40 = smp.TotalParam[79:81]
    air, sair = smp.ApparentAgeValues[0:2]  # ar40ar36 air, error
    discrimination_method = smp.TotalParam[100]  # L, sL
    mdf = []
    for i in range(len(std_air)):
        k = calc.corr.mdf(air[i], sair[i], m36[i], m40[i], std_air[i], std_err[i])  # linear, exp, pow
        mdf.append({"linear": k[0:2], "exp": k[2:4], "pow": k[4:6]}[discrimination_method[i].lower()])
    return np.transpose(mdf).tolist()


def calc_age(ar40ar39=None, params: dict = None, smp: Sample = None, index: list = None):
    """
    40Ar/39Ar age calculation, two methods are supported: Min et al. (2000) or general equation.
    Parameters
    ----------
    ar40ar39 : 2D DataFrame, Series, list
    params : dict
    smp : Sample instance
    index:

    Returns
    -------

    """
    params_index_dict = {
        34: 'L', 35: 'sL', 36: 'Le', 37: 'sLe', 38: 'Lb', 39: 'sLb', 48: 'A', 49: 'sA',
        50: 'Ae', 51: 'sAe', 52: 'Ab', 53: 'sAb', 59: 't', 60: 'st', 67: 'J', 68: 'sJ',
        81: 'W', 82: 'sW', 83: 'No', 84: 'sNo', 85: 'Y', 86: 'sY', 87: 'f', 88: 'sf', 110: 'Min'
    }

    if isinstance(ar40ar39, pd.Series):
        ar40ar39 = [ar40ar39.tolist(), [0] * ar40ar39.size]
    if isinstance(ar40ar39, pd.DataFrame):
        ar40ar39 = ar40ar39.transpose().values.tolist()
    if ar40ar39 is None and smp is not None:
        ar40ar39 = smp.ApparentAgeValues[0:2]
    if len(np.shape(ar40ar39)) == 1:
        ar40ar39 = np.reshape(ar40ar39, (2, 1))
    if index is None:
        index = list(range(np.shape(ar40ar39)[-1]))

    if smp is None and params is None:
        raise ValueError(f"Parameters are required for calculating ages, or it is empty.")
    if params is not None:
        for key, val in params.items():
            if not isinstance(val, list):
                params[key] = list(val)
    if smp is not None:
        try:
            params_from_smp = dict(zip(
                list(params_index_dict.values()),
                [[smp.TotalParam[i][j] for j in index] for i in params_index_dict.keys()]
            ))
        except Exception:
            print(traceback.format_exc())
            raise ValueError(f"Parameters cannot be found in the given sample object")
        if params is not None:
            params_from_smp.update(params)
        params = params_from_smp

    # check if using Min equation
    params['Min'] = [i if isinstance(i, bool) else False for i in params['Min']]

    idx1 = np.flatnonzero(np.where(params['Min'], True, False))  # True, using Min euqation
    idx2 = np.flatnonzero(np.where(params['Min'], False, True))  # False
    k1, k2 = [], []
    if np.size(idx1) > 0:
        k1 = calc.age.calc_age_min(
            F=[ar40ar39[0][i] for i in idx1], sF=[ar40ar39[1][i] for i in idx1],
            **dict(zip(params.keys(), [[val[i] for i in idx1] for val in params.values()])))
    if np.size(idx2) > 0:
        k2 = calc.age.calc_age_general(
            F=[ar40ar39[0][i] for i in idx2], sF=[ar40ar39[1][i] for i in idx2],
            **dict(zip(params.keys(), [[val[i] for i in idx2] for val in params.values()])))

    # idx1 = params[params['Min'].astype(bool)].index
    # idx2 = params[~params['Min'].astype(bool)].index  # The operators are: | for or, & for and, and ~ for not
    # k1, k2 = [], []
    # if idx1.size > 0:
    #     k1 = calc.age.calc_age_min(
    #         F=ar40ar39.take(idx1)[0], sF=ar40ar39.take(idx1)[1], **params.take(idx1).to_dict('list'))
    # if idx2.size > 0:
    #     k2 = calc.age.calc_age_general(
    #         F=ar40ar39.take(idx2)[0], sF=ar40ar39.take(idx2)[1], **params.take(idx2).to_dict('list'))

    columns = ['age', 's1', 's2', 's3']
    ages = pd.concat([
        pd.DataFrame([*k1], columns=idx1, index=columns),
        pd.DataFrame([*k2], columns=idx2, index=columns)
    ], axis=1).transpose().reset_index(drop=True)

    if len(index) == 1:
        return ages.transpose().squeeze().tolist()
    else:
        return ages.transpose().values.tolist()


# =======================
# Search components
# =======================
def get_content_dict(smp: Sample):
    """

    Parameters
    ----------
    smp

    Returns
    -------

    """
    return dict(zip(
        ['smp', 'blk', 'cor', 'deg', 'pub', 'age', 'iso', 'pam', 'mak', 'seq'],
        [smp.SampleIntercept, smp.BlankIntercept, smp.CorrectedValues, smp.DegasValues,
         smp.PublishValues, smp.ApparentAgeValues, smp.IsochronValues, smp.TotalParam,
         [smp.IsochronMark], [smp.SequenceName, smp.SequenceValue]]
    ))


def get_dict_from_obj(obj: (Sample, Plot, Table, Set, Label, Axis, Text,
                            ArArBasic, ArArData, Sequence, RawData)):
    """

    Parameters
    ----------
    obj

    Returns
    -------

    """
    res = {}
    for key, attr in obj.__dict__.items():
        if not isinstance(attr, (Sample, Plot, Table, Set, Label, Axis, Text,
                                 ArArBasic, ArArData, Sequence, RawData)):
            res.update({key: attr})
        else:
            res.update({key: get_dict_from_obj(attr)})
    return res


def get_components(smp: Sample):
    """
    Get updated sample.Components dict
    Parameters
    ----------
    smp

    Returns
    -------

    """
    components_name = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8',
        'figure_1', 'figure_2', 'figure_3', 'figure_4', 'figure_5', 'figure_6', 'figure_7', 'figure_8', 'figure_9',
    ]
    components = {}
    for key in components_name:
        comp = get_component_byid(smp, key)
        components.update({key: comp})
    return components


def get_component_byid(smp: Sample, comp_id: str):
    """
    Get a component (Table or Plot) based on input id
    Parameters
    ----------
    smp
    comp_id

    Returns
    -------

    """
    for key, val in smp.__dict__.items():
        if isinstance(val, (Plot, Table, ArArBasic)) and getattr(val, 'id') == comp_id:
            return val


def get_plot_set(plot: Plot, comp_id):
    """
    Get a Set, Text, Axis, Label of a sample instance based on given id
    """
    for v in [getattr(plot, k) for k in dir(plot)]:
        if isinstance(v, Plot.BasicAttr) and v.id.lower() == comp_id.lower():
            return v
    return None


# =======================
# Update
# =======================
def update_plot_from_dict(plot, attrs: dict):
    """ Set instance based on the given attrs dictionary
    Parameters
    ----------
    plot
    attrs : dict
        for example: update_plot_from_dict(sample.Info, info: dict), where info = {
            'sample': {'name': 'name', 'material': 'material', 'location': 'location'},
            'researcher': {'name': 'researcher'},
            'laboratory': {'name': 'laboratory'}
        }

    Returns
    -------

    """

    def _do(_plot, _attrs: dict):
        for k1, v1 in _attrs.items():
            if isinstance(v1, dict):
                if hasattr(_plot, k1):
                    if isinstance(getattr(_plot, k1), dict):
                        setattr(_plot, k1, calc.basic.update_dicts(getattr(_plot, k1), v1))
                        # setattr(_plot, k1, v1)
                    else:
                        _do(getattr(_plot, k1), v1)
            else:
                setattr(_plot, k1, v1)

    _do(_plot=plot, _attrs=attrs)
    return plot


def update_object_from_dict(obj, attrs: dict):
    """
    update object
    Parameters
    ----------
    obj
    attrs

    Returns
    -------

    """
    def _do(_obj, _attrs: dict):

        for k1, v1 in _attrs.items():
            if hasattr(_obj, k1):
                if getattr(_obj, k1) == v1:
                    continue
                elif isinstance(v1, dict):
                    if isinstance(getattr(_obj, k1), dict):
                        setattr(_obj, k1, calc.basic.update_dicts(getattr(_obj, k1), v1))
                        # setattr(_plot, k1, v1)
                    else:
                        _do(getattr(_obj, k1), v1)
                else:
                    setattr(_obj, k1, v1)
            else:
                setattr(_obj, k1, v1)

    _do(_obj=obj, _attrs=attrs)
    return obj


# =======================
# Merge sample instances
# =======================
def get_merged_smp(a: Sample, b: (Sample, dict)):
    """ Comparing two sample instances a and b
        This function is used to update sample instance to make sure JS can read properties it required.
    Parameters
    ----------
    a : sample instance that has old attributes,
    b : new sample instance that has some new attributes or a has similar but different name for this attribute

    Returns
    -------
    None
        return none, but a will be updated after calling this function

            for example:
                A = Sample(id = 'a', set1 = Set(id = 'set1', data = [], symbolSize = 10)),
                B = Sample(id = 'b', set1 = Set(id = 'set1', data = [2023], symbol_size = 5, line_type = 'solid')),
                after get_merged_smp(A, B), A will be Sample(id = 'a', 'set1' = Set(id = 'set1', data = [],
                                                        symbol_size = 10, line_type = 'solid'))
    """

    def get_similar_name(_name: str):
        res = []
        for i in range(len(_name) + 1):
            str_list = [i for i in _name]
            str_list.insert(i, '_')
            res.append(''.join(str_list))
        for i in range(len(_name)):
            str_list = [i for i in _name]
            str_list[i] = str_list[i].capitalize()
            res.append(''.join(str_list))
        for i in range(len(_name)):
            str_list = [i for i in _name]
            if _name[i] in '-_':
                str_list.pop(i)
                res.append(''.join(str_list))
        return res

    if not isinstance(b, dict):
        b = b.__dict__

    for name, attr in b.items():
        if hasattr(a, name):
            if isinstance(attr, (Plot, Table, ArArBasic, Plot.BasicAttr)):
                if not type(getattr(a, name)) == type(attr):
                    if isinstance(getattr(a, name), dict):
                        setattr(a, name, type(attr)(**getattr(a, name)))
                    else:
                        setattr(a, name, type(attr)())
                get_merged_smp(getattr(a, name), attr)
            if isinstance(attr, dict) and isinstance(getattr(a, name), dict):
                setattr(a, name, calc.basic.merge_dicts(getattr(a, name), attr))
            if isinstance(attr, list) and isinstance(getattr(a, name), list):
                if len(attr) > len(getattr(a, name)):
                    setattr(a, name, getattr(a, name) + attr[len(getattr(a, name)):])
            continue
        else:
            for xxx in get_similar_name(name):
                for xx in get_similar_name(xxx):
                    for x in get_similar_name(xx):
                        if hasattr(a, x):
                            # print(f'Has similar {name} = {x}: {getattr(a, x)}')
                            setattr(a, name, getattr(a, x))
                            break
                    else:
                        continue
                    break
                else:
                    continue
                break
            if not hasattr(a, name):
                setattr(a, name, attr)


# =======================
# Difference between two sample instances
# =======================
def get_diff_smp(backup: (dict, Sample), smp: (dict, Sample)):
    """ Comparing two sample component dicts or sample instances, and return difference between them.
    Parameters
    ----------
    backup : backup of sample.Components or sample before changed.
    smp : sample.Components or sample after changed

    Returns
    -------
    dict
        dict of keys and values that have difference, iterate to a sepcial difference,

            for example:
                A = Sample(id = 'a', set1 = Set(id = 'set1', data = [])),
                B = Sample(id = 'b', set1 = Set(id = 'set1', data = [2023])),
                res = get_diff_smp(A, B) will be {'id': 'b', 'set1': {'data': [2023]}}

    """
    res = {}
    if isinstance(backup, Sample) and isinstance(smp, Sample):
        return get_diff_smp(backup.__dict__, smp.__dict__)
    for name, attr in smp.items():
        if name not in backup.keys() or not isinstance(backup[name], type(attr)):
            res.update({name: attr})
            continue
        if isinstance(attr, dict):
            # if name not in backup.keys():
            #     res.update({name: attr})
            #     continue
            _res = get_diff_smp(backup[name], attr)
            if _res != {}:
                res.update({name: _res})
            continue
        if isinstance(attr, np.ndarray):
            if not np.array_equal(attr, backup[name]):
                res.update({name: attr})
            continue
        if isinstance(attr, (Plot, Table, Plot.Text, Plot.Axis, Plot.Set,
                             Plot.Label, Plot.BasicAttr, ArArBasic, ArArData)):
            _res = get_diff_smp(backup[name].__dict__, attr.__dict__)
            if _res != {}:
                res.update({name: _res})
            continue
        if str(backup[name]) == str(attr) or backup[name] == attr:
            continue
        res.update({name: attr})
    return res


# =======================
# Set parameters
# =======================
def set_params(smp: Sample, params: Union[List, str], flag: Optional[str] = None):
    """
    Parameters
    ----------
    smp
    params
    flag : optional, should be one of 'calc', 'irra', and 'smp'. If it is not given,
        the text of the extension without a dot will be used

    Returns
    -------

    """
    if isinstance(params, str) and os.path.isfile(params):
        if flag is None:
            flag = params.split(".")[-1]
        return set_params(smp, read_params(params), flag=flag)

    def remove_none(old_params, new_params, rows, length):
        res = [[]] * length
        for index, item in enumerate(new_params):
            if item is None:
                res[index] = old_params[index]
            else:
                res[index] = [item] * rows
        return res

    n = len(smp.SequenceName)

    if flag == 'calc':
        smp.TotalParam[34:56] = remove_none(smp.TotalParam[34:56], params[0:22], n, 56 - 34)
        smp.TotalParam[71:97] = remove_none(smp.TotalParam[71:97], params[22:48], n, 97 - 71)
    elif flag == 'irra':
        smp.TotalParam[0:20] = remove_none(smp.TotalParam[0:20], params[0:20], n, 20 - 0)
        smp.TotalParam[56:58] = remove_none(smp.TotalParam[56:58], params[20:22], n, 57 - 55)  # Cl36/38 productivity
        smp.TotalParam[20:27] = remove_none(smp.TotalParam[20:27], params[22:29], n, 27 - 20)
        # smp.TotalParam[26] = [params[26]] * n
        irradiation_time = []
        duration = []
        if None not in params[29:-3] and '' not in params[29:-3]:
            for i in range(len(params[29:-3])):
                if i % 2 == 0:
                    # [d, t] = params[29:-3][i].split('T')
                    # [t1, t2] = t.split(':')
                    # irradiation_time.append(d + '-' + t1 + '-' + t2 + 'D' + str(params[29:-3][i + 1]))
                    text = params[29:-3][i]
                    for char in ['T', ':']:
                        text = text.replace(char, '-')
                    irradiation_time.append(params[29:-3][i] + 'D' + str(params[29:-3][i + 1]))
                    duration.append(float(params[29:-3][i + 1]))
            smp.TotalParam[27] = ['S'.join(irradiation_time)] * n
            smp.TotalParam[28] = [params[-3]] * n
            smp.TotalParam[29] = [sum(duration)] * n
        if params[-5] != '':
            # [a, b] = params[-5].split('T')
            # [b, c] = b.split(':')
            # smp.TotalParam[30] = [a + '-' + b + '-' + c] * n
            text = params[-5]
            for char in ['T', ':']:
                text = text.replace(char, '-')
            # smp.TotalParam[30] = [text] * n
            smp.TotalParam[30] = [params[-5]] * n
        try:
            stand_time_second = [
                calc.basic.get_datetime(*smp.TotalParam[31][i].split('-')) - calc.basic.get_datetime(
                    *smp.TotalParam[30][i].split('-')) for i in range(n)]
        except Exception as e:
            # print(f'Error in calculate standing duration: {traceback.format_exc()}')
            pass
        else:
            smp.TotalParam[32] = [i / (3600 * 24 * 365.242) for i in stand_time_second]  # stand year

    elif flag == 'smp':
        smp.TotalParam[67:71] = remove_none(smp.TotalParam[67:71], params[0:4], n, 71 - 67)
        smp.TotalParam[58:67] = remove_none(smp.TotalParam[58:67], params[4:13], n, 67 - 58)
        smp.TotalParam[97:100] = remove_none(smp.TotalParam[97:100], params[13:16], n, 100 - 97)
        smp.TotalParam[115:120] = remove_none(smp.TotalParam[115:120], params[16:21], n, 120 - 115)
        smp.TotalParam[120:123] = remove_none(smp.TotalParam[120:123], params[21:24], n, 123 - 120)
        smp.TotalParam[100:114] = remove_none(
            smp.TotalParam[100:114],
            [['Linear', 'Exponential', 'Power'][params[24:27].index(True)] if True in params[24:27] else '', *params[27:]], n, 114 - 100)
    else:
        raise KeyError(f"{flag = } is not supported. It must be 'calc' for Calc Params, "
                       f"'irra' for Irradiation Params, or 'smp' for Sample Params.")
    return smp


def get_sequence(smp: Sample):
    return ArArBasic(
        size=len(smp.SequenceName), name=smp.SequenceName, value=smp.SequenceValue, unit=smp.SequenceUnit,
        mark=ArArBasic(
            size=len(smp.IsochronMark), value=smp.IsochronMark,
            set1=ArArBasic(size=sum([1 if i == 1 else 0 for i in smp.IsochronMark]),
                           index=[index for index, _ in enumerate(smp.IsochronMark) if _ == 1]),
            set2=ArArBasic(size=sum([1 if i == 2 else 0 for i in smp.IsochronMark]),
                           index=[index for index, _ in enumerate(smp.IsochronMark) if _ == 2]),
            unselected=ArArBasic(size=sum([0 if i == 2 or i == 1 else 1 for i in smp.IsochronMark]),
                                 index=[index for index, _ in enumerate(smp.IsochronMark) if _ != 1 and _ != 2]),
        )
    )


def get_results(smp: Sample):
    return ArArBasic(
        isochron=ArArBasic(**dict(
            ({'figure_2': 'normal', 'figure_3': 'inverse', 'figure_4': 'cl_1',
              'figure_5': 'cl_2', 'figure_6': 'cl_3', 'figure_7': 'three_d'}[key],
             ArArBasic(**dict(({2: 'unselected', 0: 'set1', 1: 'set2'}[_key],
                               ArArBasic(**_value)) for (_key, _value) in value.items())))
            for (key, value) in smp.Info.results.isochron.items())),
        age_plateau=ArArBasic(**dict(
            ({2: 'unselected', 0: 'set1', 1: 'set2'}[key], ArArBasic(**value))
            for (key, value) in smp.Info.results.age_plateau.items()))
    )

