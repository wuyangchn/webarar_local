#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2024 Yang 
# webarar - test.py
# ==========================================
#
#
# 
"""


from typing import Union
from decimal import Decimal


def change_number_format(numbers: Union[list, tuple], flag: str = "Scientific", precision: int = None):
    """
    Parameters
    ----------
    precision
    flag
    numbers

    Returns
    -------

    """
    flag = flag.replace(" ", "")
    _precision = [len(str(num).split(".")[1]) if "." in str(num) else 0 for num in numbers]
    if flag.startswith("AddZero"):
        precision = max(_precision) if precision is None else precision
        for index, num in enumerate(numbers):
            numbers[index] = str(num) + ('.' if '.' not in str(num) else '') + '0' * (precision - _precision[index])
        return change_number_format(numbers, flag=flag.replace("AddZero", ""), precision=precision)

    if flag.startswith("Scientific"):
        numbers = [
            ("{:." + f"{(len(str(num).replace('.', '')) - 1) if precision is None else precision}" + "e}").format(
                Decimal(str(num))) for num in numbers]
        return change_number_format(numbers, flag=flag.replace("Scientific", ""), precision=precision)

    if flag.startswith("NonZero"):
        numbers = [str(num).rstrip("0") if "." in str(num) else str(num) for num in numbers]
        return change_number_format(numbers, flag=flag.replace("NonZero", ""), precision=precision)

    if flag.startswith("Round"):
        numbers = [str(round(float(num), min(_precision) if precision is None else precision)) for num in numbers]
        return change_number_format(numbers, flag=flag.replace("Round", ""), precision=precision)

    return numbers


if __name__ == '__main__':
    data = ["0.00", 400.03234, 800.0, 1200.0234, 1600.0, 2000.10]
    print(change_number_format(data, flag="Round AddZero  NonZeroScientific", precision=1))
    pass
