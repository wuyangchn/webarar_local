from django.shortcuts import render
from programs import http_funcs
# Create your views here.


def main_view(request):
    # print(http_funcs.get_lang(request))
    return render(request, 'doc.html')


def doc_en(request):
    return render(request, 'doc.html')


def doc_zh_cn(request):
    return render(request, 'doc_zh_cn.html')


def tutorial(request):
    return render(request, 'tutorial.html')


def tutorial_zh_CN(request):
    return render(request, 'tutorial_zh_CN.html')


def deploy(request):
    return render(request, 'deploy.html')


def deploy_zh_CN(request):
    return render(request, 'deploy_zh_CN.html')


def update_log(request):
    return render(request, 'update_log.html')
