from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("charts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="birthprofile",
            name="calculation_settings",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
