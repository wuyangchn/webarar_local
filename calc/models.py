from django.db import models

# Create your models here.


class CalcRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的ip地址
    user = models.CharField("USER_UUID", max_length=64)
    # 新建者的ip地址
    ip = models.GenericIPAddressField("IP")
    # 新建者的设备信息地址
    device = models.CharField("HTTP_USER_AGENT", max_length=1000)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    # 文件名
    file_path = models.CharField("FILE_NAME", max_length=1000, null=True)
    # uuid
    cache_key = models.CharField("CACHE_KEY", max_length=64, null=True)


class IrraParams(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的ip地址
    ip = models.CharField("IP", max_length=64, null=True)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    #
    name = models.CharField("NAME", unique=True, max_length=64, null=False)
    #
    pin = models.CharField("PIN", max_length=64, null=False)
    # 文件路径
    file_path = models.CharField("FILE_PATH", max_length=1000, null=False)
    #
    uploader_email = models.EmailField('UPLOADER_EMAIL', max_length=64, null=True)


class CalcParams(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的ip地址
    ip = models.CharField("IP", max_length=64, null=True)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    #
    name = models.CharField("NAME", unique=True, max_length=64, null=False)
    #
    pin = models.CharField("PIN", max_length=64, null=False)
    # 文件路径
    file_path = models.CharField("FILE_PATH", max_length=1000, null=False)
    #
    uploader_email = models.EmailField('UPLOADER_EMAIL', max_length=64, null=True)


class SmpParams(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的ip地址
    ip = models.CharField("IP", max_length=64, null=False)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    #
    name = models.CharField("NAME", unique=True, max_length=64, null=False)
    #
    pin = models.CharField("PIN", max_length=64, null=False)
    # 文件路径
    file_path = models.CharField("FILE_PATH", max_length=1000, null=False)
    #
    uploader_email = models.EmailField('UPLOADER_EMAIL', max_length=64, null=True)


class InputFilterParams(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的ip地址
    ip = models.CharField("IP", max_length=64, null=False)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    #
    name = models.CharField("NAME", unique=True, max_length=64, null=False)
    #
    pin = models.CharField("PIN", max_length=64, null=False)
    # 文件路径
    file_path = models.CharField("FILE_PATH", max_length=1000, null=False)
    #
    uploader_email = models.EmailField('UPLOADER_EMAIL', max_length=64, null=True)


class ExportPDFParams(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的ip地址
    ip = models.CharField("IP", max_length=64, null=False)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    #
    name = models.CharField("NAME", unique=True, max_length=64, null=False)
    #
    pin = models.CharField("PIN", max_length=64, null=False)
    # 文件路径
    file_path = models.CharField("FILE_PATH", max_length=1000, null=False)
    #
    uploader_email = models.EmailField('UPLOADER_EMAIL', max_length=64, null=True)

