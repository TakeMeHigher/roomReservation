# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-11 07:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='book',
            unique_together=set([('date', 'time', 'room')]),
        ),
    ]
