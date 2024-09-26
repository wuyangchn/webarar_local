#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - smp - json
# ==========================================
#
#
#
"""

import json
import numpy as np
import pandas as pd
from .sample import Sample, Table, Plot, RawData, Sequence, ArArBasic


def dumps(a):
    # return json.dumps(a, default=lambda o: o.__dict__ if hasattr(0, '__dict__') else o, sort_keys=True, indent=4)
    return json.dumps(a, cls=MyEncoder, indent=4)


def loads(a):
    return json.loads(a)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        # np.array
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        # pd.DataFrame
        if isinstance(obj, pd.DataFrame):
            print(obj)
            raise ValueError(f"DataFrame objects found.")
        # complex number
        if isinstance(obj, complex):
            return "complex number"
        # numpy.int32
        if isinstance(obj, (np.int8, np.int16, np.int32, np.int64)):
            return int(obj)
        # sample or raw instance
        if isinstance(obj, (Sample, Plot, Table, Plot.Text, Plot.Axis, Plot.Label,
                            Plot.Set, Plot.BasicAttr, RawData, Sequence, ArArBasic)):
            if isinstance(obj, Sequence):
                return dict(obj.__dict__, **{
                    'is_blank': obj.is_blank(), 'is_unknown': obj.is_unknown(),
                    'is_air': obj.is_air()})
            return obj.__dict__
        if not isinstance(obj, (int, str, list, dict, tuple, float)):
            print(f"Special type, {type(obj) = }, {obj = }")
        return super(MyEncoder, self).default(obj)
