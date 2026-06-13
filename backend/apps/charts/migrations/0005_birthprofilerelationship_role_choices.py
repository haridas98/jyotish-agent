from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("charts", "0004_birthprofile_is_self_profile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="birthprofilerelationship",
            name="role",
            field=models.CharField(
                choices=[
                    ("partner", "Partner"),
                    ("father", "Father"),
                    ("mother", "Mother"),
                    ("brother", "Brother"),
                    ("sister", "Sister"),
                    ("sibling", "Sibling"),
                    ("boss", "Boss"),
                    ("subordinate", "Subordinate"),
                    ("opponent", "Opponent"),
                    ("other", "Other"),
                ],
                default="partner",
                max_length=32,
            ),
        ),
    ]
