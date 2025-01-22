import json
import os

from django.http import JsonResponse

from home import models as home_models
from . import models
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
        http_funcs.set_user_sql(request, home_models.User, fingerprint)
        return JsonResponse({})
    # disciplines = [
    #     '信息与通信工程', '物理学', '土木工程', '水利工程', '环境科学与工程', '机械工程', '工商管理', '安全科学与工程', '地质资源与地质工程（资源）', '地球物理学',
    #     '管理科学与工程', '数学', '外国语言文学', '新闻传播学', '计算机科学与技术', '地理科学', '法学', '马克思主义理论', '设计学', '教育学',
    #     '地质资源与地质工程（勘察地球物理）', '化学', '石油与天然气工程', '公共管理', '材料科学与工程', '地质资源与地质工程（工程地质）', '大气科学', '地质学', '软件工程',
    #     '海洋科学', '体育学', '心理学', '测绘科学与技术', '生物学', '地质资源与地质工程（岩土钻掘）', '地质资源与地质工程（地球信息）', '控制科学与工程', '应用经济学'
    # ]
    #
    # def isRenwen(s):
    #     return s in [
    #         '体育学', '公共管理', '外国语言文学', '工商管理', '应用经济学', '心理学', '教育学', '新闻传播学', '法学',  '管理科学与工程', '设计学', '马克思主义理论'
    #     ]

    # JIF21_list = ap.files.xls.open_xls(os.path.join(settings.STATICFILES_DIRS[0], f'document/JCR_JIF_2021.xls'))
    # JIF21_list = JIF21_list['JCR_JIF_2021'][1:]
    # JIF21_dict = {}
    # JIF22_list = ap.files.xls.open_xls(os.path.join(settings.STATICFILES_DIRS[0], f'document/JCR_JIF_2022.xls'))
    # JIF22_list = JIF22_list['JCR_JIF_2022'][1:]
    # JIF22_dict = {}
    # JIF23_list = ap.files.xls.open_xls(os.path.join(settings.STATICFILES_DIRS[0], f'document/JCR_JIF_2023.xls'))
    # JIF23_list = JIF23_list['JCR_JIF_2023'][1:]
    # JIF23_dict = {}
    # for journal in JIF21_list:
    #     JIF21_dict.update({str(journal[0]).upper(): journal})
    # for journal in JIF22_list:
    #     JIF22_dict.update({str(journal[0]).upper(): journal})
    # for journal in JIF23_list:
    #     JIF23_dict.update({str(journal[0]).upper(): journal})

    # def get_diff(a, b):
    #     try:
    #         diff = round(float(b) - float(a), 2)
    #         return f"+ {abs(diff)}" if diff >= 0 else f"- {abs(diff)}"
    #     except:
    #         return 'N/A'
    # data = []
    # for cug_journal in models.CUGJournalRanking.objects.all():
    #     cug_journal.tag = '人文社科类' if isRenwen(cug_journal.subject) else '理工类' if cug_journal.subject in disciplines else "N/A"
    #     cug_journal.save()
    #     journal_record = models.Journal.objects.filter(full_name__iexact=str(cug_journal.full_name)).first()
    #     if journal_record is not None:
    #         cug_journal.jif21 = journal_record.jif21
    #         cug_journal.jif22 = journal_record.jif22
    #         cug_journal.jif23 = journal_record.jif23
    #         cug_journal.short_name = journal_record.short_name
    #         cug_journal.issn = journal_record.issn
    #         cug_journal.eissn = journal_record.eissn
    #         cug_journal.tag = '人文社科类' if isRenwen(cug_journal.subject) else '理工类'
    #         cug_journal.save()
    #         jifs = [journal_record.jif21, journal_record.jif22, journal_record.jif23]
    #     else:
    #         jifs = ["N/A", "N/A", "N/A"]
    #     data.append({
    #         'journal': cug_journal.full_name, 'tier': cug_journal.tier,
    #         'discipline': cug_journal.subject, 'tag': cug_journal.tag,
    #         'IF21': jifs[0], 'IF22': jifs[1], 'IF23': jifs[2],
    #         'Diff': get_diff(jifs[1], jifs[2])
    #     })
    data = list(models.CUGJournalRanking.objects.values('full_name', 'tier', 'subject', 'tag', 'jif21', 'jif22', 'jif23'))

    def neg_jif(jif):
        if isinstance(jif, str) and not jif.isprintable():
            jif = ''.join(x for x in jif if x.isprintable())
        try:
            return -float(jif)
        except:
            return 0
    data.sort(key=lambda x: (x['tier'], neg_jif(x['jif23'])))
    log_funcs.set_info_log(http_funcs.get_ip(request), '000', 'info', 'Visit journal ranking html')
    return render(request, 'journal_ranking.html', {'data': ap.smp.json.dumps(data)})

def api_callback(request):
    return journal_ranking(request)

