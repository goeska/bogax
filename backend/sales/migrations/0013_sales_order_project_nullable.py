from django.db import migrations, models
import django.db.models.deletion


PROJECT_COLUMN_SQL = """
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'sales_order'
      AND column_name = 'project_id'
  ) THEN
    ALTER TABLE public.sales_order
      ADD COLUMN project_id integer NULL;
  END IF;
END$$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0012_project_table_and_state"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(sql=PROJECT_COLUMN_SQL, reverse_sql=migrations.RunSQL.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="salesorder",
                    name="project",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sales_orders",
                        to="sales.project",
                    ),
                ),
            ],
        )
    ]
