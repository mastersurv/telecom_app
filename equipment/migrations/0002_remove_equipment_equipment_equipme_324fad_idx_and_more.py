# Generated by Django 5.2.1 on 2025-06-01 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0001_initial'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='equipment',
            name='equipment_equipme_324fad_idx',
        ),
        migrations.RemoveIndex(
            model_name='equipment',
            name='equipment_serial__ac559e_idx',
        ),
        migrations.AddIndex(
            model_name='equipment',
            index=models.Index(fields=['equipment_type'], name='equipment_equipme_4ceebd_idx'),
        ),
        migrations.AddIndex(
            model_name='equipment',
            index=models.Index(fields=['created_at'], name='equipment_created_d183c3_idx'),
        ),
    ]
