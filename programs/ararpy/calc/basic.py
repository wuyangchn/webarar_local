#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - calc - basic
# ==========================================
#
#
#
"""
import copy


def get_datetime(t_year: int, t_month: int, t_day: int, t_hour: int, t_min: int, t_seconds: int = 0, base=None):
    """
    :param t_year: int
    :param t_month: int
    :param t_day: int
    :param t_hour: int
    :param t_min: int
    :param t_seconds: int, default == 0
    :param base: base time [y, m, d, h, m]
    :return: seconds since 1970-1-1 8:00
    """
    t_year, t_month, t_day, t_hour, t_min, t_seconds = \
        int(t_year), int(t_month), int(t_day), int(t_hour), int(t_min), int(t_seconds)
    if base is None:
        base = [1970, 1, 1, 8, 0]
    base_year, base_mouth, base_day, base_hour, base_min = base
    if t_year % 4 == 0 and t_year % 100 != 0 or t_year % 400 == 0:
        days = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    delta_seconds = ((((t_year - base_year) * 365 + ((t_year + 1 - base_year) - (t_year + 1 - base_year) % 4) / 4 +
                       sum(days[base_mouth - 1:t_month - 1]) + t_day - base_day) * 24 + t_hour - base_hour) * 60 +
                     t_min - base_min) * 60 + t_seconds
    return delta_seconds


def merge_dicts(a: dict, b: dict):
    """
    a and b, two dictionary. Return updated a
        For example:
            a = {"1": 1, "2": {"1": 1, "2": 2, "3": 3, "5": {}, "6": [1, 2]}}
            b = {"1": 'b', "2": {"1": 'b', "2": 'b', "3": 'b', "4": 'b', "5": {"1": 'b'}, "6": [1, 2, 3]}}
            Will return {'1': 1, '2': {'1': 1, '2': 2, '3': 3, '5': {'1': 'b'}, '6': [1, 2], '4': 'b'}}
    """
    res = copy.deepcopy(a)
    for key, val in b.items():
        if key not in res.keys() and key.isnumeric():
            key = int(key)
        if key not in res.keys():
            res[key] = val
        elif isinstance(val, dict):
            res[key] = merge_dicts(res[key], val)
        else:
            continue
    return res


def update_dicts(a: dict, b: dict):
    """
    a and b, two dictionary. Return updated a
        For example:
            a = {"1": 1, "2": {"1": 1, "2": 2, "3": 3, "5": {}, "6": [1, 2]}}
            b = {"1": 'b', "2": {"1": 'b', "2": 'b', "3": 'b', "4": 'b', "5": {"1": 'b'}, "6": [1, 2, 3]}}
            Will return {'1': 'b', ...}
    """
    res = copy.deepcopy(a)
    for key, val in b.items():
        if key not in res.keys() and key.isnumeric():
            key = int(key)
        if key not in res.keys():
            res[key] = val
        elif isinstance(val, dict):
            res[key] = update_dicts(res[key], val)
        else:
            res[key] = val
    return res
