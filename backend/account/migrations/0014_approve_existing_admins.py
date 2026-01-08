# Generated migration file to approve existing admin accounts and users

from django.db import migrations


def approve_existing_admins(apps, schema_editor):
    """
    Approve all existing admin accounts and set is_approved to True
    """
    User = apps.get_model('account', 'User')
    # Approve all admin and super admin users
    User.objects.filter(admin_type__in=['Admin', 'Super Admin']).update(is_approved=True)


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_user_is_approved'),
    ]

    operations = [
        migrations.RunPython(approve_existing_admins),
    ]
