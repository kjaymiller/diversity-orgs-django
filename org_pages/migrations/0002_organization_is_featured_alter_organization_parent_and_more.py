# Generated by Django 4.0.4 on 2022-06-13 19:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("org_pages", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="organization",
            name="is_featured",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="organization",
            name="parent",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="org_pages.organization"
            ),
        ),
        migrations.DeleteModel(
            name="ParentOrganization",
        ),
    ]
