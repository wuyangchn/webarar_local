from django.db import models

# Create your models here.


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的设备信息地址
    uuid = models.CharField("USER_UUID", max_length=64)
    # ip地址
    ip = models.GenericIPAddressField("IP")
    # 设备信息
    device = models.CharField("HTTP_USER_AGENT", max_length=1000)
    # 访问次数
    count = models.IntegerField("REQUEST_COUNT", default=1, editable=False)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
