from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("charts", "0003_birthprofilerelationship"),
    ]

    operations = [
        migrations.AddField(
            model_name="birthprofile",
            name="is_self_profile",
            field=models.BooleanField(default=False),
        ),
    ]
