from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GeneratedAnalysisDraft",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(max_length=64)),
                ("review_status", models.CharField(default="draft", max_length=32)),
                ("source_policy", models.CharField(default="citation_first", max_length=64)),
                ("provider", models.CharField(blank=True, max_length=64)),
                ("model", models.CharField(blank=True, max_length=128)),
                ("input_snapshot", models.JSONField(blank=True, default=dict)),
                ("packet_snapshot", models.JSONField(blank=True, default=dict)),
                ("output_json", models.JSONField(blank=True, default=dict)),
                ("prompt_markdown", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddIndex(
            model_name="generatedanalysisdraft",
            index=models.Index(fields=["kind", "review_status"], name="reports_gen_kind_89d737_idx"),
        ),
        migrations.AddIndex(
            model_name="generatedanalysisdraft",
            index=models.Index(fields=["created_at"], name="reports_gen_created_8d2ced_idx"),
        ),
    ]
