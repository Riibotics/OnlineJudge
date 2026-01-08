# Generated migration file for adding account approval system

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_userprofile_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_approved',
            field=models.BooleanField(default=False, help_text='Whether the user account is approved by admin'),
        ),
    ]
