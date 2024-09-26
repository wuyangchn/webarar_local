#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - files - basic
# ==========================================
#
#
#
"""

import os
import pickle
import traceback
import json


def upload(file, media_dir):
    try:
        name, suffix = os.path.splitext(file.name)
        if suffix.lower() not in [
            '.xls', '.age', '.xlsx', '.arr', '.jpg', '.png', '.txt',
            '.log', '.seq', '.json', '.ahd', '.csv']:
            raise TypeError(f"The imported file is not supported: {suffix}")
        web_file_path = os.path.join(media_dir, file.name)
        with open(web_file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        print("File path on the server: %s" % web_file_path)
    except PermissionError:
        raise ValueError(f'Permission denied')
    except (Exception, BaseException) as e:
        print(traceback.format_exc())
        raise ValueError(f'Error in opening file: {e}')
    else:
        return web_file_path, name, suffix


def read(file_path):
    """ Read text files, default 'r', 'rb'
    Parameters
    ----------
    file_path

    Returns
    -------

    """
    try:
        with open(file_path, 'r') as f:
            params = json.load(f)
    except UnicodeDecodeError:
        with open(file_path, 'rb') as f:
            params = pickle.load(f)
    return params


def write(file_path, params):
    """
    Parameters
    ----------
    file_path
    params

    Returns
    -------

    """
    # with open(file_path, 'wb') as f:
    #     f.write(pickle.dumps(params))
    with open(file_path, 'w') as f:  # save serialized json data to a readable text
        f.write(json.dumps(params))
    return file_path


def delete(file_path):
    """
    Parameters
    ----------
    file_path

    Returns
    -------

    """
    try:
        os.remove(file_path)
    except Exception:
        return False
    else:
        return True
