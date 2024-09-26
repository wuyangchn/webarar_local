#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - files - xls
# ==========================================
#
#
#
"""
from xlrd import open_workbook, biffh


def open_xls(filepath: str):
    res = {}
    try:
        wb = open_workbook(filepath)
        for sheet_name in wb.sheet_names():
            sheet = wb.sheet_by_name(sheet_name)
            res[sheet_name] = [[sheet.cell(row, col).value for col in range(sheet.ncols)] for row in range(sheet.nrows)]
    except biffh.XLRDError as e:
        print('Error in opening excel file: %s' % str(e))
        return e
    else:
        return res

