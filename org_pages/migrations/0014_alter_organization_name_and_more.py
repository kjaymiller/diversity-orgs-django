# Generated by Django 4.0.4 on 2022-06-08 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org_pages', '0013_alter_parentorganization_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='parentorganization',
            name='logo',
            field=models.ImageField(blank=True, upload_to='media/logos/a760ae1d-3858-466b-876d-0f3c58293602/'),
        ),
        migrations.AlterField(
            model_name='parentorganization',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]