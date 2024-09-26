#  Copyright (C) 2024 Yang. - All Rights Reserved
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - __init__.py
# ==========================================
#
# ArArPy
#
"""

import pandas as pd
from . import calc, smp, files, test


""" Information """

name = 'ararpy'
version = '0.0.1.a4'
__version__ = version
full_version = version
last_update = '2024-01-04'

""" ArArPy Functions """

from_arr = smp.initial.from_arr_files
from_age = smp.initial.from_calc_files
from_full = smp.initial.from_full_files
from_raw = smp.initial.from_raw_files
from_empty = smp.initial.from_empty

save = lambda _smp, _path: files.arr_file.save(_path, _smp)

""" Classes """

Sample = smp.Sample
Table = smp.Table
Plot = smp.Plot
Set = smp.Set
Label = smp.Label
Axis = smp.Axis
Text = smp.Text
RawData = smp.RawData
Sequence = smp.Sequence
ArArBasic = smp.ArArBasic
ArArData = smp.ArArData

""" ArArData Functions """

ArArData.to_df = lambda _ad: pd.DataFrame(_ad.data, index=_ad.header).transpose()
ArArData.to_list = lambda _ad: _ad.data

""" Sample Class Methods """

Sample.name = smp.info.name
Sample.doi = lambda _smp: _smp.Doi
Sample.sample = lambda _smp: _smp.Info.sample
Sample.researcher = lambda _smp: _smp.Info.researcher
Sample.laboratory = lambda _smp: _smp.Info.laboratory

Sample.results = lambda _smp: smp.basic.get_results(_smp)
Sample.sequence = lambda _smp: smp.basic.get_sequence(_smp)

Sample.initial = smp.initial.initial
Sample.set_selection = lambda _smp, _index, _mark: smp.plots.set_selection(_smp, _index, _mark)
Sample.update_table = lambda _smp, _data, _id: smp.table.update_handsontable(_smp, _data, _id)

# Sample.unknown = lambda _smp: ArArData(name='unknown', data=_smp.SampleIntercept)
# Sample.blank = lambda _smp: ArArData(name='blank', data=_smp.BlankIntercept)
# Sample.parameters = lambda _smp: ArArData(name='parameters', data=_smp.TotalParam)
# Sample.corrected = lambda _smp: ArArData(name='corrected', data=_smp.CorrectedValues)
# Sample.degas = lambda _smp: ArArData(name='degas', data=_smp.DegasValues)
# Sample.isochron = lambda _smp: ArArData(name='isochron', data=_smp.IsochronValues)
# Sample.apparent_ages = lambda _smp: ArArData(name='apparent_ages', data=_smp.ApparentAgeValues)
# Sample.publish = lambda _smp: ArArData(name='publish', data=_smp.PublishValues)

Sample.unknown = lambda _smp: ArArData(name='unknown', data=calc.arr.transpose(_smp.UnknownTable.data))
Sample.blank = lambda _smp: ArArData(name='blank', data=calc.arr.transpose(_smp.BlankTable.data))
Sample.parameters = lambda _smp: ArArData(name='parameters', data=calc.arr.transpose(_smp.TotalParamsTable.data))
Sample.corrected = lambda _smp: ArArData(name='corrected', data=calc.arr.transpose(_smp.CorrectedTable.data))
Sample.degas = lambda _smp: ArArData(name='degas', data=calc.arr.transpose(_smp.DegasPatternTable.data))
Sample.isochron = lambda _smp: ArArData(name='isochron', data=calc.arr.transpose(_smp.IsochronsTable.data))
Sample.apparent_ages = lambda _smp: ArArData(name='apparent_ages', data=calc.arr.transpose(_smp.AgeSpectraTable.data))
Sample.publish = lambda _smp: ArArData(name='publish', data=calc.arr.transpose(_smp.PublishTable.data))

Sample.corr_blank = smp.corr.corr_blank
Sample.corr_massdiscr = smp.corr.corr_massdiscr
Sample.corr_decay = smp.corr.corr_decay
Sample.corr_ca = smp.corr.calc_degas_ca
Sample.corr_k = smp.corr.calc_degas_k
Sample.corr_cl = smp.corr.calc_degas_cl
Sample.corr_atm = smp.corr.calc_degas_atm
Sample.corr_r = smp.corr.calc_degas_r
Sample.calc_ratio = smp.corr.calc_ratio
Sample.set_params = smp.basic.set_params

Sample.set_info = lambda _smp, info: setattr(_smp, 'Info', smp.basic.update_plot_from_dict(_smp.Info, info))

Sample.recalculate = lambda _smp, *args, **kwargs: smp.calculation.recalculate(_smp, *args, **kwargs)
Sample.plot_init = lambda _smp: smp.calculation.recalculate(
    _smp, re_plot=True, isIsochron=False, isInit=True, isPlateau=False)
Sample.plot_isochron = lambda _smp, **kwargs: smp.calculation.recalculate(
    _smp, re_plot=True, isIsochron=True, isInit=False, isPlateau=False, **kwargs)
Sample.plot_age_plateau = lambda _smp: smp.calculation.recalculate(
    _smp, re_plot=True, isIsochron=False, isInit=False, isPlateau=True)
Sample.plot_normal = lambda _smp: smp.calculation.recalculate(
    _smp, re_plot=True, isIsochron=True, isInit=False, isPlateau=False, figures=['figure_2'])
Sample.plot_inverse = lambda _smp: smp.calculation.recalculate(
    _smp, re_plot=True, isIsochron=True, isInit=False, isPlateau=False, figures=['figure_3'])
Sample.plot_cl_1 = lambda _smp: smp.calculation.recalculate(
    _smp, re_plot=True, isIsochron=True, isInit=False, isPlateau=False, figures=['figure_4'])
Sample.plot_cl_2 = lambda _smp: smp.calculation.recalculate(
    _smp, re_plot=True, isIsochron=True, isInit=False, isPlateau=False, figures=['figure_5'])
Sample.plot_cl_3 = lambda _smp: smp.calculation.recalculate(
    _smp, re_plot=True, isIsochron=True, isInit=False, isPlateau=False, figures=['figure_6'])
Sample.plot_3D = lambda _smp: smp.calculation.recalculate(
    _smp, re_plot=True, isIsochron=True, isInit=False, isPlateau=False, figures=['figure_7'])

Sample.show_data = lambda _smp: \
    f"Sample Name: \n\t{_smp.name()}\n" \
    f"Doi: \n\t{_smp.doi()}\n" \
    f"Corrected Values: \n\t{_smp.corrected().to_df()}\n" \
    f"Parameters: \n\t{_smp.parameters().to_df()}\n" \
    f"Isochron Values: \n\t{_smp.isochron().to_df()}\n" \
    f"Apparent Ages: \n\t{_smp.apparent_ages().to_df()}\n" \
    f"Publish Table: \n\t{_smp.publish().to_df()}\n"

__tab = "\t"
Sample.help = lambda _smp: f"" \
                           f"builtin methods:\n " \
                           f"{__tab.join([func for func in dir(Sample) if callable(getattr(Sample, func)) and func.startswith('__')])}\n" \
                           f"dunder-excluded methods:\n " \
                           f"{__tab.join([func for func in dir(Sample) if callable(getattr(Sample, func)) and not func.startswith('__')])}\n"

""" RawData Class Methods """

RawData.do_regression = smp.raw.do_regression
RawData.get_sequence = smp.raw.get_sequence
RawData.to_sample = smp.initial.from_raw_data
RawData.get_unknown = lambda _raw: smp.raw.get_sequence(_raw, True, 'is_unknown', unique=False)
RawData.get_blank = lambda _raw: smp.raw.get_sequence(_raw, True, 'is_blank', unique=False)
RawData.get_air = lambda _raw: smp.raw.get_sequence(_raw, True, 'is_air', unique=False)
Sequence.get_data_df = lambda _seq: pd.DataFrame(_seq.data)
Sequence.get_flag_df = lambda _seq: pd.DataFrame(_seq.flag)
