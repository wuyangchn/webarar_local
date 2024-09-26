#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - smp - calculation
# 2023-12-4
# ==========================================
#
# ArArPy.smp.smp_funcs
#
"""

from . import (
    basic, corr, initial, plots, style, table
)
from .sample import Sample


def recalculate(
        sample: Sample, re_initial: bool = False,
        re_corr_blank: bool = False, re_corr_massdiscr: bool = False,
        re_corr_decay: bool = False, re_degas_ca: bool = False, re_degas_k: bool = False,
        re_degas_cl: bool = False, re_degas_atm: bool = False, re_degas_r: bool = False,
        re_calc_ratio: bool = False, re_calc_apparent_age: bool = False, monte_carlo: bool = False,
        re_plot: bool = False, re_plot_style: bool = False, re_set_table: bool = False,
        re_table_style: bool = False, **kwargs
):
    """
    Assign recalculate functions based on selections
    Parameters
    ----------
    sample
    re_initial
    re_corr_blank
    re_corr_massdiscr
    re_corr_decay
    re_degas_ca
    re_degas_k
    re_degas_cl
    re_degas_atm
    re_degas_r
    re_calc_ratio
    re_calc_apparent_age
    monte_carlo
    re_plot
    re_plot_style
    re_set_table
    re_table_style
    kwargs

    Returns
    -------
    Sample
    """
    if len(sample.UnselectedSequence) == len(sample.SelectedSequence1) == len(sample.SelectedSequence2) == 0:
        sample.UnselectedSequence = list(range(len(sample.SequenceName)))
    # print(f"{sample.UnselectedSequence = }")
    # print(f"{sample.SelectedSequence1 = }")
    # print(f"{sample.SelectedSequence2 = }")
    # --- initializing ---
    if re_initial:  # 1
        initial.re_set_smp(sample)
    # --- calculating ---
    if re_corr_blank:  # 2
        corr.corr_blank(sample)
    if re_corr_massdiscr:  # 3
        corr.corr_massdiscr(sample)
    if re_corr_decay:  # 4
        corr.corr_decay(sample)
    if re_degas_ca:  # 5
        corr.calc_degas_ca(sample)
    if re_degas_k:  # 6
        corr.calc_degas_k(sample)
    if re_degas_cl:  # 7
        corr.calc_degas_cl(sample)
    if re_degas_atm:  # 8
        corr.calc_degas_atm(sample)
    if re_degas_r:  # 9
        corr.calc_degas_r(sample)
    if re_calc_ratio:  # 10
        corr.calc_ratio(sample, monte_carlo)
    if re_calc_apparent_age:  # 11
        basic.calc_apparent_ages(sample)
    # --- plot and table ---
    if re_plot:  # 12
        plots.set_plot_data(sample, **kwargs)
    if re_plot_style:  # 13
        style.set_plot_style(sample)
    if re_set_table:  # 14
        table.update_table_data(sample)
    if re_table_style:  # 15
        style.set_table_style(sample)
    return sample

