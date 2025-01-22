from django.db import models

# Create your models here.


class Journal(models.Model):
    id = models.BigAutoField(primary_key=True)
    full_name = models.CharField("FULL_NAME", unique=True, max_length=190)
    short_name = models.CharField("SHORT_NAME", max_length=100)
    jif21 = models.CharField("JIF21", max_length=64)
    jif22 = models.CharField("JIF22", max_length=64)
    jif23 = models.CharField("JIF23", max_length=64)
    category = models.CharField("CATEGORY", max_length=500)
    issn = models.CharField("ISSN", max_length=64)
    eissn = models.CharField("EISSN", max_length=64)


class CUGJournalRanking(models.Model):
    id = models.BigAutoField(primary_key=True)
    full_name = models.CharField("FULL_NAME", max_length=190)
    short_name = models.CharField("SHORT_NAME", max_length=100, default="N/A")
    tier = models.CharField("TIER", max_length=64)
    subject = models.CharField("SUBJECT", max_length=100)
    tag = models.CharField("TAG", max_length=64, default="")
    jif21 = models.CharField("JIF21", max_length=64, default="N/A")
    jif22 = models.CharField("JIF22", max_length=64, default="N/A")
    jif23 = models.CharField("JIF23", max_length=64, default="N/A")
    issn = models.CharField("ISSN", max_length=64, default="N/A")
    eissn = models.CharField("EISSN", max_length=64, default="N/A")
