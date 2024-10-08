#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2024 Yang 
# webarar - api_test
# ==========================================
#
#
# 
"""

import requests

url = 'http://127.0.0.1:8000/calc/api/export_pdf'
data = {"cache_key": "6afb992af3ee43b68155ab7fb3cf467d", "figure_id": "figure_2", "merged_pdf": False}
response = requests.post(url, json=data)
# response.status_code
# 200
# response.text
# '{"status": "success", "href": "/static/download/22WHA0433.arr"}'

url = 'http://127.0.0.1:8000/calc/api/open_arr'
f = open(r"D:\DjangoProjects\webarar\static\download\22WHA0433.arr", "rb")
data = {"arr_file": f}
response2 = requests.post(url, files=data)
# response2.status_code
# 200
#

