# Generated by Django 5.0.8 on 2024-10-14 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_remove_user_userid_user_user_id_alter_user_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_id',
            field=models.CharField(editable=False, max_length=10, unique=True),
        ),
    ]
