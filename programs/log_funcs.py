import logging
import os
import time
from django.conf import settings
from concurrent_log_handler import ConcurrentTimedRotatingFileHandler


# https://blog.csdn.net/tofu_yi/article/details/118566756
# https://zhuanlan.zhihu.com/p/445411809
# 实例化logging对象,并以当前文件的名字作为logger实例的名字
logger_collect = logging.getLogger('collect')
logfile = os.path.abspath("logs/main.log")
# Using concurrent_log_handler instead of logging Headler,
# to avoid PermissionError during rotating the log files
# https://github.com/Preston-Landers/concurrent-log-handler
logger_collect.addHandler(ConcurrentTimedRotatingFileHandler(logfile, when='MIDNIGHT', backupCount=3))
logger_collect.setLevel(getattr(logging, 'INFO'))

# time format
default_time_format = '%Y-%m-%d %H:%M:%S'
default_msec_format = '%s.%03d'

OPERATION_DICT = {
    '000': 'Visit',
    '001': 'Open file',
    '002': 'Chang view',
    '003': 'Click btn',
    '004': 'Handle raw file',
    '005': 'Handle param project',
}


def set_info_log(ip, operationCode, type, msg=''):
    operation = OPERATION_DICT[str(operationCode)]
    return getattr(logger_collect, type.lower())(f"{format_time(time.time())} -- ip: {ip}, operation: {operation}, msg: {msg}")


def format_time(ct, datefmt=None):
    """
    Return the creation time as formatted text.
    """
    msecs = (ct - int(ct)) * 1000
    if datefmt:
        s = time.strftime(datefmt, ct)
    else:
        s = time.strftime(default_time_format, time.localtime(ct))
        if default_msec_format:
            s = default_msec_format % (s, msecs)
    return s


def log(*args):
    """
    Parameters
    ----------
    args

    Returns
    -------

    """
    if settings.DEBUG:
        print(*args)
