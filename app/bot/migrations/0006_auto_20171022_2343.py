# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-22 23:43
from __future__ import unicode_literals

from django.db import migrations


def forwards_func(apps, schema_editor):
    from bot.lib.conversation import create_conversation, create_conversation_stage

    conversations = dict(
        create_project=['name_project', 'pattern_menu', 'add_pattern', 'select_pattern', 'material_menu',
                        'add_material', 'select_material', 'add_due_date', 'add_tags'],
        create_supplies=['add_tags'],
    )
    for name, stages in conversations.items():
        conversation = create_conversation(name=name)
        for stage in stages:
            create_conversation_stage(conversation_name=name, stage_name=stage)


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('bot', '0005_auto_20171019_0251'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
