# Generated by Django 4.2.5 on 2024-11-15 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0005_cugjournalranking_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='cugjournalranking',
            name='eissn',
            field=models.CharField(default='N/A', max_length=64, verbose_name='EISSN'),
        ),
        migrations.AddField(
            model_name='cugjournalranking',
            name='issn',
            field=models.CharField(default='N/A', max_length=64, verbose_name='ISSN'),
        ),
        migrations.AddField(
            model_name='cugjournalranking',
            name='jif21',
            field=models.CharField(default='N/A', max_length=64, verbose_name='JIF21'),
        ),
        migrations.AddField(
            model_name='cugjournalranking',
            name='jif22',
            field=models.CharField(default='N/A', max_length=64, verbose_name='JIF22'),
        ),
        migrations.AddField(
            model_name='cugjournalranking',
            name='jif23',
            field=models.CharField(default='N/A', max_length=64, verbose_name='JIF23'),
        ),
        migrations.AddField(
            model_name='cugjournalranking',
            name='short_name',
            field=models.CharField(default='N/A', max_length=100, verbose_name='SHORT_NAME'),
        ),
    ]
