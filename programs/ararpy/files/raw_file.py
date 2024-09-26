#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# webarar - raw_file
# ==========================================
#
#
#
"""

from typing import List, Union
import traceback
import os
import re
import pickle
import chardet
from xlrd import open_workbook
from datetime import datetime
from parse import parse as string_parser
import dateutil.parser as datetime_parser
from ..calc.arr import get_item

""" Open raw data file """

DEFAULT_SAMPLE_INFO = {}


def open_file(file_path: str, input_filter: List[Union[str, int, bool]]):
    """
    Parameters
    ----------
    file_path:
    input_filter

    Returns
    -------
    step_list -> [[[header of step one], [cycle one in the step], [cycle two in the step]],[[],[]]]
        example:
            [
                [
                    [1, '6/8/2019  8:20:51 PM', 'BLK', 'B'],  # step header
                    # [sequence index, date time, label, value]
                    ['1', 12.30, 87.73, 12.30, 1.30, 12.30, 0.40, 12.30, 0.40, 12.30, 0.44],  # step/sequence 1
                    # [cycle index, time, Ar40 signal, time, Ar39 signal, ..., time, Ar36 signal]
                    ['2', 24.66, 87.70, 24.66, 1.14, 24.66, 0.36, 24.66, 0.35, 24.66, 0.43],  # step/sequence 2
                    ...
                    ['10', 123.06, 22262.68, 123.06, 6.54, 123.06, 8.29, 123.06, 0.28, 123.06, 29.22],
                ],
                [
                    ...
                ]
            ]

    """
    extension = str(os.path.split(file_path)[-1]).split('.')[-1]
    try:
        handler = {'txt': open_raw_txt, 'excel': open_raw_xls,
                   'Qtegra Exported XLS': open_qtegra_exported_xls, 'Seq': open_raw_seq}[
            ['txt', 'excel', 'Qtegra Exported XLS', 'Seq'][int(input_filter[1])]]
    except KeyError:
        print(traceback.format_exc())
        raise FileNotFoundError("Wrong File.")
    return handler(file_path, input_filter)


def open_qtegra_exported_xls(filepath, input_filter=None):
    if input_filter is None:
        input_filter = []
    try:
        wb = open_workbook(filepath)
        sheets = wb.sheet_names()
        sheet = wb.sheet_by_name(sheets[0])
        value, step_header, step_list = [], [], []
        for row in range(sheet.nrows):
            row_set = []
            for col in range(sheet.ncols):
                if sheet.cell(row, col).value == '':
                    pass
                else:
                    row_set.append(sheet.cell(row, col).value)
            if row_set != [] and len(row_set) > 1:
                value.append(row_set)
        for each_row in value:
            # if the first item of each row is float (1.0, 2.0, ...) this row is the header of a step.
            if isinstance(each_row[0], float):
                each_row[0] = int(each_row[0])
                if "M" in each_row[1].upper():
                    each_row[1] = datetime.strptime(each_row[1], '%m/%d/%Y  %I:%M:%S %p').isoformat(timespec='seconds')
                else:
                    each_row[1] = datetime.strptime(each_row[1], '%m/%d/%Y  %H:%M:%S').isoformat(timespec='seconds')
                step_header.append(each_row)
        for step_index, each_step_header in enumerate(step_header):
            row_start_number = value.index(each_step_header)
            try:
                row_stop_number = value.index(step_header[step_index + 1])
            except IndexError:
                row_stop_number = len(value) + 1
            step_values = [
                each_step_header[0:4],
                *list(map(
                    # lambda x: [x[0], x[1], x[2], x[1], x[3], x[1], x[4], x[1], x[5], x[1], x[6]],
                    # x[1] = time, x[2] = H2:40, x[3] = H1: 39, x[4] = AX: 38, x[5] = L1: 37, x[6] = L2: 36
                    lambda x: [x[0], x[1], x[6], x[1], x[5], x[1], x[4], x[1], x[3], x[1], x[2]],
                    # in sequence: Ar36, Ar37, Ar38, Ar39, Ar40
                    [value[i] for i in range(row_start_number + 2, row_stop_number - 7, 1)]))
            ]
            step_list.append(step_values)
    except Exception as e:
        raise ValueError('Error in opening the original file: %s' % str(e))
    else:
        return {'data': step_list}


def open_raw_txt(file_path, input_filter: List[Union[str, int]]):
    """
    Parameters
    ----------
    input_filter
    file_path

    Returns
    -------

    """
    if not input_filter:
        raise ValueError("Input filter is empty array.")

    if os.path.splitext(file_path)[1][1:].lower() != input_filter[0].strip().lower():
        raise ValueError("The file does not comply with the extension in the given filter.")

    with open(file_path, 'rb') as f:
        contents = f.read()
        encoding = chardet.detect(contents)
        lines = [line.strip().split(['\t', ';', " ", ",", input_filter[3]][int(input_filter[2])])
                 for line in contents.decode(encoding=encoding["encoding"]).split('\r\n')]

    file_name = os.path.basename(file_path).rstrip(os.path.splitext(file_path)[-1])
    step_list = get_raw_data([lines], input_filter, file_name=file_name)
    return {'data': step_list}


def open_raw_xls(file_path, input_filter: List[Union[str, int]]):
    """
    Parameters
    ----------
    file_path
    input_filter

    Returns
    -------

    """
    if not input_filter:
        raise ValueError("Input filter is empty array.")

    if os.path.splitext(file_path)[1][1:].lower() != input_filter[0].strip().lower():
        raise ValueError("The file does not comply with the extension in the given filter.")

    def _get_content_from_sheet(_index) -> List[List[Union[str, bool, int, float]]]:
        _sheet = wb.sheet_by_index(_index)
        return [[_sheet.cell(_row, _col).value for _col in range(_sheet.ncols)] for _row in range(_sheet.nrows)]

    wb = open_workbook(file_path)
    used_sheet_index = set([input_filter[i] - 1 if input_filter[i] != 0 else 0 for i in
                            [4, 36, 39, 42, 45, 48, 51, 54, 57, 60, 63, 66, 69, 72, 75, 78, 81, 84, 87,
                             90, 93, 96, 99, 102, 105, 108, 111, 114, 117, 120, 123, 126, 129]])
    contents = [[] if i not in used_sheet_index else _get_content_from_sheet(i)
                for i in range(max(used_sheet_index) + 1)]

    file_name = os.path.basename(file_path).rstrip(os.path.splitext(file_path)[-1])
    step_list = get_raw_data(contents, input_filter, file_name=file_name)

    return {'data': step_list}


def open_raw_seq(file_path, input_filter=None):
    with open(file_path, 'rb') as f:
        sequences = pickle.load(f)
    name_list = []
    for seq in sequences:
        while seq.name in name_list:
            seq.name = f"{seq.name}-{seq.index}"
        name_list.append(seq.name)

    return {'sequences': sequences}


def get_raw_data(file_contents: List[List[Union[int, float, str, bool, list]]], input_filter: list,
                 file_name: str = "") -> list:
    """
    Parameters
    ----------
    file_name
    file_contents
    input_filter

    Returns
    -------

    """

    def datetime_parse(string, format):
        try:
            return datetime.strptime(string, format)
        except ValueError as v:
            if len(v.args) > 0 and v.args[0].startswith('unconverted data remains: '):
                string = string[:-(len(v.args[0]) - 26)]
                return datetime.strptime(string, format)
            else:
                raise

    step_list = []
    idx = step_index = 0

    header = input_filter[5]
    sample_info_index = input_filter[33:64]
    isotopic_data_index = input_filter[8:28]

    while True:
        # Zero datetime
        try:
            if input_filter[134]:  # input_filter[134]: date in one string
                if sample_info_index[1].strip() != "":
                    zero_date = datetime_parse(
                        get_item(file_contents, sample_info_index[15:18], base=[1, 1 - idx, 1]), sample_info_index[1])
                else:
                    zero_date = datetime_parser.parse(get_item(file_contents, sample_info_index[15:18], base=[1, 1 - idx, 1]))
            else:
                zero_date = datetime(year=get_item(file_contents, sample_info_index[15:18], base=1),
                                     month=get_item(file_contents, sample_info_index[21:24], base=[1, 1 - idx, 1]),
                                     day=get_item(file_contents, sample_info_index[27:30], base=[1, 1 - idx, 1]))

            if input_filter[135]:  # input_filter[135]: time in one string
                if sample_info_index[2].strip() != "":
                    zero_time = datetime_parse(
                        get_item(file_contents, sample_info_index[18:21], base=[1, 1 - idx, 1]), sample_info_index[2])
                else:
                    zero_time = datetime_parser.parse(get_item(file_contents, sample_info_index[18:21], base=[1, 1 - idx, 1]))
            else:
                zero_time = datetime(year=2020, month=12, day=31,
                                     hour=get_item(file_contents, sample_info_index[18:21], base=[1, 1 - idx, 1]),
                                     minute=get_item(file_contents, sample_info_index[24:27], base=[1, 1 - idx, 1]),
                                     second=get_item(file_contents, sample_info_index[30:33], base=[1, 1 - idx, 1]))

            zero_datetime = datetime(zero_date.year, zero_date.month, zero_date.day, zero_time.hour,
                                 zero_time.minute, zero_time.second).isoformat(timespec='seconds')
        except (TypeError, ValueError, IndexError):
            # print(f"Cannot parse zero datetime")
            zero_datetime = datetime(1949, 10, 1, 10, 0, 0).isoformat(timespec='seconds')

        # Experiment name
        try:
            experiment_name = get_item(file_contents, sample_info_index[3:6], default="", base=[1, 1 - idx, 1]) if input_filter[4] > 0 else ""
        except (TypeError, ValueError, IndexError):
            # print(f"Cannot parse experiment name")
            experiment_name = "ExpNameError"

        # Step name
        try:
            step_name = get_item(file_contents, sample_info_index[6:9], default="", base=[1, 1 - idx, 1]) if input_filter[7] > 0 else ""
            if input_filter[133] and sample_info_index[0] != "":
                _res = string_parser(sample_info_index[0], file_name)
                if _res is not None:
                    experiment_name = _res.named.get("en", experiment_name)
                    step_index = _res.named.get("sn", step_name)
                    if step_index.isnumeric():
                        step_name = f"{experiment_name}-{int(step_index):02d}"
                    else:
                        step_name = f"{experiment_name}-{step_index}"
            if step_name == "":
                raise ValueError(f"Step name not found")
        except (TypeError, ValueError, IndexError):
            # When parsing the step name fails, the end of the file has been reached
            break

        # other information
        options = get_sample_info(file_contents, input_filter, default="", base=[1, 1 - idx, 1])

        current_step = [[step_name, zero_datetime, experiment_name, options]]

        break_num = 0
        cycle_num = 0
        f = float(input_filter[31])
        data_content = file_contents[input_filter[4] - 1 if input_filter[4] != 0 else 0]
        for i in range(2000):
            if break_num < input_filter[29]:
                break_num += 1
                continue
            break_num = 0
            if int(input_filter[6]) == 0:  # == 0, vertical
                start_row = input_filter[28] * cycle_num + input_filter[29] * cycle_num + header + idx - 1
                try:
                    current_step.append([
                        str(cycle_num + 1),
                        # in sequence: Ar36, Ar37, Ar38, Ar39, Ar40
                        float(data_content[start_row + isotopic_data_index[18]][isotopic_data_index[19] - 1]),
                        float(data_content[start_row + isotopic_data_index[16]][isotopic_data_index[17] - 1]) * f,
                        float(data_content[start_row + isotopic_data_index[14]][isotopic_data_index[15] - 1]),
                        float(data_content[start_row + isotopic_data_index[12]][isotopic_data_index[13] - 1]) * f,
                        float(data_content[start_row + isotopic_data_index[10]][isotopic_data_index[11] - 1]),
                        float(data_content[start_row + isotopic_data_index[ 8]][isotopic_data_index[ 9] - 1]) * f,
                        float(data_content[start_row + isotopic_data_index[ 6]][isotopic_data_index[ 7] - 1]),
                        float(data_content[start_row + isotopic_data_index[ 4]][isotopic_data_index[ 5] - 1]) * f,
                        float(data_content[start_row + isotopic_data_index[ 2]][isotopic_data_index[ 3] - 1]),
                        float(data_content[start_row + isotopic_data_index[ 0]][isotopic_data_index[ 1] - 1]) * f,
                    ])
                except (ValueError, IndexError):
                    # print(f"Cannot parse isotope data")
                    current_step.append([
                        str(cycle_num + 1), None, None, None, None, None, None, None, None, None, None,
                    ])
            elif int(input_filter[6]) == 1:  # == 1, horizontal
                start_row = input_filter[5] + idx
                col_inc = input_filter[28] * cycle_num + input_filter[29] * cycle_num - 1
                try:
                    current_step.append([
                        str(cycle_num + 1),
                        # Ar36, Ar37, Ar38, Ar39, Ar40
                        float(data_content[start_row][isotopic_data_index[19] + col_inc]),
                        float(data_content[start_row][isotopic_data_index[17] + col_inc]) * f,
                        float(data_content[start_row][isotopic_data_index[15] + col_inc]),
                        float(data_content[start_row][isotopic_data_index[13] + col_inc]) * f,
                        float(data_content[start_row][isotopic_data_index[11] + col_inc]),
                        float(data_content[start_row][isotopic_data_index[ 9] + col_inc]) * f,
                        float(data_content[start_row][isotopic_data_index[ 7] + col_inc]),
                        float(data_content[start_row][isotopic_data_index[ 5] + col_inc]) * f,
                        float(data_content[start_row][isotopic_data_index[ 3] + col_inc]),
                        float(data_content[start_row][isotopic_data_index[ 1] + col_inc]) * f,
                    ])
                except (ValueError, IndexError):
                    # print(f"Cannot parse isotope data")
                    current_step.append([
                        str(cycle_num + 1), None, None, None, None, None, None, None, None, None, None,
                    ])
            else:
                raise ValueError(f"{input_filter[6]} not in [0, 1]")

            cycle_num += 1
            if cycle_num >= input_filter[7]:
                break

        step_list.append(current_step)
        step_index += 1
        idx = input_filter[32] * step_index

        if not input_filter[132] or step_index >= 500:  # input_filter[132]: multiple sequences
            break

    return step_list


def get_sample_info(file_contents: list, input_filter: list, default="", base=1) -> dict:
    """
    Parameters
    ----------
    file_contents
    input_filter
    default
    base

    Returns
    -------

    """
    sample_info_index = input_filter[36:132]
    sample_info = DEFAULT_SAMPLE_INFO.copy()
    sample_info.update({
        "ExpName": get_item(file_contents, sample_info_index[0:3], default=default, base=base),
        "StepName": get_item(file_contents, sample_info_index[3:6], default=default, base=base),
        "SmpType": get_item(file_contents, sample_info_index[6:9], default=default, base=base),
        "StepLabel": get_item(file_contents, sample_info_index[9:12], default=default, base=base),
        "ZeroYear": get_item(file_contents, sample_info_index[12:15], default=default, base=base),  # year
        "ZeroHour": get_item(file_contents, sample_info_index[15:18], default=default, base=base),  # hour
        "ZeroMon": get_item(file_contents, sample_info_index[18:21], default=default, base=base),  # month
        "ZeroMin": get_item(file_contents, sample_info_index[21:24], default=default, base=base),  # minute
        "ZeroDay": get_item(file_contents, sample_info_index[24:27], default=default, base=base),  # day
        "ZeroSec": get_item(file_contents, sample_info_index[27:30], default=default, base=base),  # second
        "SmpName": get_item(file_contents, sample_info_index[30:33], default=default, base=base),
        "SmpLoc": get_item(file_contents, sample_info_index[33:36], default=default, base=base),
        "SmpMatr": get_item(file_contents, sample_info_index[36:39], default=default, base=base),
        "ExpType": get_item(file_contents, sample_info_index[39:42], default=default, base=base),
        "SmpWeight": get_item(file_contents, sample_info_index[42:45], default=default, base=base),
        "Stepunit": get_item(file_contents, sample_info_index[45:48], default=default, base=base),
        "HeatingTime": get_item(file_contents, sample_info_index[48:51], default=default, base=base),
        "InstrName": get_item(file_contents, sample_info_index[51:54], default=default, base=base),
        "Researcher": get_item(file_contents, sample_info_index[54:57], default=default, base=base),
        "Analyst": get_item(file_contents, sample_info_index[57:60], default=default, base=base),
        "Lab": get_item(file_contents, sample_info_index[60:63], default=default, base=base),
        "Jv": get_item(file_contents, sample_info_index[63:66], default=default, base=base),
        "Jsig": get_item(file_contents, sample_info_index[66:69], default=default, base=base),
        "CalcName": get_item(file_contents, sample_info_index[69:72], default=default, base=base),
        "IrraName": get_item(file_contents, sample_info_index[72:75], default=default, base=base),
        "IrraLabel": get_item(file_contents, sample_info_index[75:78], default=default, base=base),
        "IrraPosH": get_item(file_contents, sample_info_index[78:81], default=default, base=base),
        "IrraPosX": get_item(file_contents, sample_info_index[81:84], default=default, base=base),
        "IrraPosY": get_item(file_contents, sample_info_index[84:87], default=default, base=base),
        "StdName": get_item(file_contents, sample_info_index[87:90], default=default, base=base),
        "StdAge": get_item(file_contents, sample_info_index[90:93], default=default, base=base),
        "StdAgeSig": get_item(file_contents, sample_info_index[93:96], default=default, base=base),
        # "Experiment Name": get_item(file_contents, sample_info_index[0:3], default=default, base=base),
        # "Step Name": get_item(file_contents, sample_info_index[3:6], default=default, base=base),
        # "Sample Type": get_item(file_contents, sample_info_index[6:9], default=default, base=base),
        # "Step Label": get_item(file_contents, sample_info_index[9:12], default=default, base=base),
        # "Zero Date Year": get_item(file_contents, sample_info_index[12:15], default=default, base=base),
        # "Zero Time Hour": get_item(file_contents, sample_info_index[15:18], default=default, base=base),
        # "Zero Date Month": get_item(file_contents, sample_info_index[18:21], default=default, base=base),
        # "Zero Time Minute": get_item(file_contents, sample_info_index[21:24], default=default, base=base),
        # "Zero Date Day": get_item(file_contents, sample_info_index[24:27], default=default, base=base),
        # "Zero Time Second": get_item(file_contents, sample_info_index[27:30], default=default, base=base),
        # "Sample Name": get_item(file_contents, sample_info_index[30:33], default=default, base=base),
        # "Sample location": get_item(file_contents, sample_info_index[33:36], default=default, base=base),
        # "Sample Material": get_item(file_contents, sample_info_index[36:39], default=default, base=base),
        # "Experiment Type": get_item(file_contents, sample_info_index[39:42], default=default, base=base),
        # "Sample Weight": get_item(file_contents, sample_info_index[42:45], default=default, base=base),
        # "Step unit": get_item(file_contents, sample_info_index[45:48], default=default, base=base),
        # "Heating time": get_item(file_contents, sample_info_index[48:51], default=default, base=base),
        # "Instrument name": get_item(file_contents, sample_info_index[51:54], default=default, base=base),
        # "Researcher": get_item(file_contents, sample_info_index[54:57], default=default, base=base),
        # "Analyst": get_item(file_contents, sample_info_index[57:60], default=default, base=base),
        # "Laboratory": get_item(file_contents, sample_info_index[60:63], default=default, base=base),
        # "J value": get_item(file_contents, sample_info_index[63:66], default=default, base=base),
        # "J value error": get_item(file_contents, sample_info_index[66:69], default=default, base=base),
        # "Calc params": get_item(file_contents, sample_info_index[69:72], default=default, base=base),
        # "Irra name": get_item(file_contents, sample_info_index[72:75], default=default, base=base),
        # "Irra label": get_item(file_contents, sample_info_index[75:78], default=default, base=base),
        # "Irra position H": get_item(file_contents, sample_info_index[78:81], default=default, base=base),
        # "Irra position X": get_item(file_contents, sample_info_index[81:84], default=default, base=base),
        # "Irra position Y": get_item(file_contents, sample_info_index[84:87], default=default, base=base),
        # "Standard name": get_item(file_contents, sample_info_index[87:90], default=default, base=base),
        # "Standard age": get_item(file_contents, sample_info_index[90:93], default=default, base=base),
        # "Standard age error": get_item(file_contents, sample_info_index[93:96], default=default, base=base),
    })
    return sample_info
