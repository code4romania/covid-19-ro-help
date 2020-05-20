# Generated by Django 3.0.4 on 2020-05-09 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobilpay', '0005_paymentorder_show_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentresponse',
            name='error_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='paymentresponse',
            name='error_message',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='paymentresponse',
            name='error_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]