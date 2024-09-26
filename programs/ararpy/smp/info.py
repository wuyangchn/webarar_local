#  Copyright (C) 2024 Yang. - All Rights Reserved

# !/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2024 Yang 
# ararpy - info
# ==========================================
#
#
# 
"""


def name(smp, n: str = None):
    if n is None:
        return smp.Info.sample.name
    elif isinstance(n, str):
        smp.Info.sample.name = n
        return n
    else:
        raise ValueError(f"{n} is not a string")
