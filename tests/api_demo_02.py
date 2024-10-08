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

# ---------- 测试导出年龄谱图 PDF ----------

import requests
import ararpy as ap
import numpy as np

# ------ 将以下五个样品的年龄谱图组合到一起 -------
arr_files = [
    r"D:\DjangoProjects\webarar\private\upload\20240728_24FY55.arr",
    r"D:\DjangoProjects\webarar\private\upload\20240714_24FY52.arr",
    r"D:\DjangoProjects\webarar\private\upload\20240621_24FY56a.arr",
    r"D:\DjangoProjects\webarar\private\upload\20240705_24FY50a.arr",
    r"D:\DjangoProjects\webarar\private\upload\20240630_24FY49a.arr",
]
arr_files = [
    r"D:\DjangoProjects\webarar\private\upload\24WHN0168-19KD03-Bio.arr",
    r"D:\DjangoProjects\webarar\private\upload\24WHN0167-20TX62-Bio.arr",
    r"D:\DjangoProjects\webarar\private\upload\24WHN0166-20TX10-Mus.arr",
    r"D:\DjangoProjects\webarar\private\upload\24WHN0164-20TX31-Bio.arr",
    r"D:\DjangoProjects\webarar\private\upload\24WHN0165-20TX10-Bio.arr",
]
colors = ['#1f3c40', '#e35000', '#e1ae0f', '#3d8ebf', '#77dd83', '#c7ae88', '#83d6bb', '#653013', '#cc5f16', '#d0b269']
series = []

# ------ 构建数据 -------
for index, file in enumerate(arr_files):
    smp = ap.from_arr(file_path=file)
    age = smp.ApparentAgeValues[2:4]
    ar = smp.DegasValues[20]
    data = ap.calc.spectra.get_data(*age, ar, cumulative=False)
    series.append({
        'type': 'series.line', 'id': f'line{index * 2 + 0}', 'name': f'line{index * 2 + 0}', 'color': colors[index],
        'data': np.transpose([data[0], data[1]]).tolist(), 'line_caps': 'square',
    })
    series.append({
        'type': 'series.line', 'id': f'line{index * 2 + 1}', 'name': f'line{index * 2 + 1}', 'color': colors[index],
        'data': np.transpose([data[0], data[2]]).tolist(), 'line_caps': 'square',
    })
    series.append({
        'type': 'text', 'id': f'text{index * 2 + 0}', 'name': f'text{index * 2 + 0}', 'color': colors[index],
        'text': f'{smp.name()}<r>{round(smp.Info.results.age_plateau[0]["age"], 2)}', 'size': 10, 'data': [index * 15 + 5, 23],
    })
data = {
    "data": [
        {
            'xAxis': [{'extent': [0, 100], 'interval': [0, 20, 40, 60, 80, 100],
                       'title': 'Cumulative <sup>39</sup>Ar Released (%)', 'nameLocation': 'middle',}],
            'yAxis': [{'extent': [0,  25], 'interval': [0, 5, 10, 15, 20, 25],
                       'title': 'Apparent Age (Ma)', 'nameLocation': 'middle',}],
            'series': series
        }
    ],
    "file_name": "WHA",
    "plot_names": ["all age plateaus"],
}

# ------ 发起请求 -------
url = 'http://127.0.0.1:8000/calc/api/export_chart'
response = requests.post(url, data=ap.smp.json.dumps(data))

# ------ 解析结果 ---
res = ap.smp.json.loads(response.content)
print(f"{res = }")
down_file = requests.get(f'http://127.0.0.1:8000{res["href"]}')
with open(f'C:\\Users\\Young\\Downloads\\{res["href"].split("/")[-1]}', 'wb') as f:
    f.write(down_file.content)
