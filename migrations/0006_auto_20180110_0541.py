# Generated by Django 2.0.1 on 2018-01-10 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_user_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='status',
            new_name='activatied',
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]