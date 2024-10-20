# Generated by Django 5.0.8 on 2024-10-11 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0006_issuedbook'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuedbook',
            name='fine_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='issuedbook',
            name='is_fine_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='issuedbook',
            name='return_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
