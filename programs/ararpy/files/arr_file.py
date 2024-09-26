#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - files - arr_file
# ==========================================
#
#
#
"""
# === External imports ===
import os
import pickle


def save(file_path, sample):
    """ Save arr project as arr files

    Parameters
    ----------
    file_path : str, filepath
    sample : Sample instance

    Returns
    -------
    str, file name
    """
    file_path = os.path.join(file_path, f"{sample.Info.sample.name}.arr")
    with open(file_path, 'wb') as f:
        f.write(pickle.dumps(sample))
    # with open(file_path, 'w') as f:
    # # save serialized json data to a readable text
    #     f.write(basic_funcs.getJsonDumps(sample))
    return f"{sample.Info.sample.name}.arr"


