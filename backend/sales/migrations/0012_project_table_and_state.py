from django.db import migrations, models
import django.db.models.deletion


PROJECT_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS public.project (
  id serial PRIMARY KEY,
  code varchar(100) NOT NULL UNIQUE,
  name varchar(255) NOT NULL,
  partner_id integer NOT NULL,
  is_active boolean NOT NULL DEFAULT true,
  update_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT project_partner_id_fkey
    FOREIGN KEY (partner_id) REFERENCES public.partner(id)
    ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_project_partner_id ON public.project(partner_id);
CREATE INDEX IF NOT EXISTS idx_project_update_at ON public.project(update_at DESC);
"""


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0011_partner_is_corporate"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(sql=PROJECT_TABLE_SQL, reverse_sql=migrations.RunSQL.noop),
            ],
            state_operations=[
                migrations.CreateModel(
                    name="Project",
                    fields=[
                        ("id", models.AutoField(primary_key=True, serialize=False)),
                        ("code", models.CharField(db_index=True, max_length=100, unique=True)),
                        ("name", models.CharField(max_length=255)),
                        ("is_active", models.BooleanField(db_index=True, default=True)),
                        ("update_at", models.DateTimeField(auto_now=True)),
                        (
                            "partner",
                            models.ForeignKey(
                                db_column="partner_id",
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name="projects",
                                to="sales.partner",
                            ),
                        ),
                    ],
                    options={
                        "db_table": "project",
                        "ordering": ["-update_at", "-id"],
                    },
                )
            ],
        )
    ]

