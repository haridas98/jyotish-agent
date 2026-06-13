from django.db import migrations, models


def backfill_graha_count(apps, schema_editor):
    ChartCalculation = apps.get_model("charts", "ChartCalculation")
    for calculation in ChartCalculation.objects.only("id", "result").iterator(chunk_size=500):
        result = calculation.result if isinstance(calculation.result, dict) else {}
        grahas = result.get("grahas")
        calculation.graha_count = len(grahas) if isinstance(grahas, list) else 0
        calculation.save(update_fields=["graha_count"])


class Migration(migrations.Migration):
    dependencies = [
        ("charts", "0006_birthprofilerelationship_charts_rel_user_updated_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="chartcalculation",
            name="graha_count",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.RunPython(backfill_graha_count, migrations.RunPython.noop),
    ]
