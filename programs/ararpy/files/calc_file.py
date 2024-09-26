
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - files - calc_file
# ==========================================

Open age files from ArArCALC. It currently supports version: 25.2 and 24.0.
Version 25.2 is preferred to 24.0 as containing more detailed parameters than 24.0.

ArArCalcFile(file_path, file_name: optional)
    -> open()
        -> get content and sample info ()

"""
import traceback
import pandas as pd
import numpy as np
import re
from xlrd import open_workbook, biffh
import os
import msoffcrypto

from . import xls
from ..calc.basic import get_datetime
from ..calc import arr, err, isochron


def read_calc_file(file_path: str):
    """
    :param file_path: file with suffix of .age or .air
    :return: dict, keys are sheet name, value are list of [[col 0], [col 1], ...] of corresponding sheet
    """
    decrypt_file_path = file_path + '_decrypt.xls'
    try:
        with open(file_path, 'rb') as file:
            office_file = msoffcrypto.OfficeFile(file)
            office_file.load_key(password=bytes.fromhex(
                open(os.path.join(os.path.dirname(__file__), '../../conf.txt'), "r").read()).decode())
            office_file.decrypt(open(decrypt_file_path, 'wb'))
        wb = open_workbook(decrypt_file_path)
        worksheets = wb.sheet_names()
        book_contents = dict()
        for each_sheet in worksheets:
            sheet = wb.sheet_by_name(each_sheet)
            sheet_contents = [
                [sheet.cell(row, col).value for col in range(sheet.ncols)]
                for row in range(sheet.nrows)
            ]
            book_contents[each_sheet] = sheet_contents
        os.remove(decrypt_file_path)
    except Exception as e:
        print(traceback.format_exc())
        return False
    else:
        return book_contents


def open_252(data: pd.DataFrame, logs01: pd.DataFrame, logs02: pd.DataFrame):
    """
    Open 25.2 version ArArCALC files
    :param data:
    :param logs01:
    :param logs02:
    :return:
    """
    # add default columns for 999, -999, and -1 index
    data[-999] = [0] * data.index.size
    data[999] = [1] * data.index.size
    data[-1] = [np.nan] * data.index.size
    # rows_unm --> 样品阶段数
    sequence_index = [1, 2, ]
    sample_values_index = [16, 17, 21, 22, 26, 27, 31, 32, 36, 37,]
    blank_values_index = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12,]
    corrected_values_index = [
        188, 189, 190, 191, 192, 193, 194, 195, 196, 197,]
    degas_values_index = [
        138, 139, 140, 141, 142, 143, 144, 145,  # 36 a, c, ca, cl    0-9
        146, 147,  # 37 ca    10-11
        156, 157, 148, 149, 150, 151, 152, 153, 154, 155,  # 38 cl, a, c, k, ca   12-21
        158, 159, 160, 161,  # 39 k, ca    22-25
        162, 163, 164, 165, 166, 167, 168, 169,  # 40 r, a, c, k    26-33
    ]
    publish_values_index = [
        101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
    ]
    apparent_age_values_index = [
        198, 199, 200, 201, -999, -999, 202, 203,  # f, sf, ages, s, s, s, 40Arr%, 39Ar%
    ]
    isochron_values_index = [
        116, 117, 118, 119, 122,  # normal isochron
        -1, 127, 128, 129, 130, 133,  # inverse
        -1, -999, -999, -999, -999, -999,  # 39/38 vs 40/38
        -1, -999, -999, -999, -999, -999,  # 39/40 vs 39/40
        -1, -999, -999, -999, -999, -999,  # 38/39 vs 40/39
        -1, -999, -999, -999, -999, -999, -999, -999, -999, -999,  # 3D isochron, 36/39, 38/39, 40/39
    ]
    isochron_mark_index = [115,]
    total_param_index = [
        71, 72, 73, 74, 75, 76, 77, 78, 79, 80,  # 0-9
        81, 82, 83, 84, 85, 86, 87, 88, 89, 90,  # 10-19
        91, 92, 93, 94, 95, 96, -999, -999, 63, -999,  # 20-29
        -999, -999, -1, -1, -999, -999, -999, -999, -999, -999,  # 30-39
        -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,  # 40-49
        -999, -999, -999, -999, -999, -999, -999, -999, 67, 49,  # 50-59
        50, -999, -999, -999, -999, -999, -999, 51, 52, 53,  # 60-69
        54, -999, -999, -999, -999, -999, -999, -999, -999, -999,  # 70-79
        -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,  # 80-89
        -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,  # 90-99
        -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,  # 100-109
        -999, -999, -999, -999, -1,  # 110-114
        -999, -999, -999, -999, -999, -999, -999, -999,  # 115-122
    ]

    # double transpose to remove keys
    get_data = lambda df, index: pd.concat([df[index].transpose()], ignore_index=True).transpose()

    sample_values = get_data(data, sample_values_index)
    blank_values = get_data(data, blank_values_index)
    corrected_values = get_data(data, corrected_values_index)
    degas_values = get_data(data, degas_values_index)
    publish_values = get_data(data, publish_values_index)
    apparent_age_values = get_data(data, apparent_age_values_index)
    isochron_values = get_data(data, isochron_values_index)
    total_param = get_data(data, total_param_index)
    isochron_mark = get_data(data, isochron_mark_index)
    sequence = get_data(data, sequence_index)

    # adjustment
    isochron_mark.replace({4.0: 1}, inplace=True)
    total_param[83] = logs01[1][9]  # No
    total_param[84] = logs01[1][10]  # %SD
    total_param[81] = logs01[1][11]  # K mass
    total_param[82] = logs01[1][12]  # K mass %SD

    total_param[85] = logs01[1][13]  # How many seconds in a year
    total_param[86] = 0  # %SD

    total_param[87] = logs01[1][14]  # The constant of 40K/K
    total_param[88] = logs01[1][15]  # %SD

    total_param[89] = logs01[1][16]  # The constant of 35Cl/37Cl
    total_param[90] = logs01[1][17]  # %SD
    total_param[56] = logs01[1][18]  # The constant of 36/38Cl productivity
    total_param[57] = logs01[1][19]  # %SD
    total_param[91] = logs01[1][24]  # The constant of HCl/Cl
    total_param[92] = logs01[1][25]  # %SD

    total_param[50] = logs01[1][26]  # 40K(EC) activities param
    total_param[51] = logs01[1][27]  # %SD
    total_param[52] = logs01[1][28]  # 40K(\beta-) activities param
    total_param[53] = logs01[1][29]  # %SD
    total_param[48] = logs01[1][26] + logs01[1][28]  # 40K(EC) activities param
    total_param[49] = 100 / total_param[48] * pow(
        (logs01[1][27] / 100 * logs01[1][26]) ** 2 + (logs01[1][29] / 100 * logs01[1][28]) ** 2, 0.5)  # %SD

    total_param[34] = logs01[1][36]  # decay constant of 40K total
    total_param[35] = logs01[1][37]  # %SD
    total_param[36] = logs01[1][30]  # decay constant of 40K EC
    total_param[37] = logs01[1][31]  # %SD
    total_param[38] = logs01[1][32]  # decay constant of 40K \beta-
    total_param[39] = logs01[1][33]  # %SD
    total_param[40] = 0  # decay constant of 40K \beta+
    total_param[41] = 0  # %SD
    total_param[46] = logs01[1][34]  # decay constant of 36Cl
    total_param[47] = logs01[1][35]  # %SD
    total_param[42] = logs01[1][38]  # decay constant of 39Ar
    total_param[43] = logs01[1][39]  # %SD
    total_param[44] = logs01[1][40]  # decay constant of 37Ar
    total_param[45] = logs01[1][41]  # %SD

    # logs01[1][49]]  # 1 for using weighted YORK isochron regression, 2 for unweighted
    # logs01[1][50]]  # True for including errors on irradiation constants, False for excluding those
    # [logs01[1][67]]  # MDF method, 'LIN'
    total_param[93] = logs01[1][70]  # 40Ar/36Ar air
    total_param[94] = logs01[1][71]  # %SD

    total_param[97] = 'York-2'  # Fitting method
    total_param[98] = logs01[1][0]  # Convergence
    total_param[99] = logs01[1][1]  # Iterations number
    total_param[100] = logs01[1][67]  # MDF method
    total_param[101] = logs01[1][65]  # force negative to zero when correct blank
    total_param[102] = True  # Apply 37Ar decay
    total_param[103] = True  # Apply 39Ar decay
    total_param[104] = logs01[1][6]  # Apply 37Ar decay
    total_param[105] = logs01[1][7]  # Apply 39Ar decay
    total_param[106] = True  # Apply K degas
    total_param[107] = True  # Apply Ca degas
    total_param[108] = True  # Apply Air degas
    total_param[109] = logs01[1][8]  # Apply Cl degas

    total_param[110] = True if logs01[1][5] == 'MIN' else False  # Calculating ages using Min equation [True] or conventional equation [False]
    total_param[111] = logs01[1][89]  # Use primary standard or not
    total_param[112] = logs01[1][91]  # Use standard age or not
    total_param[113] = logs01[1][92]  # Use primary ratio or not

    # irradiation time
    total_param = general_adjustment(
        total_param.copy(), logs02, get_data(data, [59, 58, 57, 60, 61]), data[63][0]
    )
    return [
        sample_values, blank_values, corrected_values, degas_values, publish_values,
        apparent_age_values, isochron_values, total_param, isochron_mark,
        sequence,
    ]


def open_240(data: pd.DataFrame, logs01: pd.DataFrame, logs02: pd.DataFrame):
    """
    Open 24.0 version ArArCALC files
    :param data:
    :param logs01:
    :param logs02:
    :return:
    """
    # add default columns for 999, -999, and -1 index
    data[-999] = [0] * data.index.size
    data[999] = [1] * data.index.size
    data[-1] = [np.nan] * data.index.size
    # values index
    sequence_index = [1, 2, ]
    sample_values_index = [16, 17, 21, 22, 26, 27, 31, 32, 36, 37,]
    blank_values_index = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12,]
    corrected_values_index = [
        -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,]
    degas_values_index = [
        # 36 a, c, ca, cl
        136, -999, 137, -999, 139, -999, 138, -999,
        # 37 ca,
        140, -999,
        # 38 cl, a, c, k, ca,
        145, -999, 141, -999, 142, -999, 143, -999, 144, -999,
        # 39 k, ca
        146, -999, 147, -999,
        # 40 r, a, c, k
        148, -999, 149, -999, 150, -999, 151, -999,
    ]
    publish_values_index = [
        99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
    ]
    apparent_age_values_index = [
        # f, sf, ages, s, s, s, 39Ar%
        156, 157, 104, 105, -999, -999, 106, 107,
    ]
    isochron_values_index = [
        # normal isochron
        114, 115, 116, 117, 120,
        # inverse
        -1, 125, 126, 127, 128, 131,
        # 39/38 vs 40/38
        -1, -999, -999, -999, -999, -999,
        # 39/40 vs 39/40
        -1, -999, -999, -999, -999, -999,
        # 38/39 vs 40/39
        -1, -999, -999, -999, -999, -999,
        # 3D isochron, 36/39, 38/39, 40/39, r1, r2, r3
        -1, -999, -999, -999, -999, -999, -999, -999, -999, -999,
    ]
    isochron_mark_index = [113,]
    total_param_index = [
        # 0-9
        69, 70, 71, 72, 73, 74, 75, 76, 77, 78,
        # 10-19
        79, 80, 81, 82, 83, 84, 85, 86, 87, 88,
        # 20-29
        89, 90, 91, 92, 93, 94, -999, -999, 63, -999,
        # 30-39
        -999, -999, -1, -1, -999, -999, -999, -999, -999, -999,
        # 40-49
        -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,
        # 50-59
        -999, -999, -999, -999, -999, -999, -999, -999, 65, 49,
        # 60-69
        50, -999, -999, -999, -999, -999, -999, 51, 52, 53,
        # 70-79
        54, -999, -999, -999, -999, -999, -999, -999, -999, -999,
        # 80-89
        -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,
        # 90-99
        -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,
        # 100-99909
        -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,
        # 110-114
        -999, -999, -999, -999, -1,
        # 115-122
        -999, -999, -999, -999, -999, -999, -999, -999,
    ]

    # double transpose to remove keys
    get_data = lambda df, index: pd.concat([df[index].transpose()], ignore_index=True).transpose()

    sample_values = get_data(data, sample_values_index)
    blank_values = get_data(data, blank_values_index)
    corrected_values = get_data(data, corrected_values_index)
    degas_values = get_data(data, degas_values_index)
    publish_values = get_data(data, publish_values_index)
    apparent_age_values = get_data(data, apparent_age_values_index)
    isochron_values = get_data(data, isochron_values_index)
    total_param = get_data(data, total_param_index)
    isochron_mark = get_data(data, isochron_mark_index)
    sequence = get_data(data, sequence_index)

    # irradiation time
    total_param = general_adjustment(
        total_param.copy(), logs02, get_data(data, [59, 58, 57, 60, 61]), data[63][0]
    )
    # Do adjustment
    isochron_mark.replace({4.0: 1}, inplace=True)
    total_param[44] = logs01[1][40]
    total_param[45] = logs01[1][41]
    total_param[42] = logs01[1][38]
    total_param[43] = logs01[1][39]
    total_param[34] = logs01[1][36]
    total_param[35] = logs01[1][37]

    return [
        sample_values, blank_values, corrected_values, degas_values, publish_values,
        apparent_age_values, isochron_values, total_param, isochron_mark,
        sequence,
    ]


def change_error_type(data: pd.DataFrame, header: pd.Series):
    """
    :param data: 2D DataFrame
    :param header: 1D Series, headers
    :return:
    """
    # 2 sigma to 1 sigma
    tochange = np.flatnonzero(header.where(header.str.contains('2s'), other=False))
    data[tochange.tolist()] = data[tochange.tolist()] / 2

    # percentage errors to absolute errors
    tochange = np.flatnonzero(header.where(header.str.contains('%1s|%2s', regex=True), other=False))
    data[tochange.tolist()] = \
        data[tochange.tolist()] * abs(data[(tochange - 1).tolist()].rename(lambda x: x + 1, axis='columns')) / 100

    return data


def general_adjustment(
        total_param: pd.DataFrame, logs02: pd.DataFrame, experimental_time: pd.DataFrame,
        irradiation_name: str
):
    """
        General handle for all age files, including set irradiaition time, initial ratios, error display
    :param total_param:
    :param logs02:
    :param experimental_time:
    :param irradiation_name:
    :return:
    """
    irra_project = pd.Series(logs02[1].copy())
    irradiation_index = np.flatnonzero(irra_project.where(irra_project.str.fullmatch(irradiation_name), other=False))[0]
    irradiation_info = logs02[32][irradiation_index].split('\n')
    # 处理辐照时间
    month_convert = {
        r'^(?i)Jan$': '01', r'^(?i)Feb$': '02', r'^(?i)Mar$': '03', r'^(?i)Apr$': '04', r'^(?i)May$': '05', r'^(?i)Jun$': '06',
        r'^(?i)Jul$': '07', r'^(?i)Aug$': '08', r'^(?i)Sep$': '09', r'^(?i)Oct$': '10', r'^(?i)Nov$': '11', r'^(?i)Dec$': '12'}
    duration_hour = []
    end_time_second = []
    irradiation_end_time = []
    last_time = []
    for each_date in irradiation_info:
        if '/' in each_date:
            _year = each_date.split(' ')[1].split('/')[2]
            _month = each_date.split(' ')[1].split('/')[1].capitalize()
            for pat, val in month_convert.items():
                if re.match(pat, _month):
                    _month = val
                    break
            _day = each_date.split(' ')[1].split('/')[0]
            _hour = each_date.split(' ')[2].split('.')[0]
            _min = each_date.split(' ')[2].split('.')[1]
            end_time_second.append(get_datetime(
                t_year=int(_year), t_month=int(_month), t_day=int(_day),
                t_hour=int(_hour), t_min=int(_min)))
            each_duration_hour = each_date.split(' ')[0].split('.')[0]
            each_duration_min = each_date.split(' ')[0].split('.')[1]
            each_duration = int(each_duration_hour) + round(int(each_duration_min) / 60, 2)
            duration_hour.append(each_duration)
            irradiation_end_time.append(f"{_year}-{_month}-{_day}T{_hour}:{_min}D{each_duration}")
            last_time = f"{_year}-{_month}-{_day}T{_hour}:{_min}"

    experimental_time: pd.DataFrame = experimental_time.apply(pd.to_numeric, errors='ignore', downcast='integer')
    experimental_time: pd.DataFrame = experimental_time.replace(to_replace=month_convert, regex=True)
    total_param[31] = [f"{i[0]}-{i[1]}-{i[2]}T{i[3]}:{i[4]}" for i in experimental_time.values.tolist()]
    total_param[26] = len(irradiation_end_time)
    total_param[27] = 'S'.join(irradiation_end_time)
    total_param[29] = sum(duration_hour)
    total_param[30] = last_time

    stand_time_second = [
        get_datetime(*i) - get_datetime(*re.findall(r'\d+', last_time)) for i in experimental_time.values.tolist()]
    total_param[32] = [i / (3600 * 24 * 365.242) for i in stand_time_second]  # stand year

    # initial ratios & error display settings
    total_param[115] = 0
    total_param[116] = 298.56
    total_param[117] = 0.31
    total_param[118] = 298.56
    total_param[119] = 0.31
    total_param[120] = 1
    total_param[121] = 1
    total_param[122] = 1

    return total_param


def open_full_xls(file_path: str, sample_name: str = ''):
    """
    filepath: absolute full path of input file
    return sample instance
    """
    try:
        res = xls.open_xls(file_path)
    except (Exception, BaseException) as e:
        return e
    start_row = 5
    rows_num = len(res['Sample Parameters']) - 5
    for key, val in res.items():
        res[key] = arr.transpose(val[:start_row + rows_num])
        # 2倍误差改回1倍
        for i in range(len(res[key])):
            if res[key][i][2] in ['2s', '%2s', '± 2s']:
                _temp = []
                for j in range(rows_num):
                    try:
                        _temp.append(res[key][i][start_row + j] / 2)
                    except TypeError:
                        _temp.append('')
                res[key][i][start_row: start_row + rows_num] = _temp
    if res['Incremental Heating Summary'][13][2] == 'K/Ca':
        _temp, _s = [], []
        for j in range(rows_num):
            try:
                _temp.append(1 / res['Relative Abundances'][13][start_row + j])
                _s.append(err.div((1, 0), (
                    res['Relative Abundances'][13][start_row + j], res['Relative Abundances'][14][start_row + j])))
            except TypeError:
                _temp.append(None)
                _s.append(None)
        res['Incremental Heating Summary'][13][start_row: start_row + rows_num] = _temp
        res['Incremental Heating Summary'][13][start_row: start_row + rows_num] = _s

    # degas相对误差改为绝对误差
    for i in range(len(res['Degassing Patterns'])):
        if res['Degassing Patterns'][i][2] in ['%1s', '%2s']:
            _temp = []
            for j in range(rows_num):
                try:
                    _temp.append(res['Degassing Patterns'][i][start_row + j] * res['Degassing Patterns'][i - 1][
                        start_row + j] / 100)
                except TypeError:
                    _temp.append('')
            res['Degassing Patterns'][i][start_row: start_row + rows_num] = _temp
    rows = list(range(start_row, rows_num))
    sequence_name = arr.partial(res['Procedure Blanks'], rows, 1)
    sequence_value = arr.partial(res['Procedure Blanks'], rows, 2)
    blank_values = arr.partial(
        res['Procedure Blanks'], rows, [3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    sample_values = arr.partial(
        res['Intercept Values'], rows, [3, 4, 8, 9, 13, 14, 18, 19, 23, 24])
    corrected_values = arr.partial(
        res['Relative Abundances'], rows, [4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
    degas_values = arr.partial(
        res['Degassing Patterns'], rows, [
            4, 5, 6, 7, 8, 9, 10, 11,
            12, 13,
            22, 23, 14, 15, 16, 17, 18, 19, 20, 21,
            24, 25, 26, 27,
            28, 29, 30, 31, 32, 33, 34, 35])
    publish_values = arr.partial(
        res['Incremental Heating Summary'], rows, [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
    apparent_age_values = arr.partial(
        res['Relative Abundances'], rows, [14, 15, 16, 17, -1, -1, 18, 19])
    isochron_values = [[np.nan] * len(rows)] * 39
    isochron_values[0:5] = arr.partial(
        res['Normal Isochron Table'], rows, [4, 5, 6, 7, 10])
    isochron_values[6:11] = arr.partial(
        res['Inverse Isochron Table'], rows, [4, 5, 6, 7, 10])
    total_param = arr.partial(
        res['Sample Parameters'], rows, [
            # 1, 2,  # 0-1
            -1, -1, -1, -1,  # 2-5
            -1, -1, -1, -1,  # 6-9
            -1, -1, -1, -1, -1, -1,  # 10-15
            -1, -1, -1, -1,  # 16-19
            -1, -1,  # 20-21
            23, 24, -1, -1, -1, -1,  # 22-27
            -1, -1,  # 28-29
            22, -1, -1, -1,  # 30-33
            -1, -1,  # 34-35
            -1, -1,  # 36-37
            -1, -1,  # 38-39
            -1, -1,  # 40-41
            -1, -1,  # 42-43
            -1, -1,  # 44-45
            -1, -1,  # 46-47
            -1, -1,  # 48-49
            -1, -1,  # 50-51
            -1, -1,  # 52-53
            -1, -1,  # 54-55
            -1, -1,  # 56-57
            -1, -1,  # 58-59
            -1, -1, -1, -1, -1, -1, -1, -1, -1,  # 60-68
            10, 11, 12, 13,  #
            -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  #
            -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  #
            -1, -1, -1, -1,  #
            -1, -1, -1, -1,  #
            -1, -1, -1, -1, -1,  #
            -1, -1, -1, -1,  #
            -1, -1, -1, -1,  #
            -1,  #
        ])

    month_convert = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                     'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
    experiment_start_time = []
    for i in arr.transpose(
            arr.partial(res['Sample Parameters'], rows, [18, 17, 16, 19, 20])):
        _year = str(i[0]) if '.' not in str(i[0]) else str(i[0]).split('.')[0]
        _month = str(month_convert[str(i[1]).capitalize()]) if str(i[1]).capitalize() in month_convert.keys() else str(
            i[1]).capitalize()
        _day = str(i[2]) if '.' not in str(i[2]) else str(i[2]).split('.')[0]
        _hour = str(i[3]) if '.' not in str(i[3]) else str(i[3]).split('.')[0]
        _min = str(i[4]) if '.' not in str(i[4]) else str(i[4]).split('.')[0]
        experiment_start_time.append(f"{_year}-{_month}-{_day}T{_hour}:{_min}")

    total_param[31] = experiment_start_time
    total_param[0:26] = arr.partial(
        res['Irradiation Constants'], rows,
        [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28])

    isochron_values[11] = [''] * len(isochron_values[0])
    isochron_values[17] = [''] * len(isochron_values[0])
    isochron_values[23] = [''] * len(isochron_values[0])
    isochron_values[12:17] = isochron.get_data(
        degas_values[20], degas_values[21], degas_values[24], degas_values[25], degas_values[10], degas_values[11]
    )  # 39/38, 40/38
    isochron_values[18:23] = isochron.get_data(
        degas_values[20], degas_values[21], degas_values[10], degas_values[11], degas_values[24], degas_values[25]
    )  # 39/40, 38/40
    isochron_values[24:29] = isochron.get_data(
        degas_values[10], degas_values[11], degas_values[24], degas_values[25], degas_values[20], degas_values[21]
    )  # 38/39, 40/39
    isochron_mark = [1 if i == 'P' else '' for i in arr.partial(
        res['Normal Isochron Table'], rows, 3)]

    sample_info = {
        'sample': {'name': sample_name, 'material': 'MATERIAL', 'location': 'LOCATION'},
        'researcher': {'name': 'RESEARCHER', 'addr': 'ADDRESS'},
        'laboratory': {'name': 'LABORATORY', 'addr': 'ADDRESS', 'analyst': 'ANALYST'}
    }

    res = [sample_values, blank_values, corrected_values, degas_values, publish_values,
           apparent_age_values, isochron_values, total_param, [isochron_mark],
           [sequence_name, sequence_value]]

    return dict(zip(['smp', 'blk', 'cor', 'deg', 'pub', 'age', 'iso', 'pam', 'mak', 'seq'], res)), sample_info


class ArArCalcFile:
    def __init__(self, file_path: str, sample_name: str = ""):
        self.file_path = file_path
        self.sample_name = sample_name
        self.supported_versions = ['25.2', '24.0']
        self.content = pd.DataFrame([])
        self.sample_info = {
            'sample': {'name': 'undefined', 'material': 'undefined',},
            'researcher': {'name': 'undefined'},
            'laboratory': {'name': 'undefined', 'analyst': 'undefined', 'info': 'undefined',}
        }

    def open(self):
        book_contents = read_calc_file(self.file_path)
        if not book_contents:
            raise ValueError('Fail to open the file')
        # create data frames for book values
        content = pd.DataFrame(book_contents['Data Tables'])
        logs01 = pd.DataFrame(book_contents['Logs01'])
        logs02 = pd.DataFrame(book_contents['Logs02'])
        logs03 = pd.DataFrame(book_contents['Logs03'])

        start_row = 5
        sequence_num = int(logs03[2][0])
        header = content.loc[2]
        data = pd.concat([content.loc[list(range(start_row, start_row + sequence_num))]], ignore_index=True).apply(
            pd.to_numeric, errors='ignore'
        )

        # check version
        version = logs03[3][0]
        if version == '25.2':
            handler = open_252
            material = data[45][0]
            analyst = data[47][0]
        elif version == '24.0':
            handler = open_240
            material = data[46][0]
            analyst = data[48][0]
        else:
            raise ValueError(f'non-supported version: {version}')

        # change error type, 2sigma to 1sigma..., relative errors to absolute errors
        data = change_error_type(data, header)
        # get full data frames
        # ['smp', 'blk', 'cor', 'deg', 'pub', 'age', 'iso', 'pam', 'inf', 'mak', 'seq',] are abbreviations for
        #     [sample_values, blank_values, corrected_values, degas_values, publish_values,
        #      apparent_age_values, isochron_values, total_param, sample_info, isochron_mark,
        #      sequence_name, sequence_value]
        self.content = pd.concat(
            handler(data.copy(), logs01, logs02), axis=1,
            keys=['smp', 'blk', 'cor', 'deg', 'pub', 'age', 'iso', 'pam', 'mak', 'seq', ],
        )

        # set error format for parameters, change to percentage
        # list(range(1, 26, 2)) irradiation correction constants
        # list(range(39, 58, 2)) decay constants
        # list(range(68, 97, 2)) J, MDF, other constants
        for column in list(range(1, 26, 2)) + list(range(68, 71, 2)):
            self.content.loc[:, ('pam', column)] = \
                (self.content['pam', column].astype("float") / (
                    self.content['pam', column - 1].astype("float")) * 100).replace(np.nan, 0)

        # sample info
        self.sample_info = {
            'sample': {
                'name': self.sample_name or data[44][0],
                'material': material, 'location': 'LOCATION'
            },
            'researcher': {'name': data[64][0]},
            'laboratory': {
                'name': logs01[1][44],
                'analyst': analyst,
                'info': '\n'.join([logs01[1][45], logs01[1][46], logs01[1][47]]),
            }
        }

        return self

    def get_content(self):
        return self.content

    def get_smp_info(self):
        return self.sample_info

    def get_df(self):
        return self.content

    def get_list(self):
        return self.content
