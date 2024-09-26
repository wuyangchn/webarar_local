#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - smp - style
# ==========================================
#
#
#
"""

import traceback
import numpy as np
from .. import calc
from . import (sample as samples, basic, initial, plots, )

Sample = samples.Sample
Table = samples.Table
Plot = samples.Plot

TABLEHEADER = lambda index: [
    '',
    samples.SAMPLE_INTERCEPT_HEADERS, samples.BLANK_INTERCEPT_HEADERS,
    samples.CORRECTED_HEADERS, samples.DEGAS_HEADERS, samples.PUBLISH_TABLE_HEADERS,
    samples.SPECTRUM_TABLE_HEADERS, samples.ISOCHRON_TABLE_HEADERS,
    samples.TOTAL_PARAMS_HEADERS
][index]


# =======================
# Reset plot style
# =======================
def set_plot_style(smp: Sample):
    """

    Parameters
    ----------
    smp

    Returns
    -------

    """
    # Reset styles
    initial.initial_plot_styles(smp, except_attrs=['data'])
    # Auto scale
    reset_plot_scale(smp)
    # Reset isochron data
    plots.reset_isochron_line_data(smp)
    # Auto position and contents of texts
    reset_text(smp)
    # Set title, which are deleted in initializing
    suffix = f"{smp.Info.sample.name} {smp.Info.sample.material}"
    for figure_id, figure in basic.get_components(smp).items():
        if isinstance(figure, Plot):
            if not hasattr(figure, 'title'):
                setattr(figure, 'title', Plot.Text())
            setattr(getattr(figure, 'title'), 'text', f"{suffix} {getattr(figure, 'name', '')}")


def reset_plot_scale(smp: Sample, only_figure: str = None):
    """
    Reset x- and y-axes scale
    Parameters
    ----------
    smp : sample instance
    only_figure

    Returns
    -------
    tuple of two tuples, (xscale, yscale)
    """
    for k, v in basic.get_components(smp).items():
        if not isinstance(v, Plot):
            continue
        if only_figure is not None and k != only_figure:
            continue
        if k == 'figure_1':
            try:
                # data = calc.arr.transpose(
                #     v.data + v.data + v.set1.data + v.set1.data + v.set2.data + v.set2.data)
                k0 = calc.arr.transpose(v.data)
                k1 = calc.arr.transpose(v.set1.data) if len(v.set1.data) != 0 else [[]] * 3
                k2 = calc.arr.transpose(v.set2.data) if len(v.set2.data) != 0 else [[]] * 3
                data = np.concatenate([k0, k1, k2], axis=1)
                ylist = np.concatenate([data[1], data[2]])
                yscale = calc.plot.get_axis_scale(ylist, min_interval=5, extra_count=1)
                xscale = [0, 100, 20]
            except (Exception, BaseException):
                print(traceback.format_exc())
                continue
        elif k == 'figure_3':
            try:
                xlist = v.data[0]
                xscale = calc.plot.get_axis_scale(xlist)
                yscale = [0, 0.004, 4, 0.001]
            except (Exception, BaseException):
                # print(traceback.format_exc())
                continue
        elif k == 'figure_7':
            try:
                xlist, ylist, zlist = v.data[0], v.data[2], v.data[4]
                xscale = calc.plot.get_axis_scale(xlist)
                yscale = calc.plot.get_axis_scale(ylist)
                zscale = calc.plot.get_axis_scale(zlist)
                setattr(getattr(v, 'zaxis'), 'min', zscale[0])
                setattr(getattr(v, 'zaxis'), 'max', zscale[1])
                setattr(getattr(v, 'zaxis'), 'split_number', zscale[2])
            except (Exception, BaseException):
                # print(traceback.format_exc())
                continue
        elif k == 'figure_9':
            try:
                xlist = v.set3.data[0] + [v.set3.data[0][i] - v.set3.data[1][i] for i in
                                          range(len(v.set3.data[0]))] + [
                            v.set3.data[0][i] + v.set3.data[1][i] for i in range(len(v.set3.data[0]))]
                ylist = v.set1.data[1]
                xscale = calc.plot.get_axis_scale(xlist)
                yscale = calc.plot.get_axis_scale(ylist)
            except (Exception, BaseException):
                print(traceback.format_exc())
                continue
        else:
            try:
                xlist = v.data[0]
                ylist = v.data[2]
                xscale = calc.plot.get_axis_scale(xlist)
                yscale = calc.plot.get_axis_scale(ylist)
            except (Exception, BaseException):
                # print(traceback.format_exc())
                continue
        setattr(getattr(v, 'xaxis', Plot.Axis()), 'min', xscale[0])
        setattr(getattr(v, 'xaxis', Plot.Axis()), 'max', xscale[1])
        setattr(getattr(v, 'xaxis', Plot.Axis()), 'split_number', xscale[2])
        setattr(getattr(v, 'yaxis', Plot.Axis()), 'min', yscale[0])
        setattr(getattr(v, 'yaxis', Plot.Axis()), 'max', yscale[1])
        setattr(getattr(v, 'yaxis', Plot.Axis()), 'split_number', yscale[2])

        if only_figure is not None and k == only_figure:
            return xscale, yscale


def reset_text(smp: Sample, only_figure: str = None):
    """
    Reset text position to default, if only figure is defined, only this figure will be reset.
    Parameters
    ----------
    smp
    only_figure

    Returns
    -------
    None
    """
    for figure_id in list(samples.DEFAULT_PLOT_STYLES.keys()):
        if only_figure is not None and figure_id != only_figure:
            continue
        figure = basic.get_component_byid(smp, figure_id)
        text_1 = basic.get_plot_set(figure, 'Text for Set 1')
        if text_1 is not None:
            setattr(text_1, 'pos', [20, 40])
            setattr(text_1, 'text', "")
        text_2 = basic.get_plot_set(figure, 'Text for Set 2')
        if text_2 is not None:
            setattr(text_2, 'pos', [70, 40])
            setattr(text_2, 'text', "")


# =======================
# Reset plot style
# =======================
def set_table_style(sample: Sample):
    """

    Parameters
    ----------
    sample

    Returns
    -------

    """
    for key, comp in basic.get_components(sample).items():
        if isinstance(comp, Table):
            comp.header = TABLEHEADER(index=int(comp.id))
            comp.colcount = len(comp.header)
            comp.coltypes = [{'type': 'numeric'}] * (comp.colcount)
            textindexs = getattr(comp, 'textindexs', [0]) if hasattr(comp, 'textindexs') else [0]
            for i in textindexs:
                comp.coltypes[i] = {'type': 'text'}

