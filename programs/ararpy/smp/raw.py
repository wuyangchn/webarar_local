#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang 
# ararpy - raw
# ==========================================
#
#
# 
"""
import os
import pandas as pd
from typing import List, Union, Optional
from types import MethodType
from ..calc import arr, raw_funcs
from ..files import raw_file
from ..files.basic import read as read_params
from . import (sample as samples)

RawData = samples.RawData
Sequence = samples.Sequence


def to_raw(file_path: Union[str, List[str]], input_filter_path: Union[str, List[str]], **kwargs):
    """ Read raw data from files, can create raw data instance based on the given files
    Raw data will have the structure like:
        [
            [ [ sequence 0 header ], [ measurement cycle 0 data ], [ measurement cycle 1 data ], ...  ],
            [ [ sequence 1 header ], [ measurement cycle 0 data ], [ measurement cycle 1 data ], ...  ],
            ...
            [ [ sequence n - 1 header ], [ measurement cycle 0 data ], [ measurement cycle 1 data ], ...  ],
        ]
    Parameters
    ----------
    file_path
    input_filter_path
    kwargs

    Returns
    -------

    """
    if isinstance(file_path, list) and isinstance(input_filter_path, list):
        raw = concatenate([to_raw(file, input_filter_path[index]) for index, file in enumerate(file_path)])
    elif isinstance(file_path, str) and isinstance(input_filter_path, str):
        input_filter = read_params(input_filter_path)
        file_name = str(os.path.split(file_path)[-1]).split('.')[0]
        res = raw_file.open_file(file_path, input_filter)
        data = res.get('data', None)
        sequences = res.get('sequences', None)
        sequence_num = len(data) if data is not None else len(sequences)
        raw = RawData(name=file_name, data=data, isotopic_num=10, sequence_num=sequence_num,
                      source=[file_path], sequence=sequences, unit=str(input_filter[30]))
    else:
        raise ValueError("File path and input filter should be both string or list with a same length.")
    return raw


def concatenate(raws: List[RawData]):
    """
    Parameters
    ----------
    raws

    Returns
    -------

    """
    step_names = []

    def resort_sequence(seq: Sequence, index):
        count = 0
        while seq.name in step_names:
            # rename
            if count == 0:
                seq.name = f"{seq.name}-{index + 1}"
            else:
                seq.name = f"{seq.name} ({count})"
            count = count + 1
        step_names.append(seq.name)
        seq.index = index
        seq.is_removed = hasattr(seq, "is_removed") and seq.is_removed is True
        return seq

    source = [_source for _raw in raws for _source in _raw.source]
    unit = set([_raw.unit for _raw in raws])
    unit = list(unit)[0] if len(unit) == 1 else 'Unknown Unit'
    sequence = [resort_sequence(seq, index) for index, seq in enumerate([i for _raw in raws for i in _raw.sequence])]
    sequence_num = len(sequence)
    exp_names = list(set([_raw.name for _raw in raws]))
    return RawData(name='&'.join(exp_names), source=source, isotopic_num=10,
                   sequence_num=sequence_num, sequence=sequence, unit=unit)


def get_sequence(raw: RawData, index: Optional[Union[list, int, str, bool]] = None,
                 flag: Optional[str] = None, unique: Optional[bool] = True):
    """
    Parameters
    ----------
    raw
    index :
        value
    flag :
        name of attribution to be matched of a sequence
    unique : bool, if True, will return the first matched sequence,
        False, return a list of all matched sequences

        a = raw.get_sequence(True, 'is_unknown', unique=False)  # get unknown sequence
        print([_a.name for _a in a])

    Returns
    -------

    """
    if index is None:
        return raw.sequence
    if isinstance(index, list):
        return [get_sequence(raw, i, flag) for i in index]
    # judge boolean before int
    if isinstance(index, (str, bool)) and flag is not None:
        return arr.filter(raw.sequence, lambda seq: getattr(seq, flag)() == index if type(
            getattr(seq, flag)) is MethodType else getattr(seq, flag) == index, unique=unique, get=None)
    if isinstance(index, int):
        return raw.sequence[index]


def do_regression(raw: RawData, sequence_index: Optional[List] = None, isotopic_index: Optional[List] = None):
    """
    Parameters
    ----------
    raw
    sequence_index
    isotopic_index

    Returns
    -------

    """

    for sequence in raw.get_sequence(index=None, flag=None):
        if hasattr(sequence_index, '__getitem__') and sequence.index not in sequence_index:
            continue
        isotope: pd.DataFrame = sequence.get_data_df()
        selected: pd.DataFrame = isotope[sequence.get_flag_df()[list(range(1, 11))]]
        # unselected: pd.DataFrame = isotope[~sequence.get_flag_df()[list(range(1, 11))]]
        selected: list = [selected[[isotopic_index * 2 + 1, 2 * (isotopic_index + 1)]].dropna().values.tolist()
                          for isotopic_index in list(range(5))]
        # unselected: list = [unselected[[isotopic_index*2 + 1, 2 * (isotopic_index + 1)]].dropna().values.tolist()
        #                     for isotopic_index in list(range(5))]

        for index, isotope in enumerate(selected):
            if hasattr(isotopic_index, '__getitem__') and index not in isotopic_index:
                continue
            # print(f"regression for {sequence.name = }, isotope {index = }")
            res = raw_funcs.get_raw_data_regression_results(isotope)
            try:
                sequence.results[index] = res[1]
                sequence.coefficients[index] = res[2]
            except IndexError:
                sequence.results.insert(index, res[1])
                sequence.coefficients.insert(index, res[2])
            except TypeError:
                sequence.results = [res[1]]
                sequence.coefficients = [res[2]]
