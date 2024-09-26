import pickle
import uuid
import json
from django.core.cache import cache
from django.shortcuts import render
from django.views import View
from calc import models
from . import ap

DEFAULT_CACHE_TIMEOUT = 86400


def get_ip(request):
    """
    Get ipv4 address from requests
    """
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_device(request):
    """
    Get device information of user browser
    """
    # print('请求相关的信息：', request.environ)  # environ里面有请求的所有信息
    # print('设备信息：', request.environ.get("HTTP_USER_AGENT"))  # 全部返回的是个字典
    try:
        return request.environ.get("HTTP_USER_AGENT")
    except AttributeError:
        return "This is ASGIRequest"


def get_lang(request):
    """
    Get language setting of user browser
    """
    try:
        return request.environ.get("HTTP_ACCEPT_LANGUAGE")
    except AttributeError:
        return "This is ASGIRequest"


def is_ajax(request):
    """
    Return if the request is from ajax
    """
    return request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"


def create_cache(obj, cache_key=''):
    """
    Create (leave key default) or update cache (give key). This is used to link sample
    instance with cache key, which is an unique identifier for this object in the cache.
    The cache key will also be sent to user so that changes from front can be identified.
    """
    if not cache_key:
        cache_key = create_cache_key()
    cache_value = pickle.dumps(obj)
    # cache_value = basic_funcs.getJsonDumps(sample)
    cache.set(cache_key, cache_value, timeout=DEFAULT_CACHE_TIMEOUT)
    return cache_key


def create_cache_key():
    """
    Create UUID as a cache_key for each opened sample instance using uuid module.
    Make a random UUID and convert it to a 32-character hexadecimal string.
    uuid1() and uuid4() can both yield unique uuid, but uuid1() might contain the
    computer’s network address
    """
    return str(uuid.uuid4().hex)


def touch_cache(cache_key=''):
    return cache.touch(cache_key, timeout=DEFAULT_CACHE_TIMEOUT, version=None)


def cache_load(cache_key):
    """
    Parameters
    ----------
    cache_key

    Returns
    -------

    """
    return pickle.loads(cache.get(cache_key))


def set_mysql(request, mysql, fingerprint, file_path="", cache_key=""):
    mysql.objects.create(
        user=str(fingerprint),
        ip=get_ip(request),
        device=get_device(request),
        file_path=file_path,
        cache_key=cache_key
    )


def set_user_sql(request, mysql, fingerprint):
    if mysql.objects.filter(uuid=str(fingerprint)).exists():
        _user = mysql.objects.get(uuid=str(fingerprint))
        _user.count = _user.count + 1
        _user.ip = get_ip(request)
        _user.device = get_device(request)
        _user.save()
    else:
        mysql.objects.create(
            uuid=str(fingerprint),
            ip=get_ip(request),
            device=get_device(request),
            count=1
        )


def open_object_file(request, sample, web_file_path, cache_key=''):
    # write cache, cache kay is considered as ID of sample instance
    cache_key = create_cache(sample, cache_key=cache_key)
    # write mysql
    fingerprint = request.POST.get('fingerprint')
    set_mysql(request, models.CalcRecord, fingerprint, web_file_path, cache_key)
    #
    allIrraNames = list(models.IrraParams.objects.values_list('name', flat=True))
    allCalcNames = list(models.CalcParams.objects.values_list('name', flat=True))
    allSmpNames = list(models.SmpParams.objects.values_list('name', flat=True))
    return render(request, 'object.html', {
        'cache_key': json.dumps(cache_key),
        'allIrraNames': allIrraNames, 'allCalcNames': allCalcNames, 'allSmpNames': allSmpNames,
        'sampleComponents': ap.smp.json.dumps(ap.smp.basic.get_components(sample)),
    })


def open_last_object(request):
    fingerprint = request.POST.get('fingerprint')
    # print(cache.keys('*'))
    try:
        last_record = models.CalcRecord.objects.filter(user=str(fingerprint)).order_by('-id')[0]
        cache_key = last_record.cache_key
    except (BaseException, Exception):
        cache_key = ''
    try:
        sample = cache_load(cache_key)
        if sample is None:
            raise IndexError
    except (BaseException, Exception):
        # print('No file found in cache!')
        sample = ap.Sample()
        ap.smp.initial.initial(sample)
        cache_key = create_cache(sample, cache_key=cache_key)
    return open_object_file(request, sample, web_file_path='', cache_key=cache_key)


class ArArView(View):
    """
    This class is rewritten based on View and is used to dispatch requests from client side.

    A request will first classified based on its method, including 'get', 'post' and others
    (see detail in class attribution http_method_names of View class); For each method, a
    function with the same name is required to handle it. Here I rewrite POST function,
    because I usually need to use <flag> to identify some special requests.

    In dispatch function, ajax requests are identified based on the flag value contained
    in request body.

    Some examples:
        1. POST request from a form, will go to <post> function, and then be dispatched
        according to the <flag> value, which is set as a hidden input;
        2. POST request from Ajax need to contain a <flag> value to let it identified. Two
        ways can be used, sending flag in url or body;
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize
        self.ip = ''
        self.flag = ''
        self.body = {}
        self.content = {}
        self.cache_key = ''
        self.sample = ...

        self.dispatch_post_method_name = [
            # Add names in daughter classes
        ]

    def post(self, request, *args, **kwargs):
        self.ip = get_ip(self.request)
        # Finding a right function to response the request
        self.flag = request.POST.get('flag').lower()
        if self.flag in self.dispatch_post_method_name:
            handler = getattr(self, self.flag, self.flag_not_matched)
        else:
            handler = self.flag_not_matched
        print("post: %s" % handler.__name__)
        return handler(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.ip = get_ip(self.request)
        # Rewrite dispatch method to add special responses to ajax requests
        handler = self.http_method_not_allowed  # Default

        # Ajax request, formdata type content, flag is included in POST
        try:
            self.flag = request.POST.get('flag').lower()
            handler = getattr(self, self.flag, self.flag_not_matched)
        except (Exception, BaseException):
            pass
        else:
            print("flag: %s" % handler.__name__)
            return handler(request, *args, **kwargs)

        # Ajax request, json type content, flag is included in body
        try:
            self.body = json.loads(request.body.decode('utf-8'))
            self.cache_key = str(self.body['cache_key'])  # Key to obtain sample from cache
            self.sample = pickle.loads(cache.get(self.cache_key, default=pickle.dumps(ap.smp.Sample())))
            touch_cache(self.cache_key)  # Update cache time
        except KeyError:
            print("No cache key in request body")
        except (Exception, BaseException):
            pass
        try:
            self.content = self.body['content']
        except KeyError:
            pass
        if "flag" in kwargs.keys():
            self.flag = kwargs['flag']
            handler = getattr(self, self.flag, self.flag_not_matched)
        elif is_ajax(request):
            if "flag" in self.body.keys():
                self.flag = str(self.body['flag']).lower()
                handler = getattr(self, self.flag, self.flag_not_matched)
        elif request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)

        print("flag: %s" % handler.__name__)
        return handler(request, *args, **kwargs)

    def flag_not_matched(self, request, *args, **kwargs):
        print(f'flag_not_matched: {self.flag}')
        pass

