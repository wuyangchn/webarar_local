import json
import os

from django.http import JsonResponse

from home import models
from django.shortcuts import render, redirect

from programs import http_funcs, log_funcs, ap
from webarar import settings

# Create your views here.


def references(request):
    return render(request, 'references.html')


def journal_ranking(request):
    # 记录访问
    if http_funcs.is_ajax(request):
        fingerprint = json.loads(request.body.decode('utf-8'))['fingerprint']
        http_funcs.set_user_sql(request, models.User, fingerprint)
        return JsonResponse({})
    disciplines = [
        '信息与通信工程', '物理学', '土木工程', '水利工程', '环境科学与工程', '机械工程', '工商管理', '安全科学与工程', '地质资源与地质工程（资源）', '地球物理学',
        '管理科学与工程', '数学', '外国语言文学', '新闻传播学', '计算机科学与技术', '地理科学', '法学', '马克思主义理论', '设计学', '教育学',
        '地质资源与地质工程（勘察地球物理）', '化学', '石油与天然气工程', '公共管理', '材料科学与工程', '地质资源与地质工程（工程地质）', '大气科学', '地质学', '软件工程',
        '海洋科学', '体育学', '心理学', '测绘科学与技术', '生物学', '地质资源与地质工程（岩土钻掘）', '地质资源与地质工程（地球信息）', '控制科学与工程', '应用经济学'
    ]
    JIF21_list = ap.files.xls.open_xls(os.path.join(settings.STATICFILES_DIRS[0], f'document/JCR_JIF_2021.xls'))
    JIF21_list = JIF21_list['JCR_JIF_2021'][1:]
    JIF21_dict = {}
    for journal in JIF21_list:
        JIF21_dict.update({str(journal[0]).upper(): journal})
    JIF22_list = ap.files.xls.open_xls(os.path.join(settings.STATICFILES_DIRS[0], f'document/JCR_JIF_2022.xls'))
    JIF22_list = JIF22_list['JCR_JIF_2022'][1:]
    JIF22_dict = {}
    for journal in JIF22_list:
        JIF22_dict.update({str(journal[0]).upper(): journal})
    def get_impact_factor(journal_name, flag=21):
        try:
            if flag == 21:
                return JIF21_dict[journal_name.upper()][6]
            elif flag == 22:
                return JIF22_dict[journal_name.upper()][6]
        except Exception as e:
            return 'N/A'
    def get_diff(a, b):
        try:
            diff = round(float(b) - float(a), 2)
            return f"+ {abs(diff)}" if diff >= 0 else f"- {abs(diff)}"
        except:
            return 'N/A'
    data = []
    def add_data(tag):
        file_url = os.path.join(settings.STATICFILES_DIRS[0], f'document/{tag}')
        for home, dirs, files in os.walk(file_url):
            for file in files:
                file_path = os.path.join(home, file)
                content = ap.files.xls.open_xls(file_path)
                for each in content['Sheet1'][1:]:
                    impact_factor_21 = get_impact_factor(each[0].upper(), flag=21)
                    impact_factor_22 = get_impact_factor(each[0].upper(), flag=22)
                    data.append({'journal': each[0].upper(), 'tier': each[1], 'discipline': each[2],
                                 'tag': tag, 'IF21': impact_factor_21, 'IF22': impact_factor_22,
                                 'Diff': get_diff(impact_factor_21, impact_factor_22)})
    add_data('理工类')
    add_data('人文社科类')
    def neg_jif(jif):
        if jif == 'N/A':
            return 0
        if isinstance(jif, str) and not jif.isprintable():
            jif = ''.join(x for x in jif if x.isprintable())
        return -float(jif)
    data.sort(key=lambda x: (x['tier'], neg_jif(x['IF22'])))
    log_funcs.set_info_log(http_funcs.get_ip(request), '000', 'info', 'Visit journal ranking html')
    return render(request, 'journal_ranking.html', {'data': json.dumps(data)})

def api_callback(request):
    return journal_ranking(request)

